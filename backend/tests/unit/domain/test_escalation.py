"""Unit tests for notification escalation policy logic."""

from datetime import datetime, timedelta, timezone
import pytest

from app.domain.types import DoseState, MedCriticality, Role
from app.domain.escalation import (
    DEFAULT_CRITICAL_POLICY,
    DEFAULT_ESCALATION_POLICY,
    get_next_escalation,
    should_mark_missed,
)


def test_no_escalation_before_due_time():
    now = datetime(2026, 11, 15, 8, 0, tzinfo=timezone.utc)
    due = datetime(2026, 11, 15, 8, 30, tzinfo=timezone.utc)
    action = get_next_escalation(current_level=0, due_time=due, now=now)
    assert action is None


def test_default_escalation_normal_medication():
    due = datetime(2026, 11, 15, 8, 0, tzinfo=timezone.utc)

    # 1. At 5 minutes past: not yet +10 min for level 1
    action = get_next_escalation(current_level=0, due_time=due, now=due + timedelta(minutes=5))
    assert action is None

    # 2. At 10 minutes past: triggers level 1 to elder
    action = get_next_escalation(current_level=0, due_time=due, now=due + timedelta(minutes=10))
    assert action is not None
    assert action.level == 1
    assert action.target_role == Role.elder
    assert action.notify_type == "dose_due"

    # 3. At 25 minutes past: not yet +30 min for level 2
    action = get_next_escalation(current_level=1, due_time=due, now=due + timedelta(minutes=25))
    assert action is None

    # 4. At 30 minutes past: triggers level 2 to caretaker (dose_missed)
    action = get_next_escalation(current_level=1, due_time=due, now=due + timedelta(minutes=30))
    assert action is not None
    assert action.level == 2
    assert action.target_role == Role.caretaker
    assert action.notify_type == "dose_missed"

    # 5. At 60 minutes past: triggers level 3 to family
    action = get_next_escalation(current_level=2, due_time=due, now=due + timedelta(minutes=60))
    assert action is not None
    assert action.level == 3
    assert action.target_role == Role.family
    assert action.notify_type == "dose_missed"

    # 6. Beyond highest level (level 3 -> 4) returns None
    action = get_next_escalation(current_level=3, due_time=due, now=due + timedelta(minutes=120))
    assert action is None


def test_critical_medication_escalates_faster():
    due = datetime(2026, 11, 15, 8, 0, tzinfo=timezone.utc)

    # Critical level 1: +5 min
    action = get_next_escalation(
        current_level=0, due_time=due, now=due + timedelta(minutes=5), criticality=MedCriticality.critical
    )
    assert action is not None
    assert action.level == 1
    assert action.target_role == Role.elder

    # Critical level 2 (caretaker): +15 min
    action = get_next_escalation(
        current_level=1, due_time=due, now=due + timedelta(minutes=15), criticality=MedCriticality.critical
    )
    assert action is not None
    assert action.level == 2
    assert action.target_role == Role.caretaker

    # Critical level 3 (family): +30 min
    action = get_next_escalation(
        current_level=2, due_time=due, now=due + timedelta(minutes=30), criticality=MedCriticality.critical
    )
    assert action is not None
    assert action.level == 3
    assert action.target_role == Role.family


def test_should_mark_missed_after_grace_period():
    due = datetime(2026, 11, 15, 8, 0, tzinfo=timezone.utc)

    # Under 60 min
    assert should_mark_missed(DoseState.scheduled, due, due + timedelta(minutes=59)) is False
    assert should_mark_missed(DoseState.reminded, due, due + timedelta(minutes=59)) is False

    # At or above 60 min
    assert should_mark_missed(DoseState.scheduled, due, due + timedelta(minutes=60)) is True
    assert should_mark_missed(DoseState.reminded, due, due + timedelta(minutes=65)) is True
    assert should_mark_missed(DoseState.snoozed, due, due + timedelta(minutes=90)) is True

    # Terminal or already resolved states should never be marked missed
    assert should_mark_missed(DoseState.taken, due, due + timedelta(minutes=120)) is False
    assert should_mark_missed(DoseState.skipped, due, due + timedelta(minutes=120)) is False
    assert should_mark_missed(DoseState.missed, due, due + timedelta(minutes=120)) is False
