"""Application settings via Pydantic BaseSettings v2."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://carecircle:carecircle@db:5432/carecircle"

    # JWT
    jwt_secret: str = "change-me-to-64-random-chars"
    action_token_secret: str = "change-me-to-64-random-chars"
    access_token_minutes: int = 30
    refresh_token_days: int = 7

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        """Allow comma-separated string in .env."""
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # Email (SMTP)
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@carecircle.local"

    # Telegram
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""

    # Vision / OCR
    vision_provider: str = "fake"
    vision_api_key: str = ""

    # Intent classifier
    intent_classifier_path: str = ""

    # Worker / scheduler
    tick_seconds: int = 30
    reminder_lead_minutes: int = 30
    default_grace_minutes: int = 60

    # Runtime environment
    env: str = "dev"

    @property
    def is_production(self) -> bool:
        return self.env == "prod"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
