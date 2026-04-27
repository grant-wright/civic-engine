from fastapi import FastAPI
from config import settings

app = FastAPI(title="Civic Engine", version="0.1.0")


@app.get("/")
async def root():
    return {"message": "Civic Engine API is running"}
