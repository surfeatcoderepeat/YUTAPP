import asyncio
from app.interfaces.telegram_bot.telegram_bot import start_bot

if __name__ == "__main__":
    print("🚀 Iniciando YUTAPP Bot...")
    asyncio.run(start_bot())