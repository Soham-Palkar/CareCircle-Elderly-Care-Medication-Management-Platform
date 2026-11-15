"""Digital Twin schemas: readings, explainable risk flags, forecasts, proposals."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.appointment import AppointmentOut


class HealthReadingCreate(BaseModel):
    kind: str = Field(pattern="^(heart_rate|sleep_hours|steps|bp_sys|bp_dia|glucose|mood)$")
    value: Decimal
    recorded_at: datetime | None = None
    source: str = "manual"


class HealthReadingOut(BaseModel):
    id: UUID
    recipient_id: UUID
    kind: str
    value: Decimal
    recorded_at: datetime
    source: str


class RiskFlagOut(BaseModel):
    id: UUID
    recipient_id: UUID
    rule_code: str
    severity: str
    message: str
    evidence: dict[str, Any]
    status: str
    created_at: datetime


class ForecastSlotOut(BaseModel):
    slot_label: str
    scheduled_at: datetime
    miss_risk: float
    explanation: str
    risk_level: str


class TwinProfileOut(BaseModel):
    recipient_id: UUID
    latest_readings: dict[str, HealthReadingOut]
    open_flags: list[RiskFlagOut]
    forecast_24h: list[ForecastSlotOut]
    upcoming_appointments: list[AppointmentOut]
    adherence_7d: float
    advisory_notice: str = "Advisory: this health profile is for care coordination only. Discuss any concerns with your doctor."


class ProposalCreate(BaseModel):
    medication_id: UUID
    change: dict[str, Any]
    rationale: str = Field(min_length=5, max_length=500)


class ProposalOut(BaseModel):
    id: UUID
    medication_id: UUID
    proposed_by: UUID | None
    change: dict[str, Any]
    rationale: str
    status: str
    decided_by: UUID | None
    decided_at: datetime | None
    created_at: datetime


class ProposalDecision(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")
    note: str = ""
