"""One-tap email action link router."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.core.security import verify_action_token
from app.models.dose_event import DoseEvent
from app.models.recipient import CareRecipient
from app.schemas.common import MessageResponse
from app.services.action_token_service import ActionTokenService

router = APIRouter(prefix="/actions", tags=["actions"])


@router.get("/{token}")
async def inspect_action_token(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    payload = verify_action_token(token)
    return {
        "status": "valid",
        "action": payload.get("action"),
        "dose_event_id": payload.get("dose_event_id"),
        "expires_in_seconds": payload.get("exp", 0) - int(payload.get("iat", 0)),
    }


@router.post("/{token}", response_model=MessageResponse)
async def execute_action_token(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    payload = verify_action_token(token)
    from uuid import UUID
    dose_id = UUID(payload["dose_event_id"])

    # Find circle_id for this dose
    stmt = (
        select(CareRecipient.circle_id)
        .join(DoseEvent, DoseEvent.recipient_id == CareRecipient.id)
        .where(DoseEvent.id == dose_id)
    )
    res = await db.execute(stmt)
    circle_id = res.scalar_one_or_none()
    if not circle_id:
        raise ValueError("Dose event circle could not be verified.")

    svc = ActionTokenService(db, circle_id)
    res_data = await svc.execute_token(token)
    return MessageResponse(message=f"Dose successfully marked as taken via email link.")
