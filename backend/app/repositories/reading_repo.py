"""Health readings repository."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select

from app.models.health_reading import HealthReading, ReadingKind
from app.models.recipient import CareRecipient
from app.repositories.base import BaseRepository


class ReadingRepository(BaseRepository):

    async def create(self, recipient_id: UUID, data: dict) -> HealthReading:
        reading = HealthReading(recipient_id=recipient_id, **data)
        self.db.add(reading)
        await self.db.flush()
        return reading

    async def get_latest_by_kind(self, recipient_id: UUID, kind: ReadingKind) -> HealthReading | None:
        stmt = (
            select(HealthReading)
            .join(CareRecipient, HealthReading.recipient_id == CareRecipient.id)
            .where(
                HealthReading.recipient_id == recipient_id,
                HealthReading.kind == kind,
                CareRecipient.circle_id == self.circle_id,
            )
            .order_by(HealthReading.recorded_at.desc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_history(self, recipient_id: UUID, kind: ReadingKind, days: int = 7) -> list[HealthReading]:
        start = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(HealthReading)
            .join(CareRecipient, HealthReading.recipient_id == CareRecipient.id)
            .where(
                HealthReading.recipient_id == recipient_id,
                HealthReading.kind == kind,
                HealthReading.recorded_at >= start,
                CareRecipient.circle_id == self.circle_id,
            )
            .order_by(HealthReading.recorded_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_7d_baseline(self, recipient_id: UUID, kind: ReadingKind) -> float | None:
        start = datetime.now(timezone.utc) - timedelta(days=7)
        stmt = (
            select(func.avg(HealthReading.value))
            .join(CareRecipient, HealthReading.recipient_id == CareRecipient.id)
            .where(
                HealthReading.recipient_id == recipient_id,
                HealthReading.kind == kind,
                HealthReading.recorded_at >= start,
                CareRecipient.circle_id == self.circle_id,
            )
        )
        res = await self.db.execute(stmt)
        avg_val = res.scalar_one_or_none()
        return float(avg_val) if avg_val is not None else None
