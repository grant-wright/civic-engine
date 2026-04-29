from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

log = logging.getLogger(__name__)

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


# Dev log — persists across game resets; collects Claude output errors for tuning.
# Entries: {timestamp, category, message, turn, cycle, detail}
dev_log: list[dict] = []


def log_dev(category: str, message: str, turn: int = 0, cycle: int = 0, **detail) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "message": message,
        "turn": turn,
        "cycle": cycle,
        "detail": detail,
    }
    dev_log.append(entry)
    log.warning("[DEV %s] %s %s", category, message, detail or "")


# Strong references to background tasks — prevents GC mid-execution.
# Use fire_task() instead of asyncio.create_task() for fire-and-forget work.
_background_tasks: set[asyncio.Task] = set()


def fire_task(coro) -> asyncio.Task:
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


async def broadcast_game_state() -> None:
    """Serialise current game state and emit to all connected clients."""
    if _sio is None or game_state is None:
        return
    payload = game_state.model_dump(mode="json")
    await _sio.emit("game_state_update", payload)
