"""Unit tests verifying production configuration and safety guards."""

import pytest
from app.core.config import Settings


def test_production_rejects_default_jwt_secret():
    with pytest.raises(ValueError, match="JWT_SECRET must be set"):
        Settings(
            APP_ENV="production",
            JWT_SECRET="change-me-to-64-random-chars",
            ACTION_TOKEN_SECRET="a" * 32,
            DATABASE_URL="postgresql+asyncpg://user:pass@prod-host:5432/carecircle",
        )


def test_production_rejects_short_jwt_secret():
    with pytest.raises(ValueError, match="at least 32 characters"):
        Settings(
            APP_ENV="production",
            JWT_SECRET="short-secret-12345",
            ACTION_TOKEN_SECRET="a" * 32,
            DATABASE_URL="postgresql+asyncpg://user:pass@prod-host:5432/carecircle",
        )


def test_production_rejects_default_action_token_secret():
    with pytest.raises(ValueError, match="ACTION_TOKEN_SECRET must be set"):
        Settings(
            APP_ENV="production",
            JWT_SECRET="a" * 32,
            ACTION_TOKEN_SECRET="change-me-to-64-random-chars",
            DATABASE_URL="postgresql+asyncpg://user:pass@prod-host:5432/carecircle",
        )


def test_production_rejects_docker_compose_database_url():
    with pytest.raises(ValueError, match="DATABASE_URL must not use the local docker-compose default"):
        Settings(
            APP_ENV="production",
            JWT_SECRET="a" * 32,
            ACTION_TOKEN_SECRET="b" * 32,
            DATABASE_URL="postgresql+asyncpg://carecircle:carecircle@db:5432/carecircle",
        )


def test_production_valid_configuration_passes():
    s = Settings(
        APP_ENV="production",
        JWT_SECRET="super-secure-production-jwt-secret-string-at-least-32-chars",
        ACTION_TOKEN_SECRET="super-secure-production-action-secret-string-32-chars",
        DATABASE_URL="postgresql+asyncpg://carecircle_admin:secret_pass@db.prod.internal:5432/carecircle_prod",
    )
    assert s.is_production is True
    assert s.effective_cookie_secure is True


def test_development_allows_defaults():
    s = Settings(APP_ENV="dev")
    assert s.is_production is False
    assert s.effective_cookie_secure is False
