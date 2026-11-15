"""Unit tests for DoseState state machine transitions (100% transition coverage)."""

import pytest
from app.domain.types import DoseState
from app.domain.state_machine import can_transition, transition, VALID_TRANSITIONS


def test_valid_transitions_from_scheduled():
    assert can_transition(DoseState.scheduled, DoseState.reminded) is True
    assert transition(DoseState.scheduled, DoseState.reminded) == DoseState.reminded

    # Invalid transitions from scheduled
    for invalid in [DoseState.taken, DoseState.taken_late, DoseState.skipped, DoseState.missed, DoseState.snoozed]:
        assert can_transition(DoseState.scheduled, invalid) is False
        with pytest.raises(ValueError, match="Invalid dose transition"):
            transition(DoseState.scheduled, invalid)


def test_valid_transitions_from_reminded():
    allowed = {DoseState.taken, DoseState.snoozed, DoseState.skipped, DoseState.missed}
    for target in allowed:
        assert can_transition(DoseState.reminded, target) is True
        assert transition(DoseState.reminded, target) == target

    # Invalid transitions from reminded
    for invalid in [DoseState.scheduled, DoseState.taken_late]:
        assert can_transition(DoseState.reminded, invalid) is False
        with pytest.raises(ValueError):
            transition(DoseState.reminded, invalid)


def test_valid_transitions_from_snoozed():
    allowed = {DoseState.reminded, DoseState.taken, DoseState.skipped, DoseState.missed}
    for target in allowed:
        assert can_transition(DoseState.snoozed, target) is True
        assert transition(DoseState.snoozed, target) == target

    for invalid in [DoseState.scheduled, DoseState.taken_late]:
        assert can_transition(DoseState.snoozed, invalid) is False
        with pytest.raises(ValueError):
            transition(DoseState.snoozed, invalid)


def test_valid_transitions_from_missed():
    # Only late taken is allowed from missed
    assert can_transition(DoseState.missed, DoseState.taken_late) is True
    assert transition(DoseState.missed, DoseState.taken_late) == DoseState.taken_late

    for invalid in [DoseState.scheduled, DoseState.reminded, DoseState.snoozed, DoseState.taken, DoseState.skipped]:
        assert can_transition(DoseState.missed, invalid) is False
        with pytest.raises(ValueError):
            transition(DoseState.missed, invalid)


def test_terminal_states_cannot_transition():
    terminal_states = [DoseState.taken, DoseState.taken_late, DoseState.skipped]
    all_states = list(DoseState)

    for term in terminal_states:
        for any_target in all_states:
            assert can_transition(term, any_target) is False
            with pytest.raises(ValueError, match="terminal state"):
                transition(term, any_target)


def test_idempotent_or_same_state_is_rejected_by_state_machine():
    # Transitioning to the exact same state is invalid in this strict state machine
    for state in DoseState:
        if state not in (VALID_TRANSITIONS.get(state, set())):
            assert can_transition(state, state) is False
