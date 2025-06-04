# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.telegram_bot import start_bot
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando YUTAPP con bot y servidor...")
    asyncio.create_task(start_bot())
    yield
    print("🛑 Terminando YUTAPP...")  # (opcional)

app = FastAPI(title="YUTAPP", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "YUTAPP API corriendo 🤘"}