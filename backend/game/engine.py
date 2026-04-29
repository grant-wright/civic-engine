import uuid

import game.store as store
from game.state import (
    GameState, Effect, EffectType, GameEvent, GameEventType,
    SegmentStatus, WaypointStatus, CanalTier, RailwayPhase,
)
from game.rules import HorsePollution, Economy, Election, Railway, RoadRage
from game.elections import check_cycle_end
from game.map import check_canal_connectivity, recompute_canal_efficiency
from game.factions import recompute_citizen_happiness


def _log_event(gs: GameState, event_type: GameEventType, description: str) -> None:
    gs.event_log.append(GameEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        turn=gs.turn,
        cycle=gs.cycle,
        description=description,
    ))


def _apply_single_effect(gs: GameState, effect: Effect) -> None:
    m = gs.metrics
    match effect.effect_type:
        case EffectType.METRIC_DELTA:
            current = getattr(m, effect.target_id, 0.0)
            setattr(m, effect.target_id,
                    max(0.0, min(100.0, current + float(effect.value))))
        case EffectType.BUDGET_DELTA:
            current = getattr(m.budget, effect.target_id, 0)
            setattr(m.budget, effect.target_id, current + int(effect.value))
        case EffectType.FACTION_MOOD:
            try:
                f = gs.get_faction(effect.target_id)
                f.happiness = max(0.0, min(100.0, f.happiness + float(effect.value)))
            except KeyError:
                valid = [f.faction_id for f in gs.factions]
                store.log_dev(
                    "effect_error",
                    f"Unknown faction_id '{effect.target_id}' in FACTION_MOOD effect — skipped",
                    turn=gs.turn,
                    cycle=gs.cycle,
                    valid_faction_ids=valid,
                    effect_description=effect.description,
                )
        case EffectType.RAILWAY_INFLUENCE:
            gs.railway_party.influence = max(
                0.0, min(100.0, gs.railway_party.influence + float(effect.value))
            )
        case EffectType.CANALPARTY_INFLUENCE:
            gs.canal_party.influence = max(
                0.0, min(100.0, gs.canal_party.influence + float(effect.value))
            )
        case EffectType.AESTHETIC_DELTA:
            m.aesthetic_index = max(
                0.0, min(100.0, m.aesthetic_index + float(effect.value))
            )
        case EffectType.ECONOMY_DELTA:
            m.economy_index = max(
                0.0, min(100.0, m.economy_index + float(effect.value))
            )
        case EffectType.INCOME_DELTA:
            delta = int(effect.value)
            m.cycle_income += delta
            m.budget.finance += delta
        case _:
            pass  # CONSTRUCTION_START/ADVANCE, REPORT_GENERATE, COUNCIL_EXTENSION handled elsewhere


def apply_pending_effects(gs: GameState) -> None:
    due = [(t, e) for t, e in gs.pending_effects if t <= gs.turn]
    gs.pending_effects = [(t, e) for t, e in gs.pending_effects if t > gs.turn]
    for _, effect in due:
        _apply_single_effect(gs, effect)


def _check_milestone(
    gs: GameState, tier_before: CanalTier, tier_after: CanalTier
) -> None:
    rank = {CanalTier.NONE: 0, CanalTier.BRONZE: 1, CanalTier.SILVER: 2, CanalTier.GOLD: 3}
    if rank[tier_after] <= rank[tier_before]:
        return
    milestone_type = {
        CanalTier.BRONZE: GameEventType.MILESTONE_BRONZE,
        CanalTier.SILVER: GameEventType.MILESTONE_SILVER,
        CanalTier.GOLD:   GameEventType.MILESTONE_GOLD,
    }[tier_after]
    _log_event(gs, milestone_type, f"Canal network reached {tier_after.value} tier!")


def advance_construction(gs: GameState) -> None:
    tier_before = check_canal_connectivity(gs.city_map)

    for seg in gs.city_map.canal_segments.values():
        if seg.status == SegmentStatus.COMPLETE:
            continue
        for wp in seg.waypoints:
            if wp.status != WaypointStatus.UNDER_CONSTRUCTION:
                continue
            wp.turns_spent += 1
            if wp.turns_spent >= wp.construction_turns_required:
                wp.status = WaypointStatus.COMPLETE
                _log_event(gs, GameEventType.WAYPOINT_COMPLETE,
                           f"{wp.name} complete on {seg.from_node}→{seg.to_node}.")
                # Auto-chain: start the next unstarted waypoint in this segment
                next_wp = next(
                    (w for w in seg.waypoints if w.status == WaypointStatus.UNSTARTED),
                    None,
                )
                if next_wp:
                    next_wp.status = WaypointStatus.UNDER_CONSTRUCTION

        if seg.status == SegmentStatus.COMPLETE:
            _log_event(gs, GameEventType.SEGMENT_COMPLETE,
                       f"Canal segment {seg.from_node}→{seg.to_node} fully complete.")

    tier_after = check_canal_connectivity(gs.city_map)
    _check_milestone(gs, tier_before, tier_after)


def update_metrics(gs: GameState) -> None:
    m = gs.metrics

    # a. Canal efficiency (derives from completed network topology)
    recompute_canal_efficiency(gs.city_map, m)

    # b. Horse pollution: rises when canal underperforms, falls otherwise
    if m.canal_efficiency_index < HorsePollution.low_efficiency_threshold:
        m.horse_pollution = min(100.0, m.horse_pollution + HorsePollution.rise_per_turn)
    else:
        m.horse_pollution = max(0.0, m.horse_pollution - HorsePollution.fall_per_turn)

    # c. Road rage: blended target from freight load and pollution, nudged ≤5 pts/turn
    road_rage_target = (
        m.road_freight_pct * RoadRage.freight_weight
        + m.horse_pollution * RoadRage.pollution_weight
    )
    step = max(-RoadRage.max_step_per_turn,
               min(RoadRage.max_step_per_turn, road_rage_target - m.road_rage_index))
    m.road_rage_index = max(0.0, min(100.0, m.road_rage_index + step))

    # d. Economy: freight-mix target with inertia
    economy_target = (
        m.canal_freight_pct * Economy.canal_freight_mult
        + m.rail_freight_pct  * Economy.rail_freight_mult
        + m.road_freight_pct  * Economy.road_freight_mult
    )
    m.economy_index += Economy.inertia * (economy_target - m.economy_index)
    m.economy_index = max(0.0, min(100.0, m.economy_index))

    # e. Citizen happiness: faction-weighted average + aesthetic
    m.citizen_happiness = recompute_citizen_happiness(gs.factions, m)

    # f. Election polling lags happiness
    m.election_polling += Election.polling_lag * (m.citizen_happiness - m.election_polling)
    m.election_polling = max(0.0, min(100.0, m.election_polling))

    # g. Railway influence grows each turn; activates when threshold crossed
    rp = gs.railway_party
    rp.influence = min(100.0, rp.influence + Railway.growth_per_turn)
    if rp.phase == RailwayPhase.LOBBY and rp.influence >= rp.activation_threshold:
        rp.phase = RailwayPhase.ACTIVE
        _log_event(gs, GameEventType.RAILWAY_ACTIVATED,
                   f"Railway party activated at {rp.influence:.0f}% influence.")

    # TODO: canal_mania check — trigger when canal_party.influence exceeds threshold (step 10+)


def advance_turn(gs: GameState) -> None:
    apply_pending_effects(gs)
    advance_construction(gs)
    update_metrics(gs)
    if check_cycle_end(gs):
        return
    gs.turn += 1
    gs.current_turn_extended = False
