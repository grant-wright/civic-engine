import uuid

from game.state import (
    GameState, GameStatus, WinState, CanalTier,
    GameEvent, GameEventType,
)
from game.rules import Election, Income, Turn


def _log_event(gs: GameState, event_type: GameEventType, description: str) -> None:
    gs.event_log.append(GameEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        turn=gs.turn,
        cycle=gs.cycle,
        description=description,
    ))


def apply_cycle_income(metrics) -> None:
    income = int(Income.base * metrics.economy_index / 100)
    metrics.budget.finance        += income // Income.finance_divisor
    metrics.budget.infrastructure += income // Income.infrastructure_divisor
    metrics.budget.transport      += income // Income.transport_divisor
    metrics.cycle_income = income


def trigger_game_over(gs: GameState, reason: str) -> None:
    from game.map import check_canal_connectivity
    tier = check_canal_connectivity(gs.city_map)
    gs.win_state = WinState(
        outcome="game_over",
        canal_tier=tier,
        cycles_survived=gs.metrics.cycles_survived,
        epitaph=(
            f"Council dissolved after {gs.metrics.cycles_survived} cycle(s). "
            f"Reason: {reason}."
        ),
    )
    gs.status = GameStatus.GAME_OVER
    _log_event(gs, GameEventType.GAME_OVER, gs.win_state.epitaph)


def trigger_win(gs: GameState) -> None:
    from game.map import check_canal_connectivity
    tier = check_canal_connectivity(gs.city_map)
    heritage = tier == CanalTier.GOLD and gs.metrics.aesthetic_index >= Election.heritage_aesthetic_threshold
    outcome = {
        CanalTier.GOLD:   "celebration",
        CanalTier.SILVER: "strong_win",
        CanalTier.BRONZE: "modest_win",
        CanalTier.NONE:   "survived",
    }[tier]
    if heritage:
        outcome = "heritage_commendation"
    gs.win_state = WinState(
        outcome=outcome,
        canal_tier=tier,
        heritage_commendation=heritage,
        cycles_survived=gs.metrics.cycles_survived,
        epitaph=_win_epitaph(outcome, gs.metrics.cycles_survived),
    )
    gs.status = GameStatus.GAME_OVER
    _log_event(gs, GameEventType.GAME_OVER, gs.win_state.epitaph)


def _win_epitaph(outcome: str, cycles: int) -> str:
    return {
        "heritage_commendation": (
            f"A golden age — {cycles} cycle(s) of prosperity and beauty."
        ),
        "celebration": (
            f"The canal network transformed the city after {cycles} cycle(s)."
        ),
        "strong_win": (
            f"Silver-tier connectivity achieved across {cycles} cycle(s)."
        ),
        "modest_win": (
            f"A functional canal network delivered in {cycles} cycle(s)."
        ),
        "survived": (
            f"The council survived {cycles} cycle(s) without completing the canal."
        ),
    }.get(outcome, f"Game ended after {cycles} cycle(s).")


def check_cycle_end(gs: GameState) -> bool:
    if gs.turn < Turn.turns_per_cycle:
        return False

    if gs.metrics.election_polling < Election.loss_threshold:
        trigger_game_over(gs, reason="election_loss")
        return True

    gs.metrics.cycles_survived += 1

    if gs.cycle >= gs.game_length:
        trigger_win(gs)
        return True

    _log_event(
        gs,
        GameEventType.ELECTION_SURVIVED,
        (
            f"Cycle {gs.cycle} election survived with "
            f"{gs.metrics.election_polling:.0f}% polling. "
            f"Entering cycle {gs.cycle + 1}."
        ),
    )
    gs.cycle += 1
    gs.turn = 1
    apply_cycle_income(gs.metrics)
    return True
