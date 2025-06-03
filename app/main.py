# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.telegram_bot import start_bot
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando ShootUp con bot y servidor...")
    asyncio.create_task(start_bot())
    yield
    print("🛑 Terminando ShootUp...")  # (opcional)

app = FastAPI(title="ShootUp", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "ShootUp API corriendo 🤘"}