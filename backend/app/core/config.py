from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://showdown:showdown@localhost:5432/showdown"
    redis_url: str = "redis://localhost:6379/0"
    steam_api_key: str = ""
    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        extra="ignore"
    )

@lru_cache
def get_settings():
    return Settings()