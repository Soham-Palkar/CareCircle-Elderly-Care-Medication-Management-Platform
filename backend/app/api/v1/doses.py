"""Dose lifecycle router."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db
from app.core.errors import NotFoundError
from app.models.member import Member
from app.models.recipient import CareRecipient
from app.schemas.dose import DoseEventOut, NextDoseOut, SkipRequest, SnoozeRequest, TakenRequest
from app.schemas.medication import MedicationOut
from app.services.dose_service import DoseService

router = APIRouter(prefix="/doses", tags=["doses"])


async def _get_recipient_id_for_circle(db: AsyncSession, circle_id: UUID) -> UUID:
    res = await db.execute(select(CareRecipient.id).where(CareRecipient.circle_id == circle_id))
    r_id = res.scalar_one_or_none()
    if not r_id:
        raise NotFoundError("Care recipient not configured for this circle.")
    return r_id


@router.get("", response_model=list[DoseEventOut])
async def list_doses(
    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> list[DoseEventOut]:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    now = datetime.now(timezone.utc)
    from_dt = from_date or (now - timedelta(days=1))
    to_dt = to_date or (now + timedelta(days=1))

    svc = DoseService(db, current_member.circle_id)
    events = await svc.list_doses(recipient_id, from_dt, to_dt)
    return [
        DoseEventOut(
            id=d.id,
            schedule_id=d.schedule_id,
            medication_id=d.medication_id,
            medication_name=d.medication.name if d.medication else None,
            scheduled_at=d.scheduled_at,
            state=d.state.value,
            escalation_level=d.escalation_level,
            snooze_until=d.snooze_until,
            taken_at=d.taken_at,
            recorded_by=d.recorded_by,
            recorded_via=d.recorded_via.value,
            skip_reason=d.skip_reason,
        )
        for d in events
    ]


@router.get("/next", response_model=NextDoseOut)
async def get_next_dose(
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> NextDoseOut:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = DoseService(db, current_member.circle_id)
    next_due = await svc.get_next_dose(recipient_id)

    if not next_due or not next_due.medication:
        return NextDoseOut(
            dose=None,
            medication=None,
            message="All scheduled medications taken for now. Great job!",
        )

    med = next_due.medication
    time_str = next_due.scheduled_at.strftime("%I:%M %p")
    return NextDoseOut(
        dose=DoseEventOut(
            id=next_due.id,
            schedule_id=next_due.schedule_id,
            medication_id=next_due.medication_id,
            medication_name=med.name,
            scheduled_at=next_due.scheduled_at,
            state=next_due.state.value,
            escalation_level=next_due.escalation_level,
            snooze_until=next_due.snooze_until,
            taken_at=next_due.taken_at,
            recorded_by=next_due.recorded_by,
            recorded_via=next_due.recorded_via.value,
            skip_reason=next_due.skip_reason,
        ),
        medication=MedicationOut(
            id=med.id,
            recipient_id=med.recipient_id,
            name=med.name,
            strength=med.strength,
            form=med.form,
            instructions=med.instructions,
            purpose_card=med.purpose_card or {},
            criticality=med.criticality.value,
            dose_quantity=med.dose_quantity,
            stock_count=med.stock_count,
            refill_threshold_days=med.refill_threshold_days,
            status=med.status.value,
            source=med.source.value,
            confirmed_with_doctor=med.confirmed_with_doctor,
            created_at=med.created_at,
            updated_at=med.updated_at,
        ),
        message=f"Time for your {med.name} ({med.strength}) scheduled for {time_str}.",
    )


@router.post("/{event_id}/taken", response_model=DoseEventOut)
async def mark_dose_taken(
    event_id: UUID,
    payload: TakenRequest,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> DoseEventOut:
    svc = DoseService(db, current_member.circle_id)
    dose = await svc.mark_taken(
        actor=current_member,
        event_id=event_id,
        via=payload.recorded_via,
        idempotency_key=payload.idempotency_key,
    )
    return DoseEventOut(
        id=dose.id,
        schedule_id=dose.schedule_id,
        medication_id=dose.medication_id,
        medication_name=dose.medication.name if dose.medication else None,
        scheduled_at=dose.scheduled_at,
        state=dose.state.value,
        escalation_level=dose.escalation_level,
        snooze_until=dose.snooze_until,
        taken_at=dose.taken_at,
        recorded_by=dose.recorded_by,
        recorded_via=dose.recorded_via.value,
        skip_reason=dose.skip_reason,
    )


@router.post("/{event_id}/snooze", response_model=DoseEventOut)
async def snooze_dose(
    event_id: UUID,
    payload: SnoozeRequest,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> DoseEventOut:
    svc = DoseService(db, current_member.circle_id)
    dose = await svc.snooze(
        actor=current_member,
        event_id=event_id,
        snooze_minutes=payload.snooze_minutes,
        idempotency_key=payload.idempotency_key,
    )
    return DoseEventOut(
        id=dose.id,
        schedule_id=dose.schedule_id,
        medication_id=dose.medication_id,
        medication_name=dose.medication.name if dose.medication else None,
        scheduled_at=dose.scheduled_at,
        state=dose.state.value,
        escalation_level=dose.escalation_level,
        snooze_until=dose.snooze_until,
        taken_at=dose.taken_at,
        recorded_by=dose.recorded_by,
        recorded_via=dose.recorded_via.value,
        skip_reason=dose.skip_reason,
    )


@router.post("/{event_id}/skip", response_model=DoseEventOut)
async def skip_dose(
    event_id: UUID,
    payload: SkipRequest,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> DoseEventOut:
    svc = DoseService(db, current_member.circle_id)
    dose = await svc.skip(
        actor=current_member,
        event_id=event_id,
        reason=payload.reason,
        idempotency_key=payload.idempotency_key,
    )
    return DoseEventOut(
        id=dose.id,
        schedule_id=dose.schedule_id,
        medication_id=dose.medication_id,
        medication_name=dose.medication.name if dose.medication else None,
        scheduled_at=dose.scheduled_at,
        state=dose.state.value,
        escalation_level=dose.escalation_level,
        snooze_until=dose.snooze_until,
        taken_at=dose.taken_at,
        recorded_by=dose.recorded_by,
        recorded_via=dose.recorded_via.value,
        skip_reason=dose.skip_reason,
    )
