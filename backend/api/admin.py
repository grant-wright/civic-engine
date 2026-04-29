import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from config import settings
from game.state import GameState, CityMap, GameStatus, PlayerType, ReportStatus
import game.store as store

_SAVES_DIR = Path(__file__).parent.parent / "saves"

router = APIRouter()


def _require_admin(token: str) -> None:
    if token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")


@router.get("/admin/state", response_model=GameState)
async def get_state(token: str = Query(...)) -> GameState:
    _require_admin(token)
    if store.game_state is None:
        raise HTTPException(status_code=503, detail="Game state not initialised")
    return store.game_state


@router.post("/admin/generate-map", response_model=CityMap)
async def generate_map(token: str = Query(...)) -> CityMap:
    _require_admin(token)
    if store.game_state is None:
        raise HTTPException(status_code=503, detail="Game state not initialised")

    from claude.map_gen import generate_city_map

    try:
        city_map = await generate_city_map()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Map generation failed: {exc}") from exc

    # 1. Replace the map
    store.game_state.city_map = city_map

    # 2. Update the authoritative faction list at the GameState root
    if city_map.factions:
        store.game_state.factions = city_map.factions

    # 3. Update each player's councillor to the first generated councillor matching their role
    for player in store.game_state.players.values():
        matching = next(
            (c for c in city_map.councillors if c.role == player.role),
            None,
        )
        if matching:
            player.councillor = matching

    return city_map


@router.post("/admin/save-map")
async def save_map(token: str = Query(...), slot: str = Query(default="default")):
    _require_admin(token)
    if store.game_state is None:
        raise HTTPException(status_code=503, detail="Game state not initialised")

    _SAVES_DIR.mkdir(exist_ok=True)
    save_path = _SAVES_DIR / f"map_{slot}.json"
    city_map = store.game_state.city_map
    save_path.write_text(city_map.model_dump_json())

    return {
        "saved": str(save_path),
        "slot": slot,
        "nodes": len(city_map.nodes),
        "canal_segments": len(city_map.canal_segments),
        "factions": len(city_map.factions),
        "councillors": len(city_map.councillors),
    }


@router.post("/admin/load-map", response_model=CityMap)
async def load_map(token: str = Query(...), slot: str = Query(default="default")):
    _require_admin(token)
    if store.game_state is None:
        raise HTTPException(status_code=503, detail="Game state not initialised")

    save_path = _SAVES_DIR / f"map_{slot}.json"
    if not save_path.exists():
        raise HTTPException(status_code=404, detail=f"No saved map in slot '{slot}'")

    city_map = CityMap.model_validate_json(save_path.read_text())

    store.game_state.city_map = city_map
    if city_map.factions:
        store.game_state.factions = city_map.factions
    for player in store.game_state.players.values():
        matching = next((c for c in city_map.councillors if c.role == player.role), None)
        if matching:
            player.councillor = matching

    return city_map


@router.post("/admin/seed-scenario")
async def seed_scenario(token: str = Query(...), scenario: str = Query(default="fresh_game")):
    _require_admin(token)
    from game.scenarios import SCENARIOS

    if scenario not in SCENARIOS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown scenario '{scenario}'. Available: {list(SCENARIOS)}",
        )

    gs = SCENARIOS[scenario]()
    store.game_state = gs
    await store.broadcast_game_state()

    if gs.status == GameStatus.IN_GAME:
        from game.reports import schedule_reports
        from claude.ai_player import make_ai_decision

        async def _seed_turn_content():
            await schedule_reports(gs)
            await store.broadcast_game_state()
            for player in gs.players.values():
                if player.player_type != PlayerType.AI:
                    continue
                for report in gs.pending_reports.get(player.player_id, []):
                    if report.status == ReportStatus.PENDING:
                        store.fire_task(
                            make_ai_decision(player, report, gs, store.broadcast_game_state)
                        )

        store.fire_task(_seed_turn_content())

    return {
        "scenario": scenario,
        "turn": gs.turn,
        "cycle": gs.cycle,
        "status": gs.status,
    }


@router.post("/admin/start-game")
async def start_game(token: str = Query(...)):
    """
    Transition the current game state to IN_GAME and generate the first turn's reports.
    Use after /admin/seed-scenario (which seeds LOBBY) to actually begin play.
    """
    _require_admin(token)
    if store.game_state is None:
        raise HTTPException(status_code=503, detail="Game state not initialised")

    gs = store.game_state
    if gs.status == GameStatus.IN_GAME:
        raise HTTPException(status_code=400, detail="Game is already IN_GAME")

    gs.status = GameStatus.IN_GAME
    await store.broadcast_game_state()

    from game.reports import schedule_reports
    from claude.ai_player import make_ai_decision

    async def _start():
        await schedule_reports(gs)
        await store.broadcast_game_state()
        for player in gs.players.values():
            if player.player_type != PlayerType.AI:
                continue
            for report in gs.pending_reports.get(player.player_id, []):
                if report.status == ReportStatus.PENDING:
                    store.fire_task(
                        make_ai_decision(player, report, gs, store.broadcast_game_state)
                    )

    store.fire_task(_start())

    return {"status": gs.status, "turn": gs.turn, "cycle": gs.cycle}


