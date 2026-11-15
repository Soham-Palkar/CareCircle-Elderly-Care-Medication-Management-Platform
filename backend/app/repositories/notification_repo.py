"""Notification outbox repository."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from app.models.notification import Notification, NotificationStatus
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository):

    async def create_if_not_exists(self, data: dict) -> tuple[Notification, bool]:
        dedupe_key = data["dedupe_key"]
        stmt = select(Notification).where(Notification.dedupe_key == dedupe_key)
        res = await self.db.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            return existing, False

        notif = Notification(circle_id=self.circle_id, **data)
        self.db.add(notif)
        await self.db.flush()
        return notif, True

    async def get_pending_batch(self, limit: int = 50) -> list[Notification]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Notification)
            .where(
                Notification.status == NotificationStatus.pending,
                Notification.next_attempt_at <= now,
            )
            .order_by(Notification.next_attempt_at.asc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def mark_sent(self, notification_id: UUID) -> None:
        stmt = select(Notification).where(Notification.id == notification_id)
        res = await self.db.execute(stmt)
        notif = res.scalar_one_or_none()
        if notif:
            notif.status = NotificationStatus.sent
            notif.sent_at = datetime.now(timezone.utc)
            await self.db.flush()

    async def mark_failed(self, notification_id: UUID, next_attempt_at: datetime) -> None:
        stmt = select(Notification).where(Notification.id == notification_id)
        res = await self.db.execute(stmt)
        notif = res.scalar_one_or_none()
        if notif:
            notif.attempts += 1
            if notif.attempts >= 5:
                notif.status = NotificationStatus.failed
            else:
                notif.next_attempt_at = next_attempt_at
            await self.db.flush()

    async def list_for_member(self, member_id: UUID, limit: int = 50) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(
                Notification.member_id == member_id,
                Notification.circle_id == self.circle_id,
            )
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
