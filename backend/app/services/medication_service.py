"""Medication management service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, NotFoundError
from app.domain.permissions import has_permission
from app.domain.risk_rules import check_r6_duplicate_or_interaction
from app.domain.types import Role
from app.models.medication import Medication
from app.models.member import Member
from app.models.schedule import MedicationSchedule
from app.repositories.audit_repo import AuditRepository
from app.repositories.medication_repo import MedicationRepository
from app.repositories.schedule_repo import ScheduleRepository
from app.services.schedule_service import ScheduleService

_RULES_PATH = Path(__file__).parent.parent / "db" / "seed_data" / "interaction_rules.json"


def _load_interaction_rules() -> list[dict]:
    if _RULES_PATH.exists():
        try:
            with open(_RULES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


class MedicationService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.med_repo = MedicationRepository(db, circle_id)
        self.schedule_repo = ScheduleRepository(db, circle_id)
        self.audit_repo = AuditRepository(db)

    async def list_active(self, recipient_id: UUID) -> list[Medication]:
        return await self.med_repo.list_active(recipient_id)

    async def get_medication(self, medication_id: UUID) -> Medication:
        med = await self.med_repo.get_by_id(medication_id)
        if not med:
            raise NotFoundError("Medication not found in this circle.")
        return med

    async def check_advisory(self, new_name: str, recipient_id: UUID) -> dict[str, Any] | None:
        active = await self.med_repo.list_active(recipient_id)
        existing_names = [m.name for m in active]
        rules = _load_interaction_rules()
        res = check_r6_duplicate_or_interaction(new_name, existing_names, rules)
        if res:
            return {
                "rule_code": res.rule_code,
                "severity": res.severity.value,
                "message": res.message,
                "evidence": res.evidence,
            }
        return None

    async def create_medication(
        self,
        actor: Member,
        recipient_id: UUID,
        data: dict[str, Any],
    ) -> tuple[Medication, dict[str, Any] | None]:
        perms = getattr(actor, "permissions", None)
        perm_dict = {c.name: getattr(perms, c.name) for c in perms.__table__.columns} if perms else None
        if not has_permission(actor.role, "can_edit_meds", perm_dict):
            raise ForbiddenError("You do not have permission to add medications.")

        advisory = await self.check_advisory(data["name"], recipient_id)

        med = await self.med_repo.create(data, recipient_id)
        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="medication_created",
            entity_type="medication",
            entity_id=med.id,
            after={"name": med.name, "strength": med.strength},
        )
        await self.db.commit()
        return med, advisory

    async def update_medication(
        self,
        actor: Member,
        medication_id: UUID,
        updates: dict[str, Any],
    ) -> Medication:
        perms = getattr(actor, "permissions", None)
        perm_dict = {c.name: getattr(perms, c.name) for c in perms.__table__.columns} if perms else None
        if not has_permission(actor.role, "can_edit_meds", perm_dict):
            raise ForbiddenError("You do not have permission to edit medications.")

        med = await self.get_medication(medication_id)
        before_dict = {k: getattr(med, k) for k in updates if hasattr(med, k)}

        updated = await self.med_repo.update(medication_id, updates)
        if not updated:
            raise NotFoundError("Medication not found.")

        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="medication_updated",
            entity_type="medication",
            entity_id=medication_id,
            before=before_dict,
            after=updates,
        )
        await self.db.commit()
        return updated

    async def archive_medication(self, actor: Member, medication_id: UUID) -> Medication:
        perms = getattr(actor, "permissions", None)
        perm_dict = {c.name: getattr(perms, c.name) for c in perms.__table__.columns} if perms else None
        if not has_permission(actor.role, "can_edit_meds", perm_dict):
            raise ForbiddenError("You do not have permission to archive medications.")

        med = await self.get_medication(medication_id)
        # Deactivate all active schedules
        active_sched = await self.schedule_repo.get_active_for_medication(medication_id)
        if active_sched:
            await self.schedule_repo.deactivate(active_sched.id)

        archived = await self.med_repo.archive(medication_id)
        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="medication_archived",
            entity_type="medication",
            entity_id=medication_id,
        )
        await self.db.commit()
        return archived or med

    async def create_schedule(
        self,
        actor: Member,
        medication_id: UUID,
        data: dict[str, Any],
    ) -> MedicationSchedule:
        perms = getattr(actor, "permissions", None)
        perm_dict = {c.name: getattr(perms, c.name) for c in perms.__table__.columns} if perms else None
        if not has_permission(actor.role, "can_edit_meds", perm_dict):
            raise ForbiddenError("You do not have permission to configure medication schedules.")

        med = await self.get_medication(medication_id)

        # Deactivate existing schedule and link supersedes_id
        active = await self.schedule_repo.get_active_for_medication(medication_id)
        supersedes_id = None
        if active:
            await self.schedule_repo.deactivate(active.id)
            supersedes_id = active.id

        data["supersedes_id"] = supersedes_id
        schedule = await self.schedule_repo.create(medication_id, data)

        # Regenerate upcoming events for next 7 days
        sched_service = ScheduleService(self.db, self.circle_id)
        await sched_service.regenerate_events_for_schedule(schedule, med.recipient_id)

        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="schedule_created",
            entity_type="medication_schedule",
            entity_id=schedule.id,
            after={"kind": schedule.kind.value, "supersedes_id": str(supersedes_id) if supersedes_id else None},
        )
        await self.db.commit()
        return schedule
