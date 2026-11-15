"""Schedule proposal repository."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from app.models.medication import Medication
from app.models.proposal import ProposalStatus, ScheduleProposal
from app.models.recipient import CareRecipient
from app.repositories.base import BaseRepository


class ProposalRepository(BaseRepository):

    async def create(self, medication_id: UUID, data: dict, proposed_by: UUID | None) -> ScheduleProposal:
        proposal = ScheduleProposal(
            medication_id=medication_id,
            proposed_by=proposed_by,
            **data,
        )
        self.db.add(proposal)
        await self.db.flush()
        return proposal

    async def get_by_id(self, proposal_id: UUID) -> ScheduleProposal | None:
        stmt = (
            select(ScheduleProposal)
            .join(Medication, ScheduleProposal.medication_id == Medication.id)
            .join(CareRecipient, Medication.recipient_id == CareRecipient.id)
            .where(
                ScheduleProposal.id == proposal_id,
                CareRecipient.circle_id == self.circle_id,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_for_recipient(self, recipient_id: UUID) -> list[ScheduleProposal]:
        stmt = (
            select(ScheduleProposal)
            .join(Medication, ScheduleProposal.medication_id == Medication.id)
            .join(CareRecipient, Medication.recipient_id == CareRecipient.id)
            .where(
                Medication.recipient_id == recipient_id,
                CareRecipient.circle_id == self.circle_id,
            )
            .order_by(ScheduleProposal.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def decide(self, proposal_id: UUID, status: ProposalStatus, decided_by: UUID) -> ScheduleProposal | None:
        proposal = await self.get_by_id(proposal_id)
        if proposal:
            proposal.status = status
            proposal.decided_by = decided_by
            proposal.decided_at = datetime.now(timezone.utc)
            await self.db.flush()
        return proposal
