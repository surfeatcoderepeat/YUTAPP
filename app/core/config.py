# app/core/config.py
from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    telegram_bot_token: str
    openai_api_key: str
    database_url: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()