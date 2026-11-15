"""Signed action token service for one-tap email action links."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_action_token, verify_action_token
from app.models.member import Member
from app.services.dose_service import DoseService


class ActionTokenService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id

    def generate_token(self, dose_event_id: UUID, member_id: UUID, action: str = "taken") -> str:
        return create_action_token(dose_event_id, action, member_id)

    async def execute_token(self, token: str) -> dict:
        payload = verify_action_token(token)
        dose_event_id = UUID(payload["dose_event_id"])
        member_id = UUID(payload["member_id"])
        action = payload["action"]

        if action == "taken":
            # Fetch member for actor context
            from app.repositories.member_repo import MemberRepository

            m_repo = MemberRepository(self.db, self.circle_id)
            member = await m_repo.get_by_id(member_id)
            if not member:
                raise ValueError("Authorized member for this token no longer exists.")

            dose_svc = DoseService(self.db, self.circle_id)
            dose = await dose_svc.mark_taken(
                actor=member,
                event_id=dose_event_id,
                via="email_link",
                idempotency_key=f"email_action_{token[:20]}",
            )
            return {"status": "success", "action": "taken", "dose_id": str(dose.id)}

        return {"status": "unsupported_action"}
