"""Risk flags repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.recipient import CareRecipient
from app.models.risk_flag import RiskFlag, RiskFlagStatus
from app.repositories.base import BaseRepository


class FlagRepository(BaseRepository):

    async def create(self, recipient_id: UUID, data: dict) -> RiskFlag:
        flag = RiskFlag(recipient_id=recipient_id, **data)
        self.db.add(flag)
        await self.db.flush()
        return flag

    async def get_open_flags(self, recipient_id: UUID) -> list[RiskFlag]:
        stmt = (
            select(RiskFlag)
            .join(CareRecipient, RiskFlag.recipient_id == CareRecipient.id)
            .where(
                RiskFlag.recipient_id == recipient_id,
                RiskFlag.status.in_([RiskFlagStatus.open, RiskFlagStatus.acknowledged]),
                CareRecipient.circle_id == self.circle_id,
            )
            .order_by(RiskFlag.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def acknowledge(self, flag_id: UUID) -> RiskFlag | None:
        stmt = (
            select(RiskFlag)
            .join(CareRecipient, RiskFlag.recipient_id == CareRecipient.id)
            .where(
                RiskFlag.id == flag_id,
                CareRecipient.circle_id == self.circle_id,
            )
        )
        res = await self.db.execute(stmt)
        flag = res.scalar_one_or_none()
        if flag:
            flag.status = RiskFlagStatus.acknowledged
            await self.db.flush()
        return flag

    async def resolve(self, flag_id: UUID) -> RiskFlag | None:
        stmt = (
            select(RiskFlag)
            .join(CareRecipient, RiskFlag.recipient_id == CareRecipient.id)
            .where(
                RiskFlag.id == flag_id,
                CareRecipient.circle_id == self.circle_id,
            )
        )
        res = await self.db.execute(stmt)
        flag = res.scalar_one_or_none()
        if flag:
            flag.status = RiskFlagStatus.resolved
            await self.db.flush()
        return flag

    async def exists_open(self, recipient_id: UUID, rule_code: str) -> bool:
        stmt = (
            select(RiskFlag)
            .join(CareRecipient, RiskFlag.recipient_id == CareRecipient.id)
            .where(
                RiskFlag.recipient_id == recipient_id,
                RiskFlag.rule_code == rule_code,
                RiskFlag.status == RiskFlagStatus.open,
                CareRecipient.circle_id == self.circle_id,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none() is not None
