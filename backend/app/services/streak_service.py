"""Streak and relationship-based rewards service."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reward import Reward, RewardType
from app.models.streak import Streak
from app.repositories.adherence_repo import AdherenceRepository


class StreakService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.adh_repo = AdherenceRepository(db, circle_id)

    async def get_streak(self, recipient_id: UUID) -> Streak:
        return await self.adh_repo.get_streak(recipient_id)

    async def record_dose_taken(self, recipient_id: UUID, for_date: date) -> Streak:
        streak = await self.adh_repo.get_streak(recipient_id)

        if streak.last_date == for_date:
            return streak

        if streak.last_date == for_date - timedelta(days=1):
            streak.current_streak += 1
        elif streak.last_date is None or streak.last_date < for_date - timedelta(days=1):
            streak.current_streak = 1

        streak.best_streak = max(streak.best_streak, streak.current_streak)
        streak.last_date = for_date
        await self.db.flush()

        await self._check_rewards(recipient_id, streak.current_streak)
        return streak

    async def _check_rewards(self, recipient_id: UUID, current_streak: int) -> None:
        milestones = [
            (7, RewardType.call, "Family celebration call unlocked!"),
            (14, RewardType.photo, "Special family memory photo unlocked!"),
            (30, RewardType.message, "Heartwarming appreciation message from family!"),
        ]

        now = datetime.now(timezone.utc)
        for days, r_type, ref in milestones:
            if current_streak >= days:
                stmt = select(Reward).where(
                    Reward.recipient_id == recipient_id,
                    Reward.threshold_days == days,
                )
                res = await self.db.execute(stmt)
                if not res.scalar_one_or_none():
                    reward = Reward(
                        recipient_id=recipient_id,
                        threshold_days=days,
                        reward_type=r_type,
                        reward_ref=ref,
                        unlocked_at=now,
                    )
                    self.db.add(reward)
                    await self.db.flush()
