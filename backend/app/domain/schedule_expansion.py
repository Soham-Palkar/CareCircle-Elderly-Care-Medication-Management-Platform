"""
schedule_expansion.py — Expand medication schedules into concrete UTC datetimes.

This module converts abstract schedule parameters (fixed clock times or
routine-relative anchors) into an ordered sequence of UTC-aware
:class:`~datetime.datetime` objects, one per dose occurrence.

No database, network, or framework imports are allowed in this module.
Only the Python standard library and *pytz* are used.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Iterator

import pytz


@dataclass
class ScheduleParams:
    """All parameters required to expand a single medication schedule.

    Attributes:
        schedule_id:        UUID of the schedule (stored as string).
        kind:               ``"fixed_time"`` or ``"routine_anchor"``.
        time_of_day:        Wall-clock time for ``fixed_time`` schedules.
                            ``None`` for ``routine_anchor`` schedules.
        anchor:             Routine anchor name (e.g. ``"breakfast"``,
                            ``"lunch"``, ``"dinner"``, ``"bedtime"``,
                            ``"wake"``) for ``routine_anchor`` schedules.
                            ``None`` for ``fixed_time`` schedules.
        anchor_offset_min:  Minutes to add to the anchor time before computing
                            the dose time.  May be negative (dose before anchor).
        days_of_week:       Bitmask of active weekdays.
                            Bit 0 (value 1) = Monday, bit 6 (value 64) = Sunday.
                            Use 127 (0b1111111) for every day.
        start_date:         Inclusive first date on which doses occur.
        end_date:           Inclusive last date on which doses occur, or ``None``
                            for an open-ended schedule.
        recipient_timezone: IANA timezone string for the elder's local time
                            (e.g. ``"Asia/Kolkata"``).
        routine_times:      Mapping of anchor name → local time string
                            (``"HH:MM"``) representing the elder's typical
                            routine.  Required for ``routine_anchor`` schedules.
                            Example::

                                {
                                    "breakfast": "08:30",
                                    "lunch":     "13:30",
                                    "dinner":    "20:30",
                                    "bedtime":   "22:00",
                                    "wake":      "07:00",
                                }
    """

    schedule_id: str
    kind: str
    time_of_day: time | None
    anchor: str | None
    anchor_offset_min: int
    days_of_week: int
    start_date: date
    end_date: date | None
    recipient_timezone: str
    routine_times: dict


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_WEEKDAY_BITS = {
    0: 1,   # Monday
    1: 2,   # Tuesday
    2: 4,   # Wednesday
    3: 8,   # Thursday
    4: 16,  # Friday
    5: 32,  # Saturday
    6: 64,  # Sunday
}


def _is_active_on(params: ScheduleParams, day: date) -> bool:
    """Return True if *day* falls on an active weekday per the bitmask."""
    bit = _WEEKDAY_BITS[day.weekday()]
    return bool(params.days_of_week & bit)


def _local_time_for_day(params: ScheduleParams, day: date) -> time | None:
    """Resolve the local dose time for *day*.

    For ``fixed_time`` schedules this is simply :attr:`~ScheduleParams.time_of_day`.
    For ``routine_anchor`` schedules the anchor time is looked up from
    :attr:`~ScheduleParams.routine_times` and the offset is applied.

    Returns ``None`` if the anchor is not found in ``routine_times``.
    """
    if params.kind == "fixed_time":
        return params.time_of_day

    # routine_anchor
    anchor = params.anchor
    if anchor is None or anchor not in params.routine_times:
        return None

    raw = params.routine_times[anchor]  # e.g. "08:30"
    h, m = map(int, raw.split(":"))
    base = datetime(day.year, day.month, day.day, h, m)
    adjusted = base + timedelta(minutes=params.anchor_offset_min)
    return adjusted.time()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def expand_schedule(
    params: ScheduleParams,
    from_date: date,
    to_date: date,
) -> Iterator[tuple[str, datetime]]:
    """Yield ``(schedule_id, scheduled_at_utc)`` for each dose in the range.

    The generator walks every calendar day in ``[from_date, to_date]`` and
    emits a UTC-aware :class:`~datetime.datetime` for each day that:

    1. Falls within the schedule's ``start_date``/``end_date`` bounds.
    2. Is active according to the ``days_of_week`` bitmask.
    3. Has a resolvable local dose time (anchor found in ``routine_times``).

    Duplicate ``(schedule_id, scheduled_at_utc)`` pairs are never emitted
    (guarded by an internal *seen* set).

    DST transitions are handled correctly: pytz localizes the naive local
    datetime with ``is_dst=False`` (fall-back ambiguity resolved to standard
    time) before converting to UTC.

    Args:
        params:    All parameters describing the schedule.
        from_date: Inclusive start of the expansion window.
        to_date:   Inclusive end of the expansion window.

    Yields:
        Tuples of ``(schedule_id: str, scheduled_at_utc: datetime)``.
        ``scheduled_at_utc`` is always timezone-aware (UTC).

    Raises:
        pytz.exceptions.UnknownTimeZoneError: If ``params.recipient_timezone``
            is not a valid IANA timezone string.

    Examples:
        >>> from datetime import date, time
        >>> p = ScheduleParams(
        ...     schedule_id="abc",
        ...     kind="fixed_time",
        ...     time_of_day=time(9, 0),
        ...     anchor=None,
        ...     anchor_offset_min=0,
        ...     days_of_week=0b1111111,  # every day
        ...     start_date=date(2024, 1, 1),
        ...     end_date=None,
        ...     recipient_timezone="UTC",
        ...     routine_times={},
        ... )
        >>> slots = list(expand_schedule(p, date(2024, 1, 1), date(2024, 1, 3)))
        >>> len(slots)
        3
        >>> slots[0][0]
        'abc'
    """
    tz = pytz.timezone(params.recipient_timezone)
    utc = pytz.utc
    seen: set[tuple[str, datetime]] = set()

    current = from_date
    delta = timedelta(days=1)

    while current <= to_date:
        # 1. Check schedule bounds.
        if current < params.start_date:
            current += delta
            continue
        if params.end_date is not None and current > params.end_date:
            current += delta
            continue

        # 2. Check weekday bitmask.
        if not _is_active_on(params, current):
            current += delta
            continue

        # 3. Resolve local time.
        local_t = _local_time_for_day(params, current)
        if local_t is None:
            current += delta
            continue

        # 4. Build a naive local datetime and localise it.
        naive_local = datetime(
            current.year, current.month, current.day,
            local_t.hour, local_t.minute, local_t.second,
        )
        try:
            aware_local = tz.localize(naive_local, is_dst=False)
        except pytz.exceptions.NonExistentTimeError:
            # Clocks spring forward — shift forward by one hour.
            aware_local = tz.localize(
                naive_local + timedelta(hours=1), is_dst=True
            )

        # 5. Convert to UTC.
        aware_utc = aware_local.astimezone(utc)

        # 6. Dedup and yield.
        key = (params.schedule_id, aware_utc)
        if key not in seen:
            seen.add(key)
            yield params.schedule_id, aware_utc

        current += delta
