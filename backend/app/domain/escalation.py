"""escalation.py — Pure domain logic for notification escalation.

Rules:
- Escalation occurs when an unresolved dose event exceeds its scheduled due time.
- Delays are evaluated against due_time (scheduled_at).
- Default ladder (if no custom policies configured):
    L0: 0 min -> elder (in-app, voice, email, Telegram)
    L1: +10 min -> elder repeat reminder
    L2: +30 min -> caretaker (event marked missed)
    L3: +60 min -> family
- Pure functions only; no database, network, or external framework dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from app.domain.types import DoseState, EscalationAction, MedCriticality, Role


@dataclass(frozen=True)
class EscalationPolicyEntry:
    level: int
    delay_minutes: int
    target_role: Role
    criticality: MedCriticality = MedCriticality.normal


DEFAULT_ESCALATION_POLICY: list[EscalationPolicyEntry] = [
    EscalationPolicyEntry(level=0, delay_minutes=0, target_role=Role.elder),
    EscalationPolicyEntry(level=1, delay_minutes=10, target_role=Role.elder),
    EscalationPolicyEntry(level=2, delay_minutes=30, target_role=Role.caretaker),
    EscalationPolicyEntry(level=3, delay_minutes=60, target_role=Role.family),
]

# Critical medicines escalate faster
DEFAULT_CRITICAL_POLICY: list[EscalationPolicyEntry] = [
    EscalationPolicyEntry(level=0, delay_minutes=0, target_role=Role.elder, criticality=MedCriticality.critical),
    EscalationPolicyEntry(level=1, delay_minutes=5, target_role=Role.elder, criticality=MedCriticality.critical),
    EscalationPolicyEntry(level=2, delay_minutes=15, target_role=Role.caretaker, criticality=MedCriticality.critical),
    EscalationPolicyEntry(level=3, delay_minutes=30, target_role=Role.family, criticality=MedCriticality.critical),
]


def get_next_escalation(
    current_level: int,
    due_time: datetime,
    now: datetime,
    policies: Sequence[EscalationPolicyEntry] | None = None,
    criticality: MedCriticality = MedCriticality.normal,
) -> EscalationAction | None:
    """Return the next EscalationAction if due, or None.

    Evaluates whether the time elapsed since due_time warrants transitioning
    to level = current_level + 1.
    """
    if now < due_time:
        return None

    if not policies:
        policies = DEFAULT_CRITICAL_POLICY if criticality == MedCriticality.critical else DEFAULT_ESCALATION_POLICY

    next_level = current_level + 1
    # Find matching policy for next_level
    matching = [p for p in policies if p.level == next_level]
    if not matching:
        return None

    policy = matching[0]
    elapsed_minutes = (now - due_time).total_seconds() / 60.0

    if elapsed_minutes >= policy.delay_minutes:
        notify_type = "dose_missed" if policy.level >= 2 else "dose_due"
        return EscalationAction(
            level=policy.level,
            target_role=policy.target_role,
            notify_type=notify_type,
            description=f"Escalation level {policy.level} to {policy.target_role.value} (+{policy.delay_minutes}m)",
        )

    return None


def should_mark_missed(
    state: DoseState,
    due_time: datetime,
    now: datetime,
    grace_minutes: int = 60,
) -> bool:
    """Return True if an unresolved dose event has passed its grace period."""
    if state not in (DoseState.scheduled, DoseState.reminded, DoseState.snoozed):
        return False
    elapsed_minutes = (now - due_time).total_seconds() / 60.0
    return elapsed_minutes >= grace_minutes
