"""Appointment repository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from app.models.appointment import Appointment, AppointmentStatus
from app.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository):

    async def create(self, recipient_id: UUID, data: dict, created_by: UUID | None) -> Appointment:
        appt = Appointment(
            circle_id=self.circle_id,
            recipient_id=recipient_id,
            created_by=created_by,
            **data,
        )
        self.db.add(appt)
        await self.db.flush()
        return appt

    async def get_by_id(self, appointment_id: UUID) -> Appointment | None:
        stmt = select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.circle_id == self.circle_id,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_upcoming(self, recipient_id: UUID, from_dt: datetime) -> list[Appointment]:
        stmt = (
            select(Appointment)
            .where(
                Appointment.recipient_id == recipient_id,
                Appointment.circle_id == self.circle_id,
                Appointment.status == AppointmentStatus.upcoming,
                Appointment.scheduled_at >= from_dt,
            )
            .order_by(Appointment.scheduled_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def list_all(self, recipient_id: UUID) -> list[Appointment]:
        stmt = (
            select(Appointment)
            .where(
                Appointment.recipient_id == recipient_id,
                Appointment.circle_id == self.circle_id,
            )
            .order_by(Appointment.scheduled_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update(self, appointment_id: UUID, updates: dict) -> Appointment | None:
        appt = await self.get_by_id(appointment_id)
        if not appt:
            return None
        for k, v in updates.items():
            if hasattr(appt, k) and v is not None:
                setattr(appt, k, v)
        await self.db.flush()
        return appt
