"""Notifications router."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db
from app.models.member import Member
from app.schemas.notification import NotificationOut
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
async def list_notifications(
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> list[NotificationOut]:
    svc = NotificationService(db, current_member.circle_id)
    items = await svc.list_for_member(current_member.id)
    return [
        NotificationOut(
            id=n.id,
            member_id=n.member_id,
            circle_id=n.circle_id,
            channel=n.channel.value,
            type=n.type.value,
            status=n.status.value,
            attempts=n.attempts,
            sent_at=n.sent_at,
            created_at=n.created_at,
        )
        for n in items
    ]
