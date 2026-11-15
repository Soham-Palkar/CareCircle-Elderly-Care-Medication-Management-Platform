"""Voice coordinator router (Feature F4)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db
from app.core.errors import NotFoundError
from app.models.member import Member
from app.models.recipient import CareRecipient
from app.schemas.voice import VoiceIntentRequest, VoiceIntentResponse
from app.services.voice_service import VoiceService

router = APIRouter(prefix="/voice", tags=["voice"])


async def _get_recipient_id_for_circle(db: AsyncSession, circle_id: UUID) -> UUID:
    res = await db.execute(select(CareRecipient.id).where(CareRecipient.circle_id == circle_id))
    r_id = res.scalar_one_or_none()
    if not r_id:
        raise NotFoundError("Care recipient not configured for this circle.")
    return r_id


@router.post("/intent", response_model=VoiceIntentResponse)
async def process_voice_intent(
    payload: VoiceIntentRequest,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> VoiceIntentResponse:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = VoiceService(db, current_member.circle_id)
    res = await svc.handle_intent(
        actor=current_member,
        recipient_id=recipient_id,
        text=payload.text,
        language=payload.language,
        dose_event_id=payload.dose_event_id,
    )
    return VoiceIntentResponse(**res)
