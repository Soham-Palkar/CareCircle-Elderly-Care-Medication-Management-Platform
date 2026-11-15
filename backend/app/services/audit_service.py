"""Audit service."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.audit_repo import AuditRepository


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = AuditRepository(db)

    async def log_action(
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
        return await self.repo.log(
            circle_id=circle_id,
            actor_member_id=actor_member_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before=before,
            after=after,
            ip=ip,
        )

    async def list_logs(
        self,
        circle_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        return await self.repo.list_for_circle(circle_id, page, page_size)
