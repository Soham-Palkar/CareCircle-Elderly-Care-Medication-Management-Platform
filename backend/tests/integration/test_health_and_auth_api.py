"""Integration and route verification tests."""

import pytest
from app.main import app
from app.core.errors import UnauthorizedError
from app.domain.permissions import has_permission
from app.domain.types import Role


def test_routes_registered_in_app():
    # Verify openapi routes are properly wired up via openapi spec
    openapi = app.openapi()
    paths = openapi.get("paths", {})
    assert len(paths) >= 40
    assert "/health" in paths
    assert "/ready" in paths
    assert "/api/v1/health" in paths
    assert "/api/v1/doses" in paths
    assert "/api/v1/medications" in paths
    assert "/api/v1/appointments" in paths
    assert "/api/v1/twin/flags" in paths
    assert "/api/v1/scans" in paths
    assert "/api/v1/scans/verify-dose" in paths
    assert "/api/v1/voice/intent" in paths


def test_unauthenticated_access_throws_unauthorized():
    from app.core.security import decode_token
    with pytest.raises(UnauthorizedError):
        decode_token("invalid.bearer.token")
