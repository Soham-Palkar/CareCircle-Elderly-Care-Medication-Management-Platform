"""Adherence and streak repository."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select

from app.models.adherence_daily import AdherenceDaily
from app.models.recipient import CareRecipient
from app.models.streak import Streak
from app.repositories.base import BaseRepository


class AdherenceRepository(BaseRepository):

    async def upsert_daily(
        self,
        recipient_id: UUID,
        for_date: date,
        scheduled: int,
        taken: int,
        missed: int,
    ) -> AdherenceDaily:
        stmt = select(AdherenceDaily).where(
            AdherenceDaily.recipient_id == recipient_id,
            AdherenceDaily.date == for_date,
        )
        res = await self.db.execute(stmt)
        record = res.scalar_one_or_none()
        if record:
            record.scheduled_count = scheduled
            record.taken_count = taken
            record.missed_count = missed
        else:
            record = AdherenceDaily(
                recipient_id=recipient_id,
                date=for_date,
                scheduled_count=scheduled,
                taken_count=taken,
                missed_count=missed,
            )
            self.db.add(record)
        await self.db.flush()
        return record

    async def get_streak(self, recipient_id: UUID) -> Streak:
        stmt = select(Streak).where(Streak.recipient_id == recipient_id)
        res = await self.db.execute(stmt)
        streak = res.scalar_one_or_none()
        if not streak:
            streak = Streak(recipient_id=recipient_id, current_streak=0, best_streak=0)
            self.db.add(streak)
            await self.db.flush()
        return streak

    async def update_streak(
        self,
        recipient_id: UUID,
        current_streak: int,
        best_streak: int,
        last_date: date | None,
    ) -> Streak:
        streak = await self.get_streak(recipient_id)
        streak.current_streak = current_streak
        streak.best_streak = max(streak.best_streak, best_streak)
        streak.last_date = last_date
        await self.db.flush()
        return streak
