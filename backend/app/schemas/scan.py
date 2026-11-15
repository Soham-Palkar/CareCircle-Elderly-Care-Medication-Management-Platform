"""Scan draft and pill-check verification schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.schemas.medication import MedicationCreate, ScheduleCreate


class ScanDraftOut(BaseModel):
    id: UUID
    recipient_id: UUID
    uploaded_by: UUID
    extracted: dict[str, Any]
    confidence: Decimal
    status: str
    expires_at: datetime
    created_at: datetime


class ScanConfirmRequest(BaseModel):
    medication_data: MedicationCreate
    schedule_data: ScheduleCreate


class VerifyDoseRequest(BaseModel):
    dose_event_id: UUID


class VerifyDoseResponse(BaseModel):
    match: bool
    confidence: float
    message: str
