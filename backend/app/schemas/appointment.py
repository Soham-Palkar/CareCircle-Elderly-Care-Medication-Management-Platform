"""Appointment schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    doctor_name: str = Field(min_length=1, max_length=100)
    specialty: str = ""
    location: str = ""
    scheduled_at: datetime
    notes: str = ""
    reminder_offsets_min: list[int] = Field(default_factory=lambda: [1440, 120])


class AppointmentUpdate(BaseModel):
    doctor_name: str | None = None
    specialty: str | None = None
    location: str | None = None
    scheduled_at: datetime | None = None
    notes: str | None = None
    status: str | None = None
    reminder_offsets_min: list[int] | None = None


class AppointmentOut(BaseModel):
    id: UUID
    circle_id: UUID
    recipient_id: UUID
    doctor_name: str
    specialty: str
    location: str
    scheduled_at: datetime
    notes: str
    status: str
    reminder_offsets_min: list[int]
    created_by: UUID | None
    created_at: datetime
