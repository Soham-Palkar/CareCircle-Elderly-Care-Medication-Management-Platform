"""Unit tests for Laplace-smoothed miss risk forecasting."""

from datetime import datetime, timezone
import pytest

from app.domain.forecast import (
    SlotHistory,
    build_forecast,
    classify_risk,
    compute_miss_risk,
)


def test_compute_miss_risk_laplace():
    # 0 misses out of 10 -> (0 + 1) / (10 + 2) = 1/12 ≈ 0.083
    risk_0 = compute_miss_risk(missed=0, total=10)
    assert round(risk_0, 3) == 0.083

    # 5 misses out of 10 -> (5 + 1) / (10 + 2) = 6/12 = 0.50
    risk_half = compute_miss_risk(missed=5, total=10)
    assert risk_half == 0.50

    # 10 misses out of 10 -> (10 + 1) / (10 + 2) = 11/12 ≈ 0.917
    risk_all = compute_miss_risk(missed=10, total=10)
    assert round(risk_all, 3) == 0.917


def test_classify_risk():
    assert classify_risk(0.15) == "low"
    assert classify_risk(0.29) == "low"
    assert classify_risk(0.30) == "medium"
    assert classify_risk(0.59) == "medium"
    assert classify_risk(0.60) == "high"
    assert classify_risk(0.95) == "high"


def test_build_forecast():
    # Monday is weekday 0
    histories = [
        SlotHistory(slot_label="morning", weekday=0, missed=1, total=10),
        SlotHistory(slot_label="evening", weekday=0, missed=8, total=10),
    ]
    # Upcoming slots on Monday (2026-11-16 is a Monday)
    dt_morning = datetime(2026, 11, 16, 8, 30, tzinfo=timezone.utc)
    dt_evening = datetime(2026, 11, 16, 20, 30, tzinfo=timezone.utc)

    forecasts = build_forecast(
        slot_histories=histories,
        upcoming_slots=[("morning", dt_morning), ("evening", dt_evening)],
    )

    assert len(forecasts) == 2
    # Morning: (1+1)/(10+2) = 2/12 ≈ 0.17 -> low
    assert forecasts[0].slot_label == "morning"
    assert forecasts[0].risk_level == "low"

    # Evening: (8+1)/(10+2) = 9/12 = 0.75 -> high
    assert forecasts[1].slot_label == "evening"
    assert forecasts[1].risk_level == "high"
    assert "Monday" in forecasts[1].explanation
