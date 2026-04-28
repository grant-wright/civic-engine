from pathlib import Path

from fastapi import FastAPI
from config import settings
import game.store as store
from game.scenarios import scenario_fresh_game
from api.admin import router as admin_router

app = FastAPI(title="Civic Engine", version="0.1.0")

# Initialise game state at startup
store.game_state = scenario_fresh_game()

# Auto-load saved default map if one exists — skips regeneration on restart
_default_map_path = Path(__file__).parent / "saves" / "map_default.json"
if _default_map_path.exists():
    from game.state import CityMap
    _city_map = CityMap.model_validate_json(_default_map_path.read_text())
    store.game_state.city_map = _city_map
    if _city_map.factions:
        store.game_state.factions = _city_map.factions
    for _player in store.game_state.players.values():
        _match = next((c for c in _city_map.councillors if c.role == _player.role), None)
        if _match:
            _player.councillor = _match

# Routers
app.include_router(admin_router)


@app.get("/")
async def root():
    return {"message": "Civic Engine API is running"}
