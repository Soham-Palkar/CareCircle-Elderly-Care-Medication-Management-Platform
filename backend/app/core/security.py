"""Security utilities: password hashing, JWT, and action tokens."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.errors import UnauthorizedError

_ph = PasswordHasher()

# ── Used action tokens (in-memory set; for production use a DB-backed store) ─
_used_action_tokens: set[str] = set()


# ─────────────────────────────────────────────────────────────────────────────
# Passcode hashing (argon2id)
# ─────────────────────────────────────────────────────────────────────────────

def hash_passcode(plain: str) -> str:
    """Return an argon2id hash of *plain*.  Never log the return value."""
    return _ph.hash(plain)


def verify_passcode(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*.  Never log either argument."""
    try:
        return _ph.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


# ─────────────────────────────────────────────────────────────────────────────
# JWT tokens
# ─────────────────────────────────────────────────────────────────────────────

def _now() -> int:
    return int(time.time())


def create_access_token(
    member_id: UUID | str,
    circle_id: UUID | str,
    role: str,
) -> str:
    """Mint a short-lived access JWT.  Never log the returned token."""
    settings = get_settings()
    payload: dict[str, Any] = {
        "sub": str(member_id),
        "circle_id": str(circle_id),
        "role": role,
        "type": "access",
        "iat": _now(),
        "exp": _now() + settings.access_token_minutes * 60,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_refresh_token(member_id: UUID | str) -> str:
    """Mint a long-lived refresh JWT.  Never log the returned token."""
    settings = get_settings()
    payload: dict[str, Any] = {
        "sub": str(member_id),
        "type": "refresh",
        "iat": _now(),
        "exp": _now() + settings.refresh_token_days * 86400,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT.  Raises UnauthorizedError on failure."""
    settings = get_settings()
    try:
        payload: dict[str, Any] = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except JWTError as exc:
        raise UnauthorizedError("Token is invalid or expired.") from exc


# ─────────────────────────────────────────────────────────────────────────────
# Action tokens (HMAC-SHA256, single-use)
# ─────────────────────────────────────────────────────────────────────────────

_ACTION_TOKEN_TTL = 3600  # 1 hour in seconds


def create_action_token(
    dose_event_id: UUID | str,
    action: str,
    member_id: UUID | str,
) -> str:
    """Create a one-time HMAC-signed action token (for email action links).

    Format: base64url( JSON payload ) + '.' + HMAC signature
    Never log the returned token value.
    """
    settings = get_settings()
    payload = {
        "dose_event_id": str(dose_event_id),
        "action": action,
        "member_id": str(member_id),
        "exp": _now() + _ACTION_TOKEN_TTL,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    import base64

    encoded = base64.urlsafe_b64encode(payload_bytes).rstrip(b"=").decode()
    sig = hmac.new(
        settings.action_token_secret.encode(),
        encoded.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{encoded}.{sig}"


def verify_action_token(token: str) -> dict[str, Any]:
    """Verify and consume a one-time action token.

    Raises UnauthorizedError if the token is expired, invalid, or already used.
    """
    import base64

    settings = get_settings()

    try:
        encoded, sig = token.rsplit(".", 1)
    except ValueError:
        raise UnauthorizedError("Malformed action token.")

    expected_sig = hmac.new(
        settings.action_token_secret.encode(),
        encoded.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(sig, expected_sig):
        raise UnauthorizedError("Action token signature invalid.")

    # Check reuse
    if token in _used_action_tokens:
        raise UnauthorizedError("Action token has already been used.")

    # Decode payload
    try:
        padding = 4 - len(encoded) % 4
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * padding))
    except Exception as exc:
        raise UnauthorizedError("Action token payload could not be decoded.") from exc

    # Check expiry
    if _now() > payload.get("exp", 0):
        raise UnauthorizedError("Action token has expired.")

    # Mark as used
    _used_action_tokens.add(token)

    return payload
