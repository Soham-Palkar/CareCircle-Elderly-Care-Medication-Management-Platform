"""Adherence statistics and streaks router."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db
from app.core.errors import NotFoundError
from app.models.member import Member
from app.models.recipient import CareRecipient
from app.schemas.dose import AdherenceSummaryOut, StreakOut
from app.services.adherence_service import AdherenceService
from app.services.streak_service import StreakService

router = APIRouter(tags=["adherence"])


async def _get_recipient_id_for_circle(db: AsyncSession, circle_id: UUID) -> UUID:
    res = await db.execute(select(CareRecipient.id).where(CareRecipient.circle_id == circle_id))
    r_id = res.scalar_one_or_none()
    if not r_id:
        raise NotFoundError("Care recipient not configured for this circle.")
    return r_id


@router.get("/adherence/summary", response_model=AdherenceSummaryOut)
async def get_adherence_summary(
    range_days: int = Query(default=7, alias="range"),
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> AdherenceSummaryOut:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = AdherenceService(db, current_member.circle_id)
    summary = await svc.get_summary(recipient_id, days=range_days)
    return AdherenceSummaryOut(**summary)


@router.get("/streaks", response_model=StreakOut)
async def get_streaks(
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> StreakOut:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = StreakService(db, current_member.circle_id)
    streak = await svc.get_streak(recipient_id)
    return StreakOut(
        recipient_id=streak.recipient_id,
        current_streak=streak.current_streak,
        best_streak=streak.best_streak,
        last_date=streak.last_date,
    )
