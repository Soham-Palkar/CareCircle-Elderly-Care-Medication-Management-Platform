"""FastAPI dependency injectors for database sessions, auth, and role guards."""

from __future__ import annotations

from typing import AsyncGenerator
from uuid import UUID

from fastapi import Cookie, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import async_session_factory


# ─────────────────────────────────────────────────────────────────────────────
# Database session
# ─────────────────────────────────────────────────────────────────────────────


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session, rolling back on error."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# ─────────────────────────────────────────────────────────────────────────────
# Current member (from httpOnly cookie JWT)
# ─────────────────────────────────────────────────────────────────────────────

# We import Member lazily to avoid circular imports at module load time.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.member import Member


async def get_current_member(
    request: Request,
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> "Member":
    """Read the JWT from httpOnly 'access_token' cookie or Authorization Bearer header."""
    token = access_token
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

    if not token:
        raise UnauthorizedError("Not authenticated.")

    payload = decode_token(token)  # raises UnauthorizedError if invalid

    member_id_str: str | None = payload.get("sub")
    if not member_id_str:
        raise UnauthorizedError("Token missing subject claim.")

    # Import here to avoid circular dependency
    from app.models.member import Member as MemberModel
    from sqlalchemy import select

    result = await db.execute(select(MemberModel).where(MemberModel.id == UUID(member_id_str)))
    member: MemberModel | None = result.scalar_one_or_none()

    if member is None or not member.is_active:
        raise UnauthorizedError("Member not found or inactive.")

    return member


async def get_circle_id(
    member: "Member" = Depends(get_current_member),
) -> UUID:
    return member.circle_id  # type: ignore[return-value]


# ─────────────────────────────────────────────────────────────────────────────
# Role guards
# ─────────────────────────────────────────────────────────────────────────────


def _check_role(member: "Member", allowed: set[str]) -> None:
    if str(member.role) not in allowed and member.role.value not in allowed:
        raise ForbiddenError(f"Role '{member.role}' is not permitted for this action.")


async def require_elder(member: "Member" = Depends(get_current_member)) -> "Member":
    _check_role(member, {"elder"})
    return member


async def require_caretaker_or_elder(
    member: "Member" = Depends(get_current_member),
) -> "Member":
    _check_role(member, {"caretaker", "elder"})
    return member


async def require_any_role(member: "Member" = Depends(get_current_member)) -> "Member":
    _check_role(member, {"family", "caretaker", "doctor", "elder"})
    return member


async def require_doctor_or_above(
    member: "Member" = Depends(get_current_member),
) -> "Member":
    _check_role(member, {"doctor", "caretaker", "elder"})
    return member
