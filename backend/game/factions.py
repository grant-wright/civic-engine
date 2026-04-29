import asyncio
import uuid
from game.state import Faction, Metrics, GameState, GameEvent, GameEventType
from game.rules import Happiness, FactionAlertThreshold


def recompute_citizen_happiness(factions: list[Faction], metrics: Metrics) -> float:
    total_weight = sum(f.population_weight for f in factions)
    if total_weight == 0:
        return Happiness.default
    faction_component = (
        sum(f.happiness * f.population_weight for f in factions) / total_weight
    )
    return (
        (faction_component * Happiness.faction_weight)
        + (metrics.aesthetic_index * Happiness.aesthetic_weight)
    )


def faction_affected(faction: Faction, turn_summary: str) -> bool:
    """True if any of the faction's political_sensitivities appear in the turn summary."""
    summary_lower = turn_summary.lower()
    return any(s.lower() in summary_lower for s in faction.political_sensitivities)


def build_turn_summary(gs: GameState, recent_events: list[GameEvent]) -> str:
    """
    Build a plain-text summary of what happened this turn for faction reactions.
    Appends keyword tags so faction_affected() routes Claude calls correctly
    even when event descriptions don't literally contain sensitivity strings.
    FLAG FOR /ITERATE: store these summaries in gs.turn_chronicles for end-game review.
    """
    event_lines = [ev.description for ev in recent_events] or ["Routine civic business."]

    m = gs.metrics
    tags = ["civic_progress"]  # neutral tag — the game covers all civic governance, not just canals

    if any(ev.event_type in (GameEventType.WAYPOINT_COMPLETE, GameEventType.SEGMENT_COMPLETE)
           for ev in recent_events):
        tags += ["canal_progress", "worker_safety", "workers_rights"]
    else:
        tags.append("canal_progress")  # canal is always on the agenda

    if m.road_freight_pct > FactionAlertThreshold.road_freight_high:
        tags += ["freight_road", "fiscal_prudence"]

    if m.horse_pollution > FactionAlertThreshold.horse_pollution_notable:
        tags.append("horse_pollution")

    if m.aesthetic_index > FactionAlertThreshold.aesthetic_notable:
        tags += ["aesthetic_index", "heritage"]

    if m.election_polling < FactionAlertThreshold.polling_concerning:
        tags += ["election_polling", "economic_equity"]

    return "\n".join(event_lines) + f"\n\nActive conditions: {', '.join(tags)}"


async def run_faction_reactions(gs: GameState, turn_summary: str) -> None:
    """
    Generate Claude reactions for factions whose sensitivities overlap with
    this turn's events, apply happiness deltas, and log FACTION_SWING events.
    """
    import game.store as store
    from claude.citizens import generate_faction_reaction

    relevant = [f for f in gs.factions if faction_affected(f, turn_summary)]
    if not relevant:
        return

    tasks = [generate_faction_reaction(f, turn_summary, gs) for f in relevant]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    changed = False
    for faction, result in zip(relevant, results):
        if isinstance(result, Exception) or result is None:
            continue
        faction.happiness = max(0.0, min(100.0, faction.happiness + result.happiness_delta))
        gs.event_log.append(GameEvent(
            event_id=str(uuid.uuid4()),
            event_type=GameEventType.FACTION_SWING,
            turn=gs.turn,
            cycle=gs.cycle,
            description=f"{faction.name}: {result.reaction_text}",
            data={
                "faction_id": faction.faction_id,
                "delta": result.happiness_delta,
                "severity": result.severity,
            },
        ))
        changed = True

    if changed:
        await store.broadcast_game_state()
