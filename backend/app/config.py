"""Application settings, read from environment variables (or backend/.env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Recovery AI"
    app_version: str = "0.1.0"
    app_env: str = "development"
    database_url: str = "sqlite:///./recovery_ai.db"
    cors_origins: str = "http://localhost:5173"
    data_seed: int = 42
    scenario_date: str = "2026-03-10"
    scenario_clock: str = "09:40"
    llm_api_key: str = ""  # unused until a later milestone

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
