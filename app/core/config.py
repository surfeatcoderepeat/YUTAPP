# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    telegram_bot_token: str = ""
    openai_api_key: str = ""
    database_url: str = "postgresql://postgres:wYKXmVUXyDbMGMrBjFEgpKKceWaDFsFk@shuttle.proxy.rlwy.net:53773/railway"

    class Config:
        env_file = ".env"
        extra = "ignore"

print("DATABASE_URL:", Settings().database_url)

@lru_cache()
def get_settings():
    return Settings()