"""Medications and schedules router."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db
from app.core.errors import NotFoundError
from app.models.member import Member
from app.models.recipient import CareRecipient
from app.schemas.common import MessageResponse
from app.schemas.medication import MedicationCreate, MedicationOut, MedicationUpdate, ScheduleCreate, ScheduleOut
from app.services.medication_service import MedicationService

router = APIRouter(prefix="/medications", tags=["medications"])


async def _get_recipient_id_for_circle(db: AsyncSession, circle_id: UUID) -> UUID:
    res = await db.execute(select(CareRecipient.id).where(CareRecipient.circle_id == circle_id))
    r_id = res.scalar_one_or_none()
    if not r_id:
        raise NotFoundError("Care recipient not configured for this circle.")
    return r_id


@router.get("", response_model=list[MedicationOut])
async def list_medications(
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> list[MedicationOut]:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = MedicationService(db, current_member.circle_id)
    meds = await svc.list_active(recipient_id)
    return [
        MedicationOut(
            id=m.id,
            recipient_id=m.recipient_id,
            name=m.name,
            strength=m.strength,
            form=m.form,
            instructions=m.instructions,
            purpose_card=m.purpose_card or {},
            criticality=m.criticality.value,
            dose_quantity=m.dose_quantity,
            stock_count=m.stock_count,
            refill_threshold_days=m.refill_threshold_days,
            status=m.status.value,
            source=m.source.value,
            confirmed_with_doctor=m.confirmed_with_doctor,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        for m in meds
    ]


@router.post("", response_model=MedicationOut)
async def create_medication(
    payload: MedicationCreate,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> MedicationOut:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = MedicationService(db, current_member.circle_id)
    med, advisory = await svc.create_medication(
        actor=current_member,
        recipient_id=recipient_id,
        data=payload.model_dump(),
    )
    return MedicationOut(
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
    )


@router.get("/{medication_id}", response_model=MedicationOut)
async def get_medication(
    medication_id: UUID,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> MedicationOut:
    svc = MedicationService(db, current_member.circle_id)
    med = await svc.get_medication(medication_id)
    return MedicationOut(
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
    )


@router.patch("/{medication_id}", response_model=MedicationOut)
async def update_medication(
    medication_id: UUID,
    payload: MedicationUpdate,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> MedicationOut:
    svc = MedicationService(db, current_member.circle_id)
    med = await svc.update_medication(
        actor=current_member,
        medication_id=medication_id,
        updates=payload.model_dump(exclude_unset=True),
    )
    return MedicationOut(
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
    )


@router.post("/{medication_id}/archive", response_model=MessageResponse)
async def archive_medication(
    medication_id: UUID,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    svc = MedicationService(db, current_member.circle_id)
    await svc.archive_medication(current_member, medication_id)
    return MessageResponse(message="Medication and associated schedules archived.")


@router.post("/{medication_id}/schedules", response_model=ScheduleOut)
async def create_schedule(
    medication_id: UUID,
    payload: ScheduleCreate,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> ScheduleOut:
    svc = MedicationService(db, current_member.circle_id)
    sched = await svc.create_schedule(current_member, medication_id, payload.model_dump())
    return ScheduleOut(
        id=sched.id,
        medication_id=sched.medication_id,
        kind=sched.kind.value,
        time_of_day=sched.time_of_day,
        anchor=sched.anchor,
        anchor_offset_min=sched.anchor_offset_min,
        days_of_week=sched.days_of_week,
        start_date=sched.start_date,
        end_date=sched.end_date,
        grace_minutes=sched.grace_minutes,
        is_active=sched.is_active,
        supersedes_id=sched.supersedes_id,
        created_at=sched.created_at,
    )
