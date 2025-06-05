from fastapi import FastAPI
import asyncio
from app.interfaces.telegram_bot.telegram_bot import start_bot

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bot de Telegram activo"}

from fastapi import FastAPI, Lifespan

async def lifespan(app: FastAPI):
    asyncio.create_task(start_bot())
    yield

app = FastAPI(lifespan=lifespan)