"""Adherence reporting service."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.adherence_repo import AdherenceRepository
from app.repositories.dose_repo import DoseRepository


class AdherenceService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.dose_repo = DoseRepository(db, circle_id)
        self.adh_repo = AdherenceRepository(db, circle_id)

    async def get_summary(self, recipient_id: UUID, days: int = 7) -> dict:
        today = date.today()
        data = await self.dose_repo.get_adherence_7d(recipient_id, today)
        streak = await self.adh_repo.get_streak(recipient_id)

        return {
            "recipient_id": recipient_id,
            "total_scheduled": data["total"],
            "taken": data["taken"],
            "missed": data["missed"],
            "adherence_pct": data["adherence"],
            "current_streak": streak.current_streak,
            "best_streak": streak.best_streak,
        }
