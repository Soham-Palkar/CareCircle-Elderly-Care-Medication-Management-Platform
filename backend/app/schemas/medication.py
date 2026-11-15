"""Medication and schedule schemas."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class MedicationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    strength: str = Field(min_length=1, max_length=50)
    form: str = "tablet"
    instructions: str = ""
    purpose_card: dict[str, Any] = Field(default_factory=dict)
    criticality: str = "normal"
    dose_quantity: Decimal = Decimal("1.0")
    stock_count: Decimal = Decimal("0.0")
    refill_threshold_days: int = 5
    confirmed_with_doctor: bool = False


class MedicationUpdate(BaseModel):
    name: str | None = None
    strength: str | None = None
    form: str | None = None
    instructions: str | None = None
    purpose_card: dict[str, Any] | None = None
    criticality: str | None = None
    dose_quantity: Decimal | None = None
    stock_count: Decimal | None = None
    refill_threshold_days: int | None = None
    confirmed_with_doctor: bool | None = None


class MedicationOut(BaseModel):
    id: UUID
    recipient_id: UUID
    name: str
    strength: str
    form: str
    instructions: str
    purpose_card: dict[str, Any]
    criticality: str
    dose_quantity: Decimal
    stock_count: Decimal
    refill_threshold_days: int
    status: str
    source: str
    confirmed_with_doctor: bool
    created_at: datetime
    updated_at: datetime


class ScheduleCreate(BaseModel):
    kind: str = "fixed_time"
    time_of_day: time | None = None
    anchor: str | None = None
    anchor_offset_min: int = 0
    days_of_week: int = 127
    start_date: date
    end_date: date | None = None
    grace_minutes: int = 60
    confirmed_with_doctor: bool = False


class ScheduleOut(BaseModel):
    id: UUID
    medication_id: UUID
    kind: str
    time_of_day: time | None
    anchor: str | None
    anchor_offset_min: int
    days_of_week: int
    start_date: date
    end_date: date | None
    grace_minutes: int
    is_active: bool
    supersedes_id: UUID | None
    created_at: datetime
