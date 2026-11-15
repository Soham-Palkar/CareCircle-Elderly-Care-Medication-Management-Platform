"""Application settings via Pydantic BaseSettings v2."""

from __future__ import annotations

from functools import lru_cache
import os
from typing import List, Optional
from typing_extensions import Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Runtime environment
    env: str = Field(default="dev", alias="ENV")
    app_env: str = Field(default="dev", alias="APP_ENV")

    # Database (Accepts production PostgreSQL connection string)
    database_url: str = Field(
        default="postgresql+asyncpg://carecircle:carecircle@db:5432/carecircle",
        alias="DATABASE_URL",
    )

    # JWT / Secrets
    jwt_secret: str = Field(default="change-me-to-64-random-chars", alias="JWT_SECRET")
    action_token_secret: str = Field(default="change-me-to-64-random-chars", alias="ACTION_TOKEN_SECRET")
    access_token_minutes: int = 30
    refresh_token_days: int = 7

    # Cookies
    cookie_secure: Optional[bool] = None
    cookie_samesite: str = Field(default="lax", alias="COOKIE_SAMESITE")

    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000"], alias="CORS_ORIGINS")

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

    @property
    def is_production(self) -> bool:
        env_val = (self.app_env or self.env or os.environ.get("APP_ENV") or os.environ.get("ENV") or "dev").lower()
        return env_val in ("prod", "production")

    @property
    def effective_cookie_secure(self) -> bool:
        if self.cookie_secure is not None:
            return self.cookie_secure
        return self.is_production

    @model_validator(mode="after")
    def validate_production_configuration(self) -> Self:
        """Enforce strict secret and database requirements in production."""
        if self.is_production:
            if not self.jwt_secret or "change-me" in self.jwt_secret or len(self.jwt_secret) < 32:
                raise ValueError(
                    "Insecure configuration: In production (APP_ENV=production), JWT_SECRET must be "
                    "set via environment variable to a secure random string of at least 32 characters."
                )
            if not self.action_token_secret or "change-me" in self.action_token_secret or len(self.action_token_secret) < 32:
                raise ValueError(
                    "Insecure configuration: In production (APP_ENV=production), ACTION_TOKEN_SECRET must be "
                    "set via environment variable to a secure random string of at least 32 characters."
                )
            if "@db:5432" in self.database_url:
                raise ValueError(
                    "Insecure configuration: In production, DATABASE_URL must not use the local docker-compose default."
                )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
