"""Base repository enforcing circle_id tenant scoping."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Base repository from which all circle-scoped repositories inherit.

    Enforces that queries are filtered by circle_id to guarantee tenant isolation.
    """

    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
