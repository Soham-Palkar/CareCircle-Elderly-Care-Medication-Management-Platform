"""Schedule expansion and dose event pre-materialisation service."""

from __future__ import annotations

from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schedule_expansion import ScheduleParams, expand_schedule
from app.models.recipient import CareRecipient
from app.models.schedule import MedicationSchedule
from app.repositories.dose_repo import DoseRepository
from app.repositories.schedule_repo import ScheduleRepository


class ScheduleService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.sched_repo = ScheduleRepository(db, circle_id)
        self.dose_repo = DoseRepository(db, circle_id)

    async def regenerate_events_for_schedule(
        self,
        schedule: MedicationSchedule,
        recipient_id: UUID,
        days_ahead: int = 7,
    ) -> int:
        stmt = select(CareRecipient).where(CareRecipient.id == recipient_id)
        res = await self.db.execute(stmt)
        recipient = res.scalar_one_or_none()
        if not recipient:
            return 0

        today = date.today()
        from_date = max(today, schedule.start_date)
        to_date = today + timedelta(days=days_ahead)
        if schedule.end_date:
            to_date = min(to_date, schedule.end_date)

        if from_date > to_date:
            return 0

        params = ScheduleParams(
            schedule_id=schedule.id,
            kind=schedule.kind.value,
            time_of_day=schedule.time_of_day,
            anchor=schedule.anchor,
            anchor_offset_min=schedule.anchor_offset_min,
            days_of_week=schedule.days_of_week,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            recipient_timezone=recipient.timezone or "Asia/Kolkata",
            routine_times=recipient.routine_times or {},
        )

        events_to_create = []
        for sched_id, scheduled_at_utc in expand_schedule(params, from_date, to_date):
            events_to_create.append({
                "schedule_id": sched_id,
                "medication_id": schedule.medication_id,
                "recipient_id": recipient_id,
                "scheduled_at": scheduled_at_utc,
            })

        count = await self.dose_repo.bulk_create_if_not_exists(events_to_create)
        return count

    async def regenerate_all_for_recipient(
        self,
        recipient_id: UUID,
        days_ahead: int = 7,
    ) -> int:
        schedules = await self.sched_repo.get_all_active_for_recipient(recipient_id)
        total = 0
        for sched in schedules:
            total += await self.regenerate_events_for_schedule(sched, recipient_id, days_ahead)
        return total
