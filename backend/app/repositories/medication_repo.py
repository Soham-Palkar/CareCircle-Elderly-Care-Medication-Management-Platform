"""Medication repository."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.medication import Medication, MedicationStatus
from app.models.recipient import CareRecipient
from app.repositories.base import BaseRepository


class MedicationRepository(BaseRepository):

    async def create(self, data: dict, recipient_id: UUID) -> Medication:
        med = Medication(recipient_id=recipient_id, **data)
        self.db.add(med)
        await self.db.flush()
        return med

    async def get_by_id(self, medication_id: UUID) -> Medication | None:
        stmt = (
            select(Medication)
            .join(CareRecipient, Medication.recipient_id == CareRecipient.id)
            .where(
                Medication.id == medication_id,
                CareRecipient.circle_id == self.circle_id,
            )
            .options(selectinload(Medication.schedules))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_active(self, recipient_id: UUID) -> list[Medication]:
        stmt = (
            select(Medication)
            .join(CareRecipient, Medication.recipient_id == CareRecipient.id)
            .where(
                Medication.recipient_id == recipient_id,
                Medication.status == MedicationStatus.active,
                CareRecipient.circle_id == self.circle_id,
            )
            .options(selectinload(Medication.schedules))
            .order_by(Medication.name.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def list_all(self, recipient_id: UUID) -> list[Medication]:
        stmt = (
            select(Medication)
            .join(CareRecipient, Medication.recipient_id == CareRecipient.id)
            .where(
                Medication.recipient_id == recipient_id,
                CareRecipient.circle_id == self.circle_id,
            )
            .options(selectinload(Medication.schedules))
            .order_by(Medication.name.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update(self, medication_id: UUID, updates: dict) -> Medication | None:
        med = await self.get_by_id(medication_id)
        if not med:
            return None
        for k, v in updates.items():
            if hasattr(med, k) and v is not None:
                setattr(med, k, v)
        await self.db.flush()
        return med

    async def archive(self, medication_id: UUID) -> Medication | None:
        med = await self.get_by_id(medication_id)
        if med:
            med.status = MedicationStatus.archived
            await self.db.flush()
        return med

    async def decrement_stock(self, medication_id: UUID, quantity: Decimal) -> Medication | None:
        med = await self.get_by_id(medication_id)
        if med:
            med.stock_count = max(Decimal("0.0"), med.stock_count - quantity)
            await self.db.flush()
        return med
