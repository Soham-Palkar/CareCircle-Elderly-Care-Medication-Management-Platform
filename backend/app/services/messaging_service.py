"""Messaging bridge service (Feature F7 - Telegram / WhatsApp integration).

Inbound webhook security:
- Validates configured secret token header.
- Maps reply digits: '1' -> taken, '2' -> snooze, '3' -> skip.
- Routes through standard DoseService and writes complete audit history.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import UnauthorizedError
from app.models.recipient import CareRecipient
from app.repositories.member_repo import MemberRepository
from app.services.dose_service import DoseService


class MessagingService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = get_settings()

    async def handle_telegram_webhook(
        self,
        payload: dict[str, Any],
        secret_header: str | None,
    ) -> dict[str, str]:
        # 1. Verify secret token if configured
        expected_secret = self.settings.telegram_webhook_secret
        if expected_secret and secret_header != expected_secret:
            raise UnauthorizedError("Invalid or missing webhook secret header.")

        message = payload.get("message", {})
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = str(message.get("text", "")).strip()

        if not chat_id or not text:
            return {"status": "ignored"}

        # 2. Find member by telegram_chat_id
        # Temporary MemberRepository without circle_id for cross-circle lookup
        m_repo = MemberRepository(self.db, circle_id=UUID(int=0))
        member = await m_repo.find_by_telegram_chat_id(chat_id)

        if not member:
            return {"status": "unlinked_chat"}

        # 3. Find the recipient associated with this circle
        from sqlalchemy import select
        res = await self.db.execute(select(CareRecipient).where(CareRecipient.circle_id == member.circle_id))
        recipient = res.scalar_one_or_none()
        if not recipient:
            return {"status": "no_recipient"}

        dose_svc = DoseService(self.db, member.circle_id)
        next_due = await dose_svc.get_next_dose(recipient.id)

        if not next_due:
            return {"status": "no_pending_doses"}

        # 4. Map replies
        if text in ("1", "taken", "Taken", "done"):
            await dose_svc.mark_taken(actor=member, event_id=next_due.id, via="telegram")
            return {"status": "recorded_taken", "dose_id": str(next_due.id)}
        elif text in ("2", "later", "snooze"):
            await dose_svc.snooze(actor=member, event_id=next_due.id, snooze_minutes=15)
            return {"status": "recorded_snooze", "dose_id": str(next_due.id)}
        elif text in ("3", "skip"):
            await dose_svc.skip(actor=member, event_id=next_due.id, reason="Skipped via Telegram reply")
            return {"status": "recorded_skip", "dose_id": str(next_due.id)}

        return {"status": "unrecognized_command"}
