"""Appointments router."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db
from app.core.errors import NotFoundError
from app.models.member import Member
from app.models.recipient import CareRecipient
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentUpdate
from app.schemas.common import MessageResponse
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])


async def _get_recipient_id_for_circle(db: AsyncSession, circle_id: UUID) -> UUID:
    res = await db.execute(select(CareRecipient.id).where(CareRecipient.circle_id == circle_id))
    r_id = res.scalar_one_or_none()
    if not r_id:
        raise NotFoundError("Care recipient not configured for this circle.")
    return r_id


@router.get("", response_model=list[AppointmentOut])
async def list_appointments(
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> list[AppointmentOut]:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = AppointmentService(db, current_member.circle_id)
    appts = await svc.list_all(recipient_id)
    return [
        AppointmentOut(
            id=a.id,
            circle_id=a.circle_id,
            recipient_id=a.recipient_id,
            doctor_name=a.doctor_name,
            specialty=a.specialty,
            location=a.location,
            scheduled_at=a.scheduled_at,
            notes=a.notes,
            status=a.status.value,
            reminder_offsets_min=a.reminder_offsets_min or [1440, 120],
            created_by=a.created_by,
            created_at=a.created_at,
        )
        for a in appts
    ]


@router.post("", response_model=AppointmentOut)
async def create_appointment(
    payload: AppointmentCreate,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> AppointmentOut:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    svc = AppointmentService(db, current_member.circle_id)
    appt = await svc.create(current_member, recipient_id, payload.model_dump())
    return AppointmentOut(
        id=appt.id,
        circle_id=appt.circle_id,
        recipient_id=appt.recipient_id,
        doctor_name=appt.doctor_name,
        specialty=appt.specialty,
        location=appt.location,
        scheduled_at=appt.scheduled_at,
        notes=appt.notes,
        status=appt.status.value,
        reminder_offsets_min=appt.reminder_offsets_min or [1440, 120],
        created_by=appt.created_by,
        created_at=appt.created_at,
    )


@router.patch("/{appointment_id}", response_model=AppointmentOut)
async def update_appointment(
    appointment_id: UUID,
    payload: AppointmentUpdate,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> AppointmentOut:
    svc = AppointmentService(db, current_member.circle_id)
    appt = await svc.update(current_member, appointment_id, payload.model_dump(exclude_unset=True))
    return AppointmentOut(
        id=appt.id,
        circle_id=appt.circle_id,
        recipient_id=appt.recipient_id,
        doctor_name=appt.doctor_name,
        specialty=appt.specialty,
        location=appt.location,
        scheduled_at=appt.scheduled_at,
        notes=appt.notes,
        status=appt.status.value,
        reminder_offsets_min=appt.reminder_offsets_min or [1440, 120],
        created_by=appt.created_by,
        created_at=appt.created_at,
    )


@router.delete("/{appointment_id}", response_model=MessageResponse)
async def cancel_appointment(
    appointment_id: UUID,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    svc = AppointmentService(db, current_member.circle_id)
    await svc.cancel(current_member, appointment_id)
    return MessageResponse(message="Appointment successfully cancelled.")
