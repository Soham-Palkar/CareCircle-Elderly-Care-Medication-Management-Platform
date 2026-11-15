"""
types.py — Shared enums and dataclasses for the CareCircle domain layer.

This module contains NO database, network, or framework imports.
All types are pure Python data structures suitable for use across
services, event handlers, and API serialisation layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class DoseState(str, Enum):
    """Lifecycle states for a single dose event.

    Transitions are strictly governed by :mod:`backend.app.domain.state_machine`.
    Terminal states (taken, taken_late, skipped) may not transition further.
    """

    scheduled = "scheduled"
    reminded = "reminded"
    snoozed = "snoozed"
    taken = "taken"
    taken_late = "taken_late"
    skipped = "skipped"
    missed = "missed"


class DoseRecordedVia(str, Enum):
    """The channel through which a dose action was recorded."""

    app = "app"
    voice = "voice"
    telegram = "telegram"
    email_link = "email_link"
    caretaker = "caretaker"


class Role(str, Enum):
    """Roles within a CareCircle.

    Roles determine the default permission set a member starts with.
    Per-member permissions may further narrow (never exceed) caretaker/family defaults.
    Elder permissions are always maximal and cannot be narrowed.
    """

    elder = "elder"
    caretaker = "caretaker"
    family = "family"
    doctor = "doctor"


class MedCriticality(str, Enum):
    """Clinical criticality of a medication.

    *critical* medications trigger more aggressive escalation policies and
    raise R3 risk flags when missed alongside elevated vitals.
    """

    normal = "normal"
    critical = "critical"


class NotifType(str, Enum):
    """High-level notification categories sent to circle members."""

    dose_due = "dose_due"
    dose_missed = "dose_missed"
    appointment = "appointment"
    refill = "refill"
    risk_flag = "risk_flag"
    help = "help"


class NotifChannel(str, Enum):
    """Delivery channels for notifications."""

    email = "email"
    telegram = "telegram"
    in_app = "in_app"


class RiskSeverity(str, Enum):
    """Severity levels for risk flags (R1–R6).

    *info*   — advisory, no immediate action required.
    *warning* — the elder or caretaker should take note.
    *high*   — urgent; escalate to caretaker / family immediately.
    """

    info = "info"
    warning = "warning"
    high = "high"


class ScheduleKind(str, Enum):
    """How a medication schedule anchors its dose times.

    *fixed_time*      — dose at a specific wall-clock time each day.
    *routine_anchor*  — dose relative to a daily routine event (e.g. breakfast).
    """

    fixed_time = "fixed_time"
    routine_anchor = "routine_anchor"


class ReadingKind(str, Enum):
    """Kinds of health readings that the platform tracks."""

    heart_rate = "heart_rate"
    sleep_hours = "sleep_hours"
    steps = "steps"
    bp_sys = "bp_sys"
    bp_dia = "bp_dia"
    glucose = "glucose"
    mood = "mood"


class ReadingSource(str, Enum):
    """Where a health reading originated."""

    simulated = "simulated"
    manual = "manual"
    device = "device"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class DoseAction:
    """An action recorded against a dose event.

    Attributes:
        event_id:  UUID of the DoseEvent being acted upon.
        action:    The action string (e.g. "taken", "skipped", "snoozed").
        member_id: UUID of the circle member performing the action.
        via:       The channel through which the action was recorded.
    """

    event_id: UUID
    action: str
    member_id: UUID
    via: DoseRecordedVia


@dataclass
class RiskFlagResult:
    """The output of a single risk-rule evaluation.

    Attributes:
        rule_code: Identifier for the rule (e.g. "R1", "R3").
        severity:  How serious the flag is.
        message:   Human-readable advisory message shown to the user.
                   Always prefixed with "Advisory: discuss with your doctor."
        evidence:  Raw data points that triggered the flag, for audit.
    """

    rule_code: str
    severity: RiskSeverity
    message: str
    evidence: dict


@dataclass
class ForecastSlot:
    """A single upcoming dose slot with predicted miss risk.

    Attributes:
        slot_label:    Human-readable label (e.g. "morning", "evening").
        scheduled_at:  UTC datetime of the upcoming dose.
        miss_risk:     Laplace-smoothed probability of a miss (0.0–1.0).
        explanation:   Plain-language reason for the risk estimate.
        risk_level:    Categorical level: "low", "medium", or "high".
    """

    slot_label: str
    scheduled_at: datetime
    miss_risk: float
    explanation: str
    risk_level: str


@dataclass
class EscalationAction:
    """The next escalation step to perform for an un-actioned dose.

    Attributes:
        level:       Escalation level (0 = first reminder to elder, increasing).
        target_role: The role to notify at this level (e.g. "elder", "caretaker").
        notify_type: The notification type to send (matches NotifType values).
        description: Human-readable description of this escalation step.
    """

    level: int
    target_role: str
    notify_type: str
    description: str


@dataclass
class Intent:
    """The result of parsing a natural-language voice or text command.

    Attributes:
        name:       Canonical intent name (e.g. "taken", "later", "help").
                    "unknown" when no pattern matched.
        confidence: Confidence score: 1.0 for exact match, 0.8 for partial,
                    0.0 for no match.
        params:     Additional extracted parameters (may be empty).
    """

    name: str
    confidence: float
    params: dict = field(default_factory=dict)
