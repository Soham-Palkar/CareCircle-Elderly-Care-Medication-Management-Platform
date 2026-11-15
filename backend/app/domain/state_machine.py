"""
state_machine.py — Dose event state transition guard for CareCircle.

This module is the **single source of truth** for which dose-state transitions
are legally permitted.  Every path that mutates a DoseEvent's state MUST call
:func:`transition` (or at minimum :func:`can_transition`) before persisting.

No database, network, or framework imports are allowed in this module.
"""

from __future__ import annotations

from .types import DoseState

# ---------------------------------------------------------------------------
# Transition table
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[DoseState, set[DoseState]] = {
    DoseState.scheduled: {DoseState.reminded},
    DoseState.reminded: {
        DoseState.taken,
        DoseState.snoozed,
        DoseState.skipped,
        DoseState.missed,
    },
    DoseState.snoozed: {
        DoseState.reminded,
        DoseState.taken,
        DoseState.skipped,
        DoseState.missed,
    },
    DoseState.missed: {DoseState.taken_late},
    # Terminal states — no further transitions are permitted.
    DoseState.taken: set(),
    DoseState.taken_late: set(),
    DoseState.skipped: set(),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def can_transition(current: DoseState, target: DoseState) -> bool:
    """Return *True* if moving from *current* to *target* is a valid transition.

    This is a pure predicate — it never raises, never mutates state, and has no
    side effects.  Use it for pre-flight checks before calling :func:`transition`.

    Args:
        current: The dose event's present state.
        target:  The desired next state.

    Returns:
        ``True`` if the transition is listed in :data:`VALID_TRANSITIONS`,
        ``False`` otherwise (including if *current* is a terminal state).

    Examples:
        >>> can_transition(DoseState.scheduled, DoseState.reminded)
        True
        >>> can_transition(DoseState.taken, DoseState.missed)
        False
        >>> can_transition(DoseState.reminded, DoseState.taken)
        True
    """
    return target in VALID_TRANSITIONS.get(current, set())


def transition(current: DoseState, target: DoseState) -> DoseState:
    """Attempt to move a dose event from *current* to *target*.

    This is the **enforcing** variant of :func:`can_transition`.  It performs
    the same validity check, but raises a descriptive :class:`ValueError` on
    failure so callers never silently accept an illegal transition.

    The function is intentionally stateless: it does not persist anything.
    The caller is responsible for saving the returned state to the database.

    Args:
        current: The dose event's present state.
        target:  The desired next state.

    Returns:
        *target* — the new state after a successful transition.

    Raises:
        ValueError: If the transition is not permitted.  The message includes
                    both states and whether *current* is terminal, to aid
                    debugging without leaking PII.

    Examples:
        >>> transition(DoseState.scheduled, DoseState.reminded)
        <DoseState.reminded: 'reminded'>
        >>> transition(DoseState.taken, DoseState.missed)
        Traceback (most recent call last):
            ...
        ValueError: Invalid dose transition: taken → missed. 'taken' is a terminal state; no further transitions are allowed.
        >>> transition(DoseState.reminded, DoseState.scheduled)
        Traceback (most recent call last):
            ...
        ValueError: Invalid dose transition: reminded → scheduled. Allowed next states from 'reminded': missed, skipped, snoozed, taken.
    """
    allowed = VALID_TRANSITIONS.get(current, set())

    if target in allowed:
        return target

    # Build a helpful error message.
    if not allowed:
        reason = (
            f"'{current.value}' is a terminal state; no further transitions are allowed."
        )
    else:
        sorted_allowed = ", ".join(sorted(s.value for s in allowed))
        reason = (
            f"Allowed next states from '{current.value}': {sorted_allowed}."
        )

    raise ValueError(
        f"Invalid dose transition: {current.value} → {target.value}. {reason}"
    )
