"""Dose event and adherence tracking schemas."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.medication import MedicationOut


class DoseEventOut(BaseModel):
    id: UUID
    schedule_id: UUID
    medication_id: UUID
    medication_name: str | None = None
    scheduled_at: datetime
    state: str
    escalation_level: int
    snooze_until: datetime | None = None
    taken_at: datetime | None = None
    recorded_by: UUID | None = None
    recorded_via: str
    skip_reason: str | None = None


class TakenRequest(BaseModel):
    idempotency_key: str | None = None
    recorded_via: str = "app"


class SnoozeRequest(BaseModel):
    snooze_minutes: int = Field(default=15, ge=5, le=120)
    idempotency_key: str | None = None


class SkipRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=255)
    idempotency_key: str | None = None


class NextDoseOut(BaseModel):
    dose: DoseEventOut | None = None
    medication: MedicationOut | None = None
    message: str


class AdherenceSummaryOut(BaseModel):
    recipient_id: UUID
    total_scheduled: int
    taken: int
    missed: int
    adherence_pct: float
    current_streak: int
    best_streak: int


class StreakOut(BaseModel):
    recipient_id: UUID
    current_streak: int
    best_streak: int
    last_date: date | None = None
