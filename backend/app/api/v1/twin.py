"""Digital Twin Guardian router (Feature F1)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db
from app.core.errors import NotFoundError
from app.models.member import Member
from app.models.recipient import CareRecipient
from app.schemas.twin import ForecastSlotOut, HealthReadingCreate, HealthReadingOut, RiskFlagOut, TwinProfileOut
from app.services.twin_service import TwinService

router = APIRouter(prefix="/twin", tags=["twin"])


async def _get_recipient_id_for_circle(db: AsyncSession, circle_id: UUID) -> UUID:
    res = await db.execute(select(CareRecipient.id).where(CareRecipient.circle_id == circle_id))
    r_id = res.scalar_one_or_none()
    if not r_id:
        raise NotFoundError("Care recipient not configured for this circle.")
    return r_id


@router.get("/profile", response_model=TwinProfileOut)
async def get_twin_profile(
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> TwinProfileOut:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = TwinService(db, current_member.circle_id)
    profile = await svc.get_profile(recipient_id)
    return TwinProfileOut(**profile)


@router.get("/flags", response_model=list[RiskFlagOut])
async def list_open_flags(
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> list[RiskFlagOut]:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = TwinService(db, current_member.circle_id)
    # Trigger dynamic rule evaluation first
    await svc.evaluate_rules(recipient_id)
    flags = await svc.flag_repo.get_open_flags(recipient_id)
    return [
        RiskFlagOut(
            id=f.id,
            recipient_id=f.recipient_id,
            rule_code=f.rule_code,
            severity=f.severity.value,
            message=f.message,
            evidence=f.evidence,
            status=f.status.value,
            created_at=f.created_at,
        )
        for f in flags
    ]


@router.get("/forecast", response_model=list[ForecastSlotOut])
async def get_miss_risk_forecast(
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> list[ForecastSlotOut]:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = TwinService(db, current_member.circle_id)
    forecast = await svc.get_forecast(recipient_id)
    return [ForecastSlotOut(**slot) for slot in forecast]


@router.post("/readings", response_model=HealthReadingOut)
async def record_health_reading(
    payload: HealthReadingCreate,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> HealthReadingOut:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = TwinService(db, current_member.circle_id)
    reading = await svc.record_reading(
        recipient_id=recipient_id,
        kind=payload.kind,
        value=float(payload.value),
        source=payload.source,
        recorded_at=payload.recorded_at,
    )
    return HealthReadingOut(
        id=reading.id,
        recipient_id=reading.recipient_id,
        kind=reading.kind.value,
        value=reading.value,
        recorded_at=reading.recorded_at,
        source=reading.source.value,
    )
