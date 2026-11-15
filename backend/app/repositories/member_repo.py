"""Member repository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.member import Member
from app.models.permission import MemberPermission
from app.repositories.base import BaseRepository


class MemberRepository(BaseRepository):

    async def get_by_id(self, member_id: UUID) -> Member | None:
        stmt = (
            select(Member)
            .where(Member.id == member_id, Member.circle_id == self.circle_id)
            .options(selectinload(Member.permissions))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_circle(self) -> list[Member]:
        stmt = (
            select(Member)
            .where(Member.circle_id == self.circle_id)
            .options(selectinload(Member.permissions))
            .order_by(Member.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_permission(self, member_id: UUID) -> MemberPermission | None:
        stmt = select(MemberPermission).join(Member).where(
            MemberPermission.member_id == member_id,
            Member.circle_id == self.circle_id,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_permission(self, member_id: UUID, updates: dict) -> MemberPermission | None:
        perm = await self.get_permission(member_id)
        if not perm:
            return None
        for k, v in updates.items():
            if hasattr(perm, k) and v is not None:
                setattr(perm, k, v)
        await self.db.flush()
        return perm

    async def deactivate(self, member_id: UUID) -> Member | None:
        member = await self.get_by_id(member_id)
        if member:
            member.is_active = False
            await self.db.flush()
        return member

    async def increment_failed_attempts(self, member_id: UUID) -> int:
        member = await self.get_by_id(member_id)
        if member:
            member.failed_attempts += 1
            await self.db.flush()
            return member.failed_attempts
        return 0

    async def lock_member(self, member_id: UUID, until: datetime) -> None:
        member = await self.get_by_id(member_id)
        if member:
            member.locked_until = until
            await self.db.flush()

    async def reset_failed_attempts(self, member_id: UUID) -> None:
        member = await self.get_by_id(member_id)
        if member:
            member.failed_attempts = 0
            member.locked_until = None
            await self.db.flush()

    async def update_telegram_chat_id(self, member_id: UUID, chat_id: int) -> None:
        member = await self.get_by_id(member_id)
        if member:
            member.telegram_chat_id = chat_id
            await self.db.flush()

    async def find_by_telegram_chat_id(self, chat_id: int) -> Member | None:
        # Cross-circle search for incoming webhook telegram chat_id
        stmt = select(Member).where(Member.telegram_chat_id == chat_id, Member.is_active.is_(True))
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_notify_prefs(self, member_id: UUID, prefs: dict) -> None:
        member = await self.get_by_id(member_id)
        if member:
            current = dict(member.notify_prefs or {})
            current.update(prefs)
            member.notify_prefs = current
            await self.db.flush()
