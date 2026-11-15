"""Audit log repository (append-only)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditRepository:
    """Audit log repository. Always append-only."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(
        self,
        circle_id: UUID,
        actor_member_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        ip: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            circle_id=circle_id,
            actor_member_id=actor_member_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before=before,
            after=after,
            ip=ip,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def list_for_circle(
        self,
        circle_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        count_stmt = select(func.count(AuditLog.id)).where(AuditLog.circle_id == circle_id)
        total = (await self.db.execute(count_stmt)).scalar_one() or 0

        stmt = (
            select(AuditLog)
            .where(AuditLog.circle_id == circle_id)
            .order_by(AuditLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all()), total
