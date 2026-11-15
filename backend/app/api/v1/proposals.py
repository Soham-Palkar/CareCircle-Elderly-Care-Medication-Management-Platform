"""Schedule proposals router."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db, require_elder
from app.core.errors import NotFoundError
from app.models.member import Member
from app.models.recipient import CareRecipient
from app.schemas.twin import ProposalCreate, ProposalDecision, ProposalOut
from app.services.proposal_service import ProposalService

router = APIRouter(prefix="/proposals", tags=["proposals"])


async def _get_recipient_id_for_circle(db: AsyncSession, circle_id: UUID) -> UUID:
    res = await db.execute(select(CareRecipient.id).where(CareRecipient.circle_id == circle_id))
    r_id = res.scalar_one_or_none()
    if not r_id:
        raise NotFoundError("Care recipient not configured for this circle.")
    return r_id


@router.get("", response_model=list[ProposalOut])
async def list_proposals(
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> list[ProposalOut]:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = ProposalService(db, current_member.circle_id)
    items = await svc.list_proposals(recipient_id)
    return [
        ProposalOut(
            id=p.id,
            medication_id=p.medication_id,
            proposed_by=p.proposed_by,
            change=p.change,
            rationale=p.rationale,
            status=p.status.value,
            decided_by=p.decided_by,
            decided_at=p.decided_at,
            created_at=p.created_at,
        )
        for p in items
    ]


@router.post("", response_model=ProposalOut)
async def create_proposal(
    payload: ProposalCreate,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> ProposalOut:
    svc = ProposalService(db, current_member.circle_id)
    p = await svc.create_proposal(
        actor=current_member,
        medication_id=payload.medication_id,
        change=payload.change,
        rationale=payload.rationale,
    )
    return ProposalOut(
        id=p.id,
        medication_id=p.medication_id,
        proposed_by=p.proposed_by,
        change=p.change,
        rationale=p.rationale,
        status=p.status.value,
        decided_by=p.decided_by,
        decided_at=p.decided_at,
        created_at=p.created_at,
    )


@router.post("/{proposal_id}/decide", response_model=ProposalOut)
async def decide_proposal(
    proposal_id: UUID,
    payload: ProposalDecision,
    elder: Member = Depends(require_elder),
    db: AsyncSession = Depends(get_db),
) -> ProposalOut:
    svc = ProposalService(db, elder.circle_id)
    p = await svc.decide_proposal(
        actor=elder,
        proposal_id=proposal_id,
        decision=payload.decision,
    )
    return ProposalOut(
        id=p.id,
        medication_id=p.medication_id,
        proposed_by=p.proposed_by,
        change=p.change,
        rationale=p.rationale,
        status=p.status.value,
        decided_by=p.decided_by,
        decided_at=p.decided_at,
        created_at=p.created_at,
    )
