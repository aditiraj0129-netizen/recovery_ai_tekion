"""Application settings, read from environment variables (or backend/.env)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = REPO_ROOT / "data" / "generated" / "dealership_dataset.json"


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
    auto_seed: bool = True  # load the dataset on startup if the database is empty
    dataset_path: str = ""  # empty = data/generated/dealership_dataset.json
    llm_api_key: str = ""  # unused until a later milestone

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def resolved_dataset_path(self) -> Path:
        return Path(self.dataset_path) if self.dataset_path else DEFAULT_DATASET_PATH


@lru_cache
def get_settings() -> Settings:
    return Settings()
