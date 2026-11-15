"""Unit tests for the explainable Digital Twin risk rules (R1 to R6)."""

from datetime import datetime, time, timedelta, timezone
import pytest

from app.domain.types import RiskSeverity
from app.domain.risk_rules import (
    check_r1_adherence_drop,
    check_r2_refill_soon,
    check_r3_miss_and_vitals,
    check_r4_poor_sleep,
    check_r5_inactivity,
    check_r6_duplicate_or_interaction,
)


def test_r1_adherence_drop():
    # Good adherence, no slot misses
    assert check_r1_adherence_drop(0.85, {"morning": 1, "evening": 1}) is None

    # Moderate drop (< 70%) -> Warning
    res1 = check_r1_adherence_drop(0.65, {})
    assert res1 is not None
    assert res1.rule_code == "R1_ADHERENCE_DROP"
    assert res1.severity == RiskSeverity.warning
    assert "Advisory" in res1.message

    # Severe drop (< 50%) -> High
    res2 = check_r1_adherence_drop(0.40, {})
    assert res2 is not None
    assert res2.severity == RiskSeverity.high

    # Slot miss count >= 3
    res3 = check_r1_adherence_drop(0.80, {"evening": 3})
    assert res3 is not None
    assert res3.rule_code == "R1_ADHERENCE_DROP"
    assert "evening" in res3.message


def test_r2_refill_soon():
    # 20 units, 2 per day = 10 days remaining (threshold 5) -> None
    assert check_r2_refill_soon(stock_count=20.0, doses_per_day=2.0, refill_threshold_days=5) is None

    # 8 units, 2 per day = 4 days remaining (threshold 5) -> Warning
    res1 = check_r2_refill_soon(stock_count=8.0, doses_per_day=2.0, refill_threshold_days=5, medication_name="Metformin")
    assert res1 is not None
    assert res1.rule_code == "R2_REFILL_SOON"
    assert res1.severity == RiskSeverity.warning
    assert "Metformin" in res1.message

    # 3 units, 2 per day = 1.5 days remaining -> High
    res2 = check_r2_refill_soon(stock_count=3.0, doses_per_day=2.0, refill_threshold_days=5)
    assert res2 is not None
    assert res2.severity == RiskSeverity.high


def test_r3_miss_and_vitals():
    # Non-critical miss or no vitals -> None
    assert check_r3_miss_and_vitals(critical_missed_24h=False, resting_hr=95, hr_7d_baseline=75) is None
    assert check_r3_miss_and_vitals(critical_missed_24h=True, resting_hr=None, hr_7d_baseline=75) is None

    # Critical missed, resting HR elevated 10% (under 15%) -> None
    assert check_r3_miss_and_vitals(critical_missed_24h=True, resting_hr=80, hr_7d_baseline=75) is None

    # Critical missed, resting HR elevated 20% (>= 15%) -> High
    res = check_r3_miss_and_vitals(critical_missed_24h=True, resting_hr=90, hr_7d_baseline=75)
    assert res is not None
    assert res.rule_code == "R3_MISS_AND_VITALS"
    assert res.severity == RiskSeverity.high
    assert "resting heart rate" in res.message


def test_r4_poor_sleep():
    # Only 1 night data -> None
    assert check_r4_poor_sleep([4.0]) is None

    # Normal sleep -> None
    assert check_r4_poor_sleep([7.0, 6.5]) is None

    # 2 consecutive nights < 5 hours -> Info
    res = check_r4_poor_sleep([4.5, 4.2])
    assert res is not None
    assert res.rule_code == "R4_POOR_SLEEP"
    assert res.severity == RiskSeverity.info
    assert "Less than 5 hours" in res.message


def test_r5_inactivity():
    wake = time(7, 0)
    # At 9:00 AM (2h past wake) -> None
    now_early = datetime(2026, 11, 15, 9, 0, tzinfo=timezone.utc)
    assert check_r5_inactivity(last_activity_at=None, wake_time=wake, now=now_early) is None

    # At 10:30 AM (3.5h past wake) and no activity -> High
    now_late = datetime(2026, 11, 15, 10, 30, tzinfo=timezone.utc)
    res = check_r5_inactivity(last_activity_at=None, wake_time=wake, now=now_late)
    assert res is not None
    assert res.rule_code == "R5_INACTIVITY"
    assert res.severity == RiskSeverity.high


def test_r6_duplicate_or_interaction():
    existing = ["Metformin", "Amlodipine"]
    rules = [
        {"drug_a": "Amlodipine", "drug_b": "Simvastatin", "severity": "moderate", "note": "May increase statin exposure."}
    ]

    # Clean new medication -> None
    assert check_r6_duplicate_or_interaction("Paracetamol", existing, rules) is None

    # Duplicate name check -> High
    res_dup = check_r6_duplicate_or_interaction("metformin", existing, rules)
    assert res_dup is not None
    assert res_dup.rule_code == "R6_DUPLICATE_MEDICATION"
    assert res_dup.severity == RiskSeverity.high

    # Curated interaction check -> Warning
    res_int = check_r6_duplicate_or_interaction("Simvastatin", existing, rules)
    assert res_int is not None
    assert res_int.rule_code == "R6_INTERACTION_ADVISORY"
    assert "statin exposure" in res_int.message
