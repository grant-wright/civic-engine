from fastapi import APIRouter
import game.store as store

router = APIRouter()


@router.get("/health")
async def health():
    turn = store.game_state.turn if store.game_state else 0
    return {"status": "ok", "turn": turn}
