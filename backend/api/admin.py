from fastapi import APIRouter, HTTPException, Query
from config import settings
from game.state import GameState
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
