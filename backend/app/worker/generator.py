"""Worker job: Pre-materialize next 7 days of dose events."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipient import CareRecipient
from app.services.schedule_service import ScheduleService


async def generate_upcoming_doses(db: AsyncSession, days_ahead: int = 7) -> int:
    """Scan all active care recipients and materialize next N days of dose events."""
    stmt = select(CareRecipient)
    res = await db.execute(stmt)
    recipients = list(res.scalars().all())

    total_created = 0
    for r in recipients:
        svc = ScheduleService(db, r.circle_id)
        created = await svc.regenerate_all_for_recipient(r.id, days_ahead=days_ahead)
        total_created += created

    await db.commit()
    return total_created
