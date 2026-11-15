"""Schemas registry."""

from app.schemas.common import ErrorResponse, MessageResponse, PaginatedResponse
from app.schemas.auth import (
    CreateCircleRequest,
    CreateCircleResponse,
    LoginRequest,
    LoginResponse,
    CreateInviteRequest,
    InviteResponse,
    RedeemInviteRequest,
    RedeemInviteResponse,
)
from app.schemas.member import MemberOut, MemberPermissionOut, UpdatePermissionsRequest, MemberWithPermissions, NotifyPrefsUpdate
from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationOut, ScheduleCreate, ScheduleOut
from app.schemas.dose import DoseEventOut, TakenRequest, SnoozeRequest, SkipRequest, NextDoseOut, AdherenceSummaryOut, StreakOut
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut
from app.schemas.twin import HealthReadingCreate, HealthReadingOut, RiskFlagOut, ForecastSlotOut, TwinProfileOut, ProposalCreate, ProposalOut, ProposalDecision
from app.schemas.scan import ScanDraftOut, ScanConfirmRequest, VerifyDoseRequest, VerifyDoseResponse
from app.schemas.voice import VoiceIntentRequest, VoiceIntentResponse
from app.schemas.notification import NotificationOut
from app.schemas.audit import AuditLogOut

__all__ = [
    "ErrorResponse",
    "MessageResponse",
    "PaginatedResponse",
    "CreateCircleRequest",
    "CreateCircleResponse",
    "LoginRequest",
    "LoginResponse",
    "CreateInviteRequest",
    "InviteResponse",
    "RedeemInviteRequest",
    "RedeemInviteResponse",
    "MemberOut",
    "MemberPermissionOut",
    "UpdatePermissionsRequest",
    "MemberWithPermissions",
    "NotifyPrefsUpdate",
    "MedicationCreate",
    "MedicationUpdate",
    "MedicationOut",
    "ScheduleCreate",
    "ScheduleOut",
    "DoseEventOut",
    "TakenRequest",
    "SnoozeRequest",
    "SkipRequest",
    "NextDoseOut",
    "AdherenceSummaryOut",
    "StreakOut",
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentOut",
    "HealthReadingCreate",
    "HealthReadingOut",
    "RiskFlagOut",
    "ForecastSlotOut",
    "TwinProfileOut",
    "ProposalCreate",
    "ProposalOut",
    "ProposalDecision",
    "ScanDraftOut",
    "ScanConfirmRequest",
    "VerifyDoseRequest",
    "VerifyDoseResponse",
    "VoiceIntentRequest",
    "VoiceIntentResponse",
    "NotificationOut",
    "AuditLogOut",
]
