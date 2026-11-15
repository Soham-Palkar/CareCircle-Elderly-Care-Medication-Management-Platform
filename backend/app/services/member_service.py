"""Member management and permission services."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, NotFoundError
from app.domain.permissions import can_manage_member
from app.domain.types import Role
from app.models.member import Member
from app.models.permission import MemberPermission
from app.repositories.audit_repo import AuditRepository
from app.repositories.member_repo import MemberRepository


class MemberService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.member_repo = MemberRepository(db, circle_id)
        self.audit_repo = AuditRepository(db)

    async def list_members(self) -> list[Member]:
        return await self.member_repo.get_by_circle()

    async def get_member(self, member_id: UUID) -> Member:
        member = await self.member_repo.get_by_id(member_id)
        if not member:
            raise NotFoundError("Member not found in this circle.")
        return member

    async def update_permissions(
        self,
        actor: Member,
        target_member_id: UUID,
        updates: dict[str, Any],
    ) -> MemberPermission:
        if actor.role != Role.elder:
            raise ForbiddenError("Only the elder can grant or revoke member permissions.")

        target = await self.member_repo.get_by_id(target_member_id)
        if not target:
            raise NotFoundError("Target member not found in this circle.")

        if target.role == Role.elder:
            raise ForbiddenError("Elder permissions cannot be altered.")

        current_perm = await self.member_repo.get_permission(target_member_id)
        before_dict = {
            k: getattr(current_perm, k) for k in updates if current_perm and hasattr(current_perm, k)
        }

        updated = await self.member_repo.update_permission(target_member_id, updates)
        if not updated:
            raise NotFoundError("Permissions record not found.")

        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="permissions_updated",
            entity_type="member_permission",
            entity_id=target_member_id,
            before=before_dict,
            after=updates,
        )
        await self.db.commit()
        return updated

    async def deactivate_member(self, actor: Member, target_member_id: UUID) -> Member:
        target = await self.member_repo.get_by_id(target_member_id)
        if not target:
            raise NotFoundError("Member not found.")

        if not can_manage_member(actor.role, target.role) or actor.id == target.id:
            raise ForbiddenError("You do not have permission to deactivate this member.")

        deactivated = await self.member_repo.deactivate(target_member_id)
        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="member_deactivated",
            entity_type="member",
            entity_id=target_member_id,
        )
        await self.db.commit()
        return deactivated or target

    async def update_notify_prefs(self, member_id: UUID, prefs: dict[str, Any]) -> None:
        await self.member_repo.update_notify_prefs(member_id, prefs)
        await self.db.commit()

    async def link_telegram(self, member_id: UUID, chat_id: int) -> None:
        await self.member_repo.update_telegram_chat_id(member_id, chat_id)
        await self.db.commit()
