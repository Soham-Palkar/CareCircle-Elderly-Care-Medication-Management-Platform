"""Pytest configuration and shared fixtures for CareCircle tests."""

import asyncio
import os
import sys
from typing import AsyncGenerator, Callable
from unittest.mock import AsyncMock
import uuid

# Force test configuration
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "carecircle-test-secret-key-that-is-at-least-32-chars-long"
os.environ["HMAC_SECRET"] = "carecircle-test-hmac-secret-for-action-links-very-secure"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["APP_LOG_LEVEL"] = "WARNING"

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.deps import get_db
from app.core.security import create_access_token


@pytest.fixture(autouse=True)
def override_db_dependency():
    """Override get_db to prevent real DB connection hangs in fast unit/integration tests."""
    mock_session = AsyncMock()

    async def _mock_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = _mock_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Synchronous test client for FastAPI routes."""
    return TestClient(app)


@pytest.fixture
def run_async() -> Callable:
    """Helper to run async functions within standard sync tests without requiring pytest-asyncio."""
    def _run(coro):
        return asyncio.run(coro)
    return _run


@pytest.fixture
def make_token() -> Callable:
    """Generate a valid test JWT bearer token."""
    def _token(circle_id: uuid.UUID, member_id: uuid.UUID, role: str) -> str:
        return create_access_token(member_id=member_id, circle_id=circle_id, role=role)
    return _token
