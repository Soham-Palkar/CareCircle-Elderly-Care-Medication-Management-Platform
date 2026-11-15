"""Dose event repository."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload

from app.models.dose_event import DoseEvent, DoseState
from app.models.medication import Medication
from app.models.recipient import CareRecipient
from app.repositories.base import BaseRepository


class DoseRepository(BaseRepository):

    async def check_idempotency(self, idempotency_key: str) -> DoseEvent | None:
        if not idempotency_key:
            return None
        stmt = (
            select(DoseEvent)
            .join(CareRecipient, DoseEvent.recipient_id == CareRecipient.id)
            .where(
                DoseEvent.idempotency_key == idempotency_key,
                CareRecipient.circle_id == self.circle_id,
            )
            .options(selectinload(DoseEvent.medication))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def bulk_create_if_not_exists(self, events: list[dict]) -> int:
        if not events:
            return 0
        created = 0
        for ev in events:
            stmt = select(DoseEvent).where(
                DoseEvent.schedule_id == ev["schedule_id"],
                DoseEvent.scheduled_at == ev["scheduled_at"],
            )
            res = await self.db.execute(stmt)
            if not res.scalar_one_or_none():
                dose = DoseEvent(**ev)
                self.db.add(dose)
                created += 1
        await self.db.flush()
        return created

    async def get_by_id(self, event_id: UUID) -> DoseEvent | None:
        stmt = (
            select(DoseEvent)
            .join(CareRecipient, DoseEvent.recipient_id == CareRecipient.id)
            .where(
                DoseEvent.id == event_id,
                CareRecipient.circle_id == self.circle_id,
            )
            .options(selectinload(DoseEvent.medication))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_state(self, event_id: UUID, new_state: DoseState, **extra_fields) -> DoseEvent | None:
        dose = await self.get_by_id(event_id)
        if not dose:
            return None
        dose.state = new_state
        for k, v in extra_fields.items():
            if hasattr(dose, k) and v is not None:
                setattr(dose, k, v)
        await self.db.flush()
        return dose

    async def list_for_recipient(
        self,
        recipient_id: UUID,
        from_dt: datetime,
        to_dt: datetime,
    ) -> list[DoseEvent]:
        stmt = (
            select(DoseEvent)
            .join(CareRecipient, DoseEvent.recipient_id == CareRecipient.id)
            .where(
                DoseEvent.recipient_id == recipient_id,
                DoseEvent.scheduled_at >= from_dt,
                DoseEvent.scheduled_at <= to_dt,
                CareRecipient.circle_id == self.circle_id,
            )
            .options(selectinload(DoseEvent.medication))
            .order_by(DoseEvent.scheduled_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_next_due(self, recipient_id: UUID, now: datetime) -> DoseEvent | None:
        stmt = (
            select(DoseEvent)
            .join(CareRecipient, DoseEvent.recipient_id == CareRecipient.id)
            .where(
                DoseEvent.recipient_id == recipient_id,
                DoseEvent.state.in_([DoseState.scheduled, DoseState.reminded, DoseState.snoozed]),
                DoseEvent.scheduled_at >= now - timedelta(hours=2),
                CareRecipient.circle_id == self.circle_id,
            )
            .options(selectinload(DoseEvent.medication))
            .order_by(DoseEvent.scheduled_at.asc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_adherence_7d(self, recipient_id: UUID, as_of: date) -> dict:
        as_of_dt = datetime.combine(as_of, datetime.min.time()).replace(tzinfo=timezone.utc)
        start_dt = as_of_dt - timedelta(days=7)

        stmt = (
            select(
                func.count(DoseEvent.id).label("total"),
                func.count(DoseEvent.id).filter(DoseEvent.state.in_([DoseState.taken, DoseState.taken_late])).label("taken"),
                func.count(DoseEvent.id).filter(DoseEvent.state == DoseState.missed).label("missed"),
            )
            .join(CareRecipient, DoseEvent.recipient_id == CareRecipient.id)
            .where(
                DoseEvent.recipient_id == recipient_id,
                DoseEvent.scheduled_at >= start_dt,
                DoseEvent.scheduled_at <= as_of_dt + timedelta(days=1),
                CareRecipient.circle_id == self.circle_id,
            )
        )
        res = await self.db.execute(stmt)
        row = res.one()
        total = row.total or 0
        taken = row.taken or 0
        missed = row.missed or 0
        rate = (taken / total) if total > 0 else 1.0
        return {
            "total": total,
            "taken": taken,
            "missed": missed,
            "adherence": round(rate, 2),
        }
