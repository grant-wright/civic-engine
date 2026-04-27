from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.state import GameState

# Single mutable reference to the active game state.
# main.py initialises this; all other modules read/write through it.
game_state: GameState | None = None
