"""Notification outbox service."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationChannel, NotificationType
from app.repositories.notification_repo import NotificationRepository


class NotificationService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.notif_repo = NotificationRepository(db, circle_id)

    async def enqueue(
        self,
        member_id: UUID,
        channel: NotificationChannel,
        notif_type: NotificationType,
        payload: dict[str, Any],
        dedupe_key: str,
        related_event_id: UUID | None = None,
    ) -> tuple[Notification, bool]:
        data = {
            "member_id": member_id,
            "channel": channel,
            "type": notif_type,
            "payload": payload,
            "dedupe_key": dedupe_key,
            "related_event_id": related_event_id,
        }
        notif, created = await self.notif_repo.create_if_not_exists(data)
        await self.db.commit()
        return notif, created

    async def list_for_member(self, member_id: UUID) -> list[Notification]:
        return await self.notif_repo.list_for_member(member_id)
