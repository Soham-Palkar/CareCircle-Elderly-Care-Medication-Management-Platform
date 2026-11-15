"""Rate limiting using slowapi and in-memory storage."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.errors import RateLimitError


def _client_ip(request: Request) -> str:
    return get_remote_address(request) or "127.0.0.1"


limiter = Limiter(
    key_func=_client_ip,
    default_limits=["100/minute"],
    storage_uri="memory://",
)

# Custom limit decorators
LOGIN_LIMIT = "10/minute"
UPLOAD_LIMIT = "30/hour"
VOICE_LIMIT = "60/minute"
ACTION_LINK_LIMIT = "10/minute"
