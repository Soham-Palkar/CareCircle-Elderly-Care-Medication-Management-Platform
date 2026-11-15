"""Unit tests for schedule expansion across dates, routine anchors, and timezones."""

from datetime import date, time
import pytest

from app.domain.schedule_expansion import ScheduleParams, expand_schedule


def test_fixed_time_daily_expansion():
    params = ScheduleParams(
        schedule_id="sched-1",
        kind="fixed_time",
        time_of_day=time(9, 0),
        anchor=None,
        anchor_offset_min=0,
        days_of_week=127,  # Every day
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 30),
        recipient_timezone="UTC",
        routine_times={},
    )
    # Expand 3 days
    events = list(expand_schedule(params, date(2026, 11, 1), date(2026, 11, 3)))
    assert len(events) == 3
    for s_id, dt in events:
        assert s_id == "sched-1"
        assert dt.hour == 9
        assert dt.minute == 0


def test_routine_anchor_expansion():
    params = ScheduleParams(
        schedule_id="sched-breakfast",
        kind="routine_anchor",
        time_of_day=None,
        anchor="breakfast",
        anchor_offset_min=15,  # 15 minutes after breakfast
        days_of_week=127,
        start_date=date(2026, 11, 1),
        end_date=None,
        recipient_timezone="UTC",
        routine_times={"breakfast": "08:30"},
    )
    events = list(expand_schedule(params, date(2026, 11, 1), date(2026, 11, 2)))
    assert len(events) == 2
    # 08:30 + 15 min = 08:45
    for _, dt in events:
        assert dt.hour == 8
        assert dt.minute == 45


def test_days_of_week_filter():
    # Only Monday (bit 0 = 1) and Wednesday (bit 2 = 4) -> 1 + 4 = 5
    params = ScheduleParams(
        schedule_id="sched-mon-wed",
        kind="fixed_time",
        time_of_day=time(10, 0),
        anchor=None,
        anchor_offset_min=0,
        days_of_week=5,
        start_date=date(2026, 11, 2),  # Monday
        end_date=None,
        recipient_timezone="UTC",
        routine_times={},
    )
    # Mon Nov 2 to Sun Nov 8 (1 full week)
    events = list(expand_schedule(params, date(2026, 11, 2), date(2026, 11, 8)))
    assert len(events) == 2  # Nov 2 (Mon) and Nov 4 (Wed)
    assert events[0][1].date() == date(2026, 11, 2)
    assert events[1][1].date() == date(2026, 11, 4)


def test_timezone_conversion_to_utc():
    # Asia/Kolkata is UTC+5:30. Dose at 08:30 IST -> 03:00 UTC
    params = ScheduleParams(
        schedule_id="sched-ist",
        kind="fixed_time",
        time_of_day=time(8, 30),
        anchor=None,
        anchor_offset_min=0,
        days_of_week=127,
        start_date=date(2026, 11, 1),
        end_date=None,
        recipient_timezone="Asia/Kolkata",
        routine_times={},
    )
    events = list(expand_schedule(params, date(2026, 11, 1), date(2026, 11, 1)))
    assert len(events) == 1
    _, dt_utc = events[0]
    assert dt_utc.hour == 3
    assert dt_utc.minute == 0
