"""
game/reports.py — Report scheduling logic.
Determines per-domain triggers based on current metrics, then calls claude/events.py.
"""
import asyncio
from game.state import GameState, GameStatus
from game.rules import HorsePollution, Election

_ROAD_RAGE_CRISIS = 70.0  # FLAG FOR /ITERATE: move to rules.py


def _trigger(domain: str, gs: GameState) -> str:
    m = gs.metrics
    if domain == "finance":
        if m.election_polling < Election.loss_threshold + 15:
            return (
                f"Election polling at {m.election_polling:.0f}% — "
                f"the council's majority is fragile."
            )
        return f"Economy index at {m.economy_index:.0f}%. Cycle income forecast due."

    if domain == "infrastructure":
        if m.road_rage_index > _ROAD_RAGE_CRISIS:
            return (
                f"Road Rage crisis — index at {m.road_rage_index:.0f}. "
                f"Urgent infrastructure response needed."
            )
        return f"Construction active. Road Rage at {m.road_rage_index:.0f}."

    if domain == "transport":
        if m.horse_pollution > HorsePollution.crisis_threshold:
            return (
                f"Horse pollution at {m.horse_pollution:.0f} — "
                f"public health emergency imminent."
            )
        return (
            f"Canal freight at {m.canal_freight_pct:.0f}%. "
            f"Railway influence at {gs.railway_party.influence:.0f}%."
        )

    return "Routine civic business."


async def schedule_reports(gs: GameState) -> None:
    if gs.status != GameStatus.IN_GAME:
        return

    from claude.events import generate_report

    tasks = [
        generate_report(
            player.role.value,
            gs,
            _trigger(player.role.value, gs),
            player_id,
        )
        for player_id, player in gs.players.items()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception) or result is None:
            continue
        pid = result.addressed_to
        gs.pending_reports.setdefault(pid, []).append(result)
