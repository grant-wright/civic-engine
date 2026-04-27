from fastapi import FastAPI
from config import settings
import game.store as store
from game.scenarios import scenario_fresh_game
from api.admin import router as admin_router

app = FastAPI(title="Civic Engine", version="0.1.0")

# Initialise game state at startup
store.game_state = scenario_fresh_game()

# Routers
app.include_router(admin_router)


@app.get("/")
async def root():
    return {"message": "Civic Engine API is running"}
