"""Worker job: Periodic Digital Twin explainable rule engine evaluation."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipient import CareRecipient
from app.services.twin_service import TwinService


async def run_periodic_twin_rules(db: AsyncSession) -> int:
    stmt = select(CareRecipient)
    recipients = list((await db.execute(stmt)).scalars().all())

    total_flags = 0
    for r in recipients:
        twin_svc = TwinService(db, r.circle_id)
        flags = await twin_svc.evaluate_rules(r.id)
        total_flags += len(flags)

    return total_flags
