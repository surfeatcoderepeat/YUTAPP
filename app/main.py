from fastapi import FastAPI
import asyncio
from app.interfaces.telegram_bot.telegram_bot import start_bot

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bot de Telegram activo"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())