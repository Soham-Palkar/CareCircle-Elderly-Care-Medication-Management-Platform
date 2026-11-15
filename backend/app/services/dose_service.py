"""Dose lifecycle service managing taken, snooze, skip, and adherence triggers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.domain.permissions import has_permission
from app.domain.state_machine import can_transition, transition
from app.domain.types import DoseRecordedVia, DoseState
from app.models.dose_event import DoseEvent
from app.models.member import Member
from app.repositories.adherence_repo import AdherenceRepository
from app.repositories.audit_repo import AuditRepository
from app.repositories.dose_repo import DoseRepository
from app.repositories.medication_repo import MedicationRepository
from app.services.realtime import realtime_broker
from app.services.streak_service import StreakService


class DoseService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.dose_repo = DoseRepository(db, circle_id)
        self.med_repo = MedicationRepository(db, circle_id)
        self.adh_repo = AdherenceRepository(db, circle_id)
        self.audit_repo = AuditRepository(db)

    async def list_doses(
        self,
        recipient_id: UUID,
        from_dt: datetime,
        to_dt: datetime,
    ) -> list[DoseEvent]:
        return await self.dose_repo.list_for_recipient(recipient_id, from_dt, to_dt)

    async def get_next_dose(self, recipient_id: UUID) -> DoseEvent | None:
        now = datetime.now(timezone.utc)
        return await self.dose_repo.get_next_due(recipient_id, now)

    async def mark_taken(
        self,
        actor: Member,
        event_id: UUID,
        via: str = "app",
        idempotency_key: str | None = None,
    ) -> DoseEvent:
        perms = getattr(actor, "permissions", None)
        perm_dict = {c.name: getattr(perms, c.name) for c in perms.__table__.columns} if perms else None
        if not has_permission(actor.role, "can_mark_doses", perm_dict):
            raise ForbiddenError("You do not have permission to record doses.")

        # 1. Idempotency check
        if idempotency_key:
            existing = await self.dose_repo.check_idempotency(idempotency_key)
            if existing:
                return existing

        dose = await self.dose_repo.get_by_id(event_id)
        if not dose:
            raise NotFoundError("Dose event not found.")

        # 2. Determine target state (taken or taken_late)
        target_state = DoseState.taken_late if dose.state == DoseState.missed else DoseState.taken

        # 3. Validate state transition
        try:
            new_state = transition(DoseState(dose.state.value), target_state)
        except ValueError as err:
            raise ConflictError(str(err)) from err

        now = datetime.now(timezone.utc)
        recorded_via = DoseRecordedVia(via) if via in DoseRecordedVia._value2member_map_ else DoseRecordedVia.app

        dose = await self.dose_repo.update_state(
            event_id=event_id,
            new_state=new_state,
            taken_at=now,
            recorded_by=actor.id,
            recorded_via=recorded_via,
            idempotency_key=idempotency_key,
        )

        # 4. Decrement medication stock
        if dose and dose.medication_id:
            await self.med_repo.decrement_stock(dose.medication_id, dose.medication.dose_quantity)

        # 5. Update daily adherence aggregate and streak
        today_date = now.date()
        streak_svc = StreakService(self.db, self.circle_id)
        await streak_svc.record_dose_taken(dose.recipient_id, today_date)

        # 6. Audit log & Realtime event
        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="dose_taken",
            entity_type="dose_event",
            entity_id=event_id,
            after={"state": new_state.value, "via": via},
        )
        await realtime_broker.publish(
            self.circle_id,
            {"type": "dose_state_changed", "dose_id": str(event_id), "state": new_state.value},
        )

        await self.db.commit()
        return dose

    async def snooze(
        self,
        actor: Member,
        event_id: UUID,
        snooze_minutes: int = 15,
        idempotency_key: str | None = None,
    ) -> DoseEvent:
        if idempotency_key:
            existing = await self.dose_repo.check_idempotency(idempotency_key)
            if existing:
                return existing

        dose = await self.dose_repo.get_by_id(event_id)
        if not dose:
            raise NotFoundError("Dose event not found.")

        try:
            new_state = transition(DoseState(dose.state.value), DoseState.snoozed)
        except ValueError as err:
            raise ConflictError(str(err)) from err

        now = datetime.now(timezone.utc)
        snooze_until = now + timedelta(minutes=snooze_minutes)

        dose = await self.dose_repo.update_state(
            event_id=event_id,
            new_state=new_state,
            snooze_until=snooze_until,
            idempotency_key=idempotency_key,
        )

        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="dose_snoozed",
            entity_type="dose_event",
            entity_id=event_id,
            after={"snooze_minutes": snooze_minutes},
        )
        await realtime_broker.publish(
            self.circle_id,
            {"type": "dose_state_changed", "dose_id": str(event_id), "state": "snoozed"},
        )
        await self.db.commit()
        return dose

    async def skip(
        self,
        actor: Member,
        event_id: UUID,
        reason: str,
        idempotency_key: str | None = None,
    ) -> DoseEvent:
        if idempotency_key:
            existing = await self.dose_repo.check_idempotency(idempotency_key)
            if existing:
                return existing

        dose = await self.dose_repo.get_by_id(event_id)
        if not dose:
            raise NotFoundError("Dose event not found.")

        try:
            new_state = transition(DoseState(dose.state.value), DoseState.skipped)
        except ValueError as err:
            raise ConflictError(str(err)) from err

        dose = await self.dose_repo.update_state(
            event_id=event_id,
            new_state=new_state,
            skip_reason=reason,
            idempotency_key=idempotency_key,
        )

        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="dose_skipped",
            entity_type="dose_event",
            entity_id=event_id,
            after={"skip_reason": reason},
        )
        await realtime_broker.publish(
            self.circle_id,
            {"type": "dose_state_changed", "dose_id": str(event_id), "state": "skipped"},
        )
        await self.db.commit()
        return dose