@router.post("/admin/set-field")
async def set_field(
    token: str = Query(...),
    field: str = Query(...),
    value: str = Query(...),
):
    _require_admin(token)
    if store.game_state is None:
        raise HTTPException(status_code=503, detail="Game state not initialised")

    gs = store.game_state
    parts = field.split(".", 1)

    if len(parts) == 2:
        parent = getattr(gs, parts[0], None)
        if parent is None:
            raise HTTPException(status_code=400, detail=f"No attribute '{parts[0]}' on game state")
        attr_name = parts[1]
        target = parent
    else:
        attr_name = parts[0]
        target = gs

    if not hasattr(target, attr_name):
        raise HTTPException(status_code=400, detail=f"Field '{field}' not found")

    old_value = getattr(target, attr_name)
    try:
        if isinstance(old_value, float):
            new_value = float(value)
        elif isinstance(old_value, int):
            new_value = int(value)
        else:
            new_value = value
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Cannot cast '{value}' to {type(old_value).__name__}")

    setattr(target, attr_name, new_value)
    await store.broadcast_game_state()

    return {"field": field, "old": old_value, "new": new_value}


@router.post("/admin/advance-turn")
async def advance_turn_endpoint(token: str = Query(...)):
    _require_admin(token)
    if store.game_state is None:
        raise HTTPException(status_code=503, detail="Game state not initialised")

    from game.engine import advance_turn
    from game.reports import schedule_reports
    from game.factions import build_turn_summary, run_faction_reactions
    from claude.ai_player import make_ai_decision

    gs = store.game_state
    log_len_before = len(gs.event_log)
    advance_turn(gs)
    recent_events = gs.event_log[log_len_before:]
    await store.broadcast_game_state()

    turn_summary = build_turn_summary(gs, recent_events)
    store.fire_task(run_faction_reactions(gs, turn_summary))

    if gs.status == GameStatus.IN_GAME:
        await schedule_reports(gs)
        await store.broadcast_game_state()
        for player in gs.players.values():
            if player.player_type != PlayerType.AI:
                continue
            for report in gs.pending_reports.get(player.player_id, []):
                if report.status == ReportStatus.PENDING:
                    store.fire_task(
                        make_ai_decision(player, report, gs, store.broadcast_game_state)
                    )

    return {
        "turn": gs.turn,
        "cycle": gs.cycle,
        "status": gs.status,
        "polling": round(gs.metrics.election_polling, 1),
    }


@router.get("/admin/usage")
async def get_usage(token: str = Query(...)):
    _require_admin(token)
    from claude.client import usage_log

    total_cost = sum(r.cost_usd for r in usage_log)
    by_type: dict = {}
    for r in usage_log:
        bt = by_type.setdefault(
            r.call_type,
            {"calls": 0, "cost_usd": 0.0, "cache_read_tokens": 0, "input_tokens": 0},
        )
        bt["calls"] += 1
        bt["cost_usd"] += r.cost_usd
        bt["cache_read_tokens"] += r.cache_read_tokens
        bt["input_tokens"] += r.input_tokens + r.cache_write_tokens

    total_input = sum(r.input_tokens + r.cache_write_tokens for r in usage_log)
    total_cache_read = sum(r.cache_read_tokens for r in usage_log)
    cache_hit_rate = total_cache_read / max(1, total_input + total_cache_read)

    return {
        "total_cost_usd": round(total_cost, 6),
        "total_calls": len(usage_log),
        "cache_hit_rate": round(cache_hit_rate, 3),
        "by_type": by_type,
        "records": [
            {
                "call_type": r.call_type,
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "cache_write_tokens": r.cache_write_tokens,
                "cache_read_tokens": r.cache_read_tokens,
                "cost_usd": round(r.cost_usd, 6),
                "turn": r.turn,
                "cycle": r.cycle,
            }
            for r in usage_log
        ],
    }


@router.get("/admin/reports")
async def get_reports(token: str = Query(...), status: str = Query(default="all")):
    """
    Returns all reports grouped by player, with decision resolved to a human-readable label.
    ?status=all | pending | decided | deferred | escalated
    """
    _require_admin(token)
    if store.game_state is None:
        raise HTTPException(status_code=503, detail="Game state not initialised")

    gs = store.game_state
    result = {}
    for player_id, reports in gs.pending_reports.items():
        player = gs.players.get(player_id)
        player_name = player.councillor.name if player else player_id
        filtered = reports if status == "all" else [r for r in reports if r.status == status]
        result[player_id] = {
            "player_name": player_name,
            "reports": [
                {
                    "report_id": r.report_id,
                    "title": r.title,
                    "domain": r.domain,
                    "status": r.status,
                    "urgent": r.urgent,
                    "turn_received": r.turn_received,
                    "turn_deadline": r.turn_deadline,
                    "defer_count": r.defer_count,
                    "decision_option_id": r.decision,
                    "decision_label": next(
                        (o.label for o in r.options if o.option_id == r.decision), None
                    ) if r.decision else None,
                    "options": [
                        {"option_id": o.option_id, "label": o.label, "risk_level": o.risk_level}
                        for o in r.options
                    ],
                }
                for r in filtered
            ],
        }

    return result


@router.get("/admin/dev-log")
async def get_dev_log(token: str = Query(...), limit: int = Query(default=50)):
    _require_admin(token)
    entries = store.dev_log[-limit:] if limit else store.dev_log
    return {
        "total": len(store.dev_log),
        "returned": len(entries),
        "entries": entries,
    }


@router.delete("/admin/dev-log")
async def clear_dev_log(token: str = Query(...)):
    _require_admin(token)
    count = len(store.dev_log)
    store.dev_log.clear()
    return {"cleared": count}
