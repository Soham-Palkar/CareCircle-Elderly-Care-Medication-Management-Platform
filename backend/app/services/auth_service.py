"""Authentication and circle management service."""

from __future__ import annotations

import random
import string
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import create_access_token, create_refresh_token, hash_passcode, verify_passcode
from app.domain.permissions import ROLE_DEFAULT_PERMISSIONS
from app.domain.types import Role
from app.models.circle import CareCircle
from app.models.invite import Invite
from app.models.member import Member
from app.models.permission import MemberPermission
from app.models.recipient import CareRecipient
from app.models.streak import Streak
from app.repositories.audit_repo import AuditRepository


def _generate_circle_code() -> str:
    letters = "".join(random.choices(string.ascii_uppercase, k=4))
    digits = "".join(random.choices(string.digits, k=4))
    return f"{letters}-{digits}"


def _generate_invite_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.audit_repo = AuditRepository(db)

    async def create_circle(
        self,
        circle_name: str,
        elder_name: str,
        passcode: str,
    ) -> tuple[CareCircle, Member, CareRecipient]:
        # 1. Create circle
        code = _generate_circle_code()
        circle = CareCircle(name=circle_name, circle_code=code)
        self.db.add(circle)
        await self.db.flush()

        # 2. Create recipient (the elder)
        recipient = CareRecipient(circle_id=circle.id, full_name=elder_name)
        self.db.add(recipient)
        await self.db.flush()

        # 3. Create initial streak
        streak = Streak(recipient_id=recipient.id, current_streak=0, best_streak=0)
        self.db.add(streak)

        # 4. Create primary member (elder)
        passcode_hash = hash_passcode(passcode)
        member = Member(
            circle_id=circle.id,
            display_name=elder_name,
            role=Role.elder,
            passcode_hash=passcode_hash,
        )
        self.db.add(member)
        await self.db.flush()

        # 5. Grant maximal permissions to the elder
        defaults = ROLE_DEFAULT_PERMISSIONS[Role.elder]
        perm = MemberPermission(member_id=member.id, **defaults)
        self.db.add(perm)

        # 6. Audit log
        await self.audit_repo.log(
            circle_id=circle.id,
            actor_member_id=member.id,
            action="circle_created",
            entity_type="care_circle",
            entity_id=circle.id,
            after={"circle_name": circle_name, "elder_name": elder_name},
        )

        await self.db.commit()
        return circle, member, recipient

    async def login(
        self,
        circle_code: str,
        passcode: str,
        ip: str | None = None,
    ) -> tuple[Member, str, str, str]:
        """Authenticate with circle_code and passcode.

        Returns (member, access_token, refresh_token, circle_name).
        """
        stmt = select(CareCircle).where(CareCircle.circle_code == circle_code.strip().upper())
        res = await self.db.execute(stmt)
        circle = res.scalar_one_or_none()

        if not circle:
            raise UnauthorizedError("Incorrect circle code or passcode.")

        # Find active members in this circle
        m_stmt = select(Member).where(Member.circle_id == circle.id, Member.is_active.is_(True))
        m_res = await self.db.execute(m_stmt)
        members = list(m_res.scalars().all())

        now = datetime.now(timezone.utc)
        matched_member: Member | None = None

        for member in members:
            # Check lockout
            if member.locked_until and member.locked_until > now:
                raise UnauthorizedError("Account is temporarily locked. Please try again later.")

            if verify_passcode(passcode, member.passcode_hash):
                matched_member = member
                break

        if not matched_member:
            # Failed attempt on circle
            if members:
                # Increment failed attempts on the primary elder account
                members[0].failed_attempts += 1
                if members[0].failed_attempts >= 5:
                    members[0].locked_until = now + timedelta(minutes=15)
                await self.db.commit()
            raise UnauthorizedError("Incorrect circle code or passcode.")

        # Reset failed attempts on success
        matched_member.failed_attempts = 0
        matched_member.locked_until = None

        access_token = create_access_token(
            member_id=matched_member.id,
            circle_id=circle.id,
            role=matched_member.role.value,
        )
        refresh_token = create_refresh_token(member_id=matched_member.id)

        await self.audit_repo.log(
            circle_id=circle.id,
            actor_member_id=matched_member.id,
            action="login_success",
            entity_type="member",
            entity_id=matched_member.id,
            ip=ip,
        )
        await self.db.commit()

        return matched_member, access_token, refresh_token, circle.name

    async def create_invite(
        self,
        circle_id: UUID,
        created_by_id: UUID,
        role: str,
        expires_hours: int = 48,
    ) -> tuple[Invite, str]:
        raw_code = _generate_invite_code()
        hashed = hash_passcode(raw_code)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)

        invite = Invite(
            circle_id=circle_id,
            role=Role(role),
            code_hash=hashed,
            expires_at=expires_at,
            created_by=created_by_id,
        )
        self.db.add(invite)
        await self.audit_repo.log(
            circle_id=circle_id,
            actor_member_id=created_by_id,
            action="invite_created",
            entity_type="invite",
            entity_id=invite.id,
            after={"role": role, "expires_hours": expires_hours},
        )
        await self.db.commit()
        return invite, raw_code

    async def redeem_invite(
        self,
        raw_code: str,
        display_name: str,
        email: str | None,
        passcode: str,
        ip: str | None = None,
    ) -> tuple[Member, str, str]:
        now = datetime.now(timezone.utc)
        stmt = select(Invite).where(Invite.used_at.is_(None), Invite.expires_at > now)
        res = await self.db.execute(stmt)
        invites = list(res.scalars().all())

        matched_invite: Invite | None = None
        for inv in invites:
            if verify_passcode(raw_code.strip(), inv.code_hash):
                matched_invite = inv
                break

        if not matched_invite:
            raise NotFoundError("Invite code is invalid, expired, or already redeemed.")

        passcode_hash = hash_passcode(passcode)
        member = Member(
            circle_id=matched_invite.circle_id,
            display_name=display_name,
            role=matched_invite.role,
            passcode_hash=passcode_hash,
            email=email,
        )
        self.db.add(member)
        await self.db.flush()

        # Set default permissions based on role
        defaults = ROLE_DEFAULT_PERMISSIONS.get(matched_invite.role, {})
        perm = MemberPermission(member_id=member.id, **defaults)
        self.db.add(perm)

        matched_invite.used_at = now

        access_token = create_access_token(
            member_id=member.id,
            circle_id=matched_invite.circle_id,
            role=member.role.value,
        )
        refresh_token = create_refresh_token(member_id=member.id)

        await self.audit_repo.log(
            circle_id=matched_invite.circle_id,
            actor_member_id=member.id,
            action="invite_redeemed",
            entity_type="member",
            entity_id=member.id,
            ip=ip,
        )
        await self.db.commit()

        return member, access_token, refresh_token
