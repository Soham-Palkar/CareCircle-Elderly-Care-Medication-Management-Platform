"""Appointment service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, NotFoundError
from app.domain.permissions import has_permission
from app.models.appointment import Appointment, AppointmentStatus
from app.models.member import Member
from app.repositories.appointment_repo import AppointmentRepository
from app.repositories.audit_repo import AuditRepository


class AppointmentService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.appt_repo = AppointmentRepository(db, circle_id)
        self.audit_repo = AuditRepository(db)

    async def list_upcoming(self, recipient_id: UUID) -> list[Appointment]:
        now = datetime.now(timezone.utc)
        return await self.appt_repo.list_upcoming(recipient_id, now)

    async def list_all(self, recipient_id: UUID) -> list[Appointment]:
        return await self.appt_repo.list_all(recipient_id)

    async def create(
        self,
        actor: Member,
        recipient_id: UUID,
        data: dict[str, Any],
    ) -> Appointment:
        perms = getattr(actor, "permissions", None)
        perm_dict = {c.name: getattr(perms, c.name) for c in perms.__table__.columns} if perms else None
        if not has_permission(actor.role, "can_edit_appointments", perm_dict):
            raise ForbiddenError("You do not have permission to schedule appointments.")

        appt = await self.appt_repo.create(recipient_id, data, actor.id)
        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="appointment_created",
            entity_type="appointment",
            entity_id=appt.id,
            after={"doctor": appt.doctor_name, "scheduled_at": appt.scheduled_at.isoformat()},
        )
        await self.db.commit()
        return appt

    async def update(
        self,
        actor: Member,
        appointment_id: UUID,
        updates: dict[str, Any],
    ) -> Appointment:
        perms = getattr(actor, "permissions", None)
        perm_dict = {c.name: getattr(perms, c.name) for c in perms.__table__.columns} if perms else None
        if not has_permission(actor.role, "can_edit_appointments", perm_dict):
            raise ForbiddenError("You do not have permission to edit appointments.")

        appt = await self.appt_repo.get_by_id(appointment_id)
        if not appt:
            raise NotFoundError("Appointment not found.")

        updated = await self.appt_repo.update(appointment_id, updates)
        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="appointment_updated",
            entity_type="appointment",
            entity_id=appointment_id,
            after=updates,
        )
        await self.db.commit()
        return updated or appt

    async def cancel(self, actor: Member, appointment_id: UUID) -> Appointment:
        perms = getattr(actor, "permissions", None)
        perm_dict = {c.name: getattr(perms, c.name) for c in perms.__table__.columns} if perms else None
        if not has_permission(actor.role, "can_edit_appointments", perm_dict):
            raise ForbiddenError("You do not have permission to cancel appointments.")

        appt = await self.appt_repo.get_by_id(appointment_id)
        if not appt:
            raise NotFoundError("Appointment not found.")

        updated = await self.appt_repo.update(appointment_id, {"status": AppointmentStatus.cancelled})
        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="appointment_cancelled",
            entity_type="appointment",
            entity_id=appointment_id,
        )
        await self.db.commit()
        return updated or appt
