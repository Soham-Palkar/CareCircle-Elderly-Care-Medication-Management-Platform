"""Messaging bridge router (Feature F7)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db
from app.models.member import Member
from app.schemas.common import MessageResponse
from app.services.member_service import MemberService
from app.services.messaging_service import MessagingService

router = APIRouter(prefix="/messaging", tags=["messaging"])


@router.post("/telegram/link", response_model=MessageResponse)
async def link_telegram(
    chat_id: int,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    svc = MemberService(db, current_member.circle_id)
    await svc.link_telegram(current_member.id, chat_id)
    return MessageResponse(message="Telegram account successfully linked.")


@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, Any]:
    payload = await request.json()
    svc = MessagingService(db)
    return await svc.handle_telegram_webhook(payload, x_telegram_bot_api_secret_token)
