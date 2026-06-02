from functools import lru_cache
from typing import Annotated

from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from trillia_monitor.domain.value_objects import CurrencyPair


def _parse_pairs(raw: str | list[str]) -> list[CurrencyPair]:
    if isinstance(raw, list):
        return [p if isinstance(p, CurrencyPair) else CurrencyPair.parse(p) for p in raw]
    return [CurrencyPair.parse(item.strip()) for item in raw.split(",") if item.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="TRILLIA_", extra="ignore")

    database_url: str = "postgresql+asyncpg://trillia:trillia@db:5432/trillia"
    awesomeapi_base_url: str = "https://economia.awesomeapi.com.br"
    provider_timeout_seconds: float = 5.0
    provider_retry_attempts: int = 4

    polling_interval_seconds: int = Field(default=60, ge=5, le=3600)
    monitored_pairs: Annotated[list[CurrencyPair], NoDecode, BeforeValidator(_parse_pairs)] = Field(
        default_factory=lambda: [CurrencyPair("USD", "BRL")]
    )

    cors_allow_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    log_level: str = "INFO"
    log_json: bool = True
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
