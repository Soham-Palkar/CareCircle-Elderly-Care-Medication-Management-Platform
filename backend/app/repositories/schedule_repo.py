"""Medication schedule repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.medication import Medication
from app.models.recipient import CareRecipient
from app.models.schedule import MedicationSchedule
from app.repositories.base import BaseRepository


class ScheduleRepository(BaseRepository):

    async def create(self, medication_id: UUID, data: dict) -> MedicationSchedule:
        schedule = MedicationSchedule(medication_id=medication_id, **data)
        self.db.add(schedule)
        await self.db.flush()
        return schedule

    async def get_active_for_medication(self, medication_id: UUID) -> MedicationSchedule | None:
        stmt = (
            select(MedicationSchedule)
            .join(Medication, MedicationSchedule.medication_id == Medication.id)
            .join(CareRecipient, Medication.recipient_id == CareRecipient.id)
            .where(
                MedicationSchedule.medication_id == medication_id,
                MedicationSchedule.is_active.is_(True),
                CareRecipient.circle_id == self.circle_id,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all_for_medication(self, medication_id: UUID) -> list[MedicationSchedule]:
        stmt = (
            select(MedicationSchedule)
            .join(Medication, MedicationSchedule.medication_id == Medication.id)
            .join(CareRecipient, Medication.recipient_id == CareRecipient.id)
            .where(
                MedicationSchedule.medication_id == medication_id,
                CareRecipient.circle_id == self.circle_id,
            )
            .order_by(MedicationSchedule.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def deactivate(self, schedule_id: UUID) -> MedicationSchedule | None:
        stmt = (
            select(MedicationSchedule)
            .join(Medication, MedicationSchedule.medication_id == Medication.id)
            .join(CareRecipient, Medication.recipient_id == CareRecipient.id)
            .where(
                MedicationSchedule.id == schedule_id,
                CareRecipient.circle_id == self.circle_id,
            )
        )
        res = await self.db.execute(stmt)
        schedule = res.scalar_one_or_none()
        if schedule:
            schedule.is_active = False
            await self.db.flush()
        return schedule

    async def get_all_active_for_recipient(self, recipient_id: UUID) -> list[MedicationSchedule]:
        stmt = (
            select(MedicationSchedule)
            .join(Medication, MedicationSchedule.medication_id == Medication.id)
            .join(CareRecipient, Medication.recipient_id == CareRecipient.id)
            .where(
                Medication.recipient_id == recipient_id,
                MedicationSchedule.is_active.is_(True),
                CareRecipient.circle_id == self.circle_id,
            )
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
