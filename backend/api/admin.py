from fastapi import APIRouter, HTTPException, Query
from config import settings
from game.state import GameState, CityMap
import game.store as store

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
