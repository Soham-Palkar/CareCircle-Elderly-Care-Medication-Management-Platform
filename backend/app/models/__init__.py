"""SQLAlchemy models registry."""

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.circle import CareCircle
from app.models.recipient import CareRecipient
from app.models.member import Member, Role
from app.models.permission import MemberPermission
from app.models.invite import Invite
from app.models.medication import Medication, MedicationCriticality, MedicationStatus, MedicationSource
from app.models.schedule import MedicationSchedule, ScheduleKind
from app.models.dose_event import DoseEvent, DoseState, DoseRecordedVia
from app.models.appointment import Appointment, AppointmentStatus
from app.models.notification import Notification, NotificationChannel, NotificationType, NotificationStatus
from app.models.escalation_policy import EscalationPolicy
from app.models.health_reading import HealthReading, ReadingKind, ReadingSource
from app.models.risk_flag import RiskFlag, RiskSeverity, RiskFlagStatus
from app.models.proposal import ScheduleProposal, ProposalStatus
from app.models.scan_draft import ScanDraft, ScanDraftStatus
from app.models.streak import Streak
from app.models.reward import Reward, RewardType
from app.models.adherence_daily import AdherenceDaily
from app.models.interaction_rule import InteractionRule
from app.models.audit import AuditLog

__all__ = [
    "Base",
    "UUIDMixin",
    "TimestampMixin",
    "CareCircle",
    "CareRecipient",
    "Member",
    "Role",
    "MemberPermission",
    "Invite",
    "Medication",
    "MedicationCriticality",
    "MedicationStatus",
    "MedicationSource",
    "MedicationSchedule",
    "ScheduleKind",
    "DoseEvent",
    "DoseState",
    "DoseRecordedVia",
    "Appointment",
    "AppointmentStatus",
    "Notification",
    "NotificationChannel",
    "NotificationType",
    "NotificationStatus",
    "EscalationPolicy",
    "HealthReading",
    "ReadingKind",
    "ReadingSource",
    "RiskFlag",
    "RiskSeverity",
    "RiskFlagStatus",
    "ScheduleProposal",
    "ProposalStatus",
    "ScanDraft",
    "ScanDraftStatus",
    "Streak",
    "Reward",
    "RewardType",
    "AdherenceDaily",
    "InteractionRule",
    "AuditLog",
]
