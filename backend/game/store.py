from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game.state import GameState

# Single mutable reference to the active game state.
# main.py initialises this; all other modules read/write through it.
game_state: GameState | None = None

# socket_id → {client_type, player_id, role, session_id}
connected_clients: dict[str, dict[str, Any]] = {}

# Assigned by main.py after creating the socketio.AsyncServer instance.
# Other modules call broadcast_game_state() without importing sio directly.
_sio: Any = None


async def broadcast_game_state() -> None:
    """Serialise current game state and emit to all connected clients."""
    if _sio is None or game_state is None:
        return
    payload = game_state.model_dump(mode="json")
    await _sio.emit("game_state_update", payload)
