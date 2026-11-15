"""Schedule proposal service (what-if proposals requiring elder approval)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, NotFoundError
from app.domain.permissions import can_approve_proposal
from app.models.member import Member
from app.models.proposal import ProposalStatus, ScheduleProposal
from app.repositories.audit_repo import AuditRepository
from app.repositories.proposal_repo import ProposalRepository
from app.services.medication_service import MedicationService


class ProposalService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.prop_repo = ProposalRepository(db, circle_id)
        self.audit_repo = AuditRepository(db)

    async def create_proposal(
        self,
        actor: Member,
        medication_id: UUID,
        change: dict[str, Any],
        rationale: str,
    ) -> ScheduleProposal:
        proposal = await self.prop_repo.create(
            medication_id=medication_id,
            data={"change": change, "rationale": rationale, "status": ProposalStatus.pending},
            proposed_by=actor.id,
        )
        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="proposal_created",
            entity_type="schedule_proposal",
            entity_id=proposal.id,
            after={"rationale": rationale},
        )
        await self.db.commit()
        return proposal

    async def list_proposals(self, recipient_id: UUID) -> list[ScheduleProposal]:
        return await self.prop_repo.list_for_recipient(recipient_id)

    async def decide_proposal(
        self,
        actor: Member,
        proposal_id: UUID,
        decision: str,  # "approved" or "rejected"
    ) -> ScheduleProposal:
        if not can_approve_proposal(actor.role):
            raise ForbiddenError("Only the elder has final say on schedule proposals.")

        status = ProposalStatus.approved if decision == "approved" else ProposalStatus.rejected
        proposal = await self.prop_repo.decide(proposal_id, status, actor.id)
        if not proposal:
            raise NotFoundError("Proposal not found.")

        # If approved, apply the schedule change
        if status == ProposalStatus.approved:
            med_svc = MedicationService(self.db, self.circle_id)
            await med_svc.create_schedule(actor, proposal.medication_id, proposal.change)

        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action=f"proposal_{decision}",
            entity_type="schedule_proposal",
            entity_id=proposal.id,
        )
        await self.db.commit()
        return proposal
