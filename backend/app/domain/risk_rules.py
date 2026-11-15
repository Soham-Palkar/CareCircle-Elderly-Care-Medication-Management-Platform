"""risk_rules.py — Explainable Digital Twin rule engine (R1 to R6).

All rules are pure functions that evaluate domain data and produce
a RiskFlagResult or None. No clinical diagnosis is ever made or implied.
Every generated flag includes explicit evidence and an advisory notice.
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Sequence

from app.domain.types import RiskFlagResult, RiskSeverity

ADVISORY_NOTICE = "Advisory: this coordination flag is rule-based and not medical advice. Discuss with your doctor."


def check_r1_adherence_drop(
    adherence_7d: float,
    slot_misses_7d: dict[str, int],
) -> RiskFlagResult | None:
    """R1 ADHERENCE_DROP: 7-day adherence below 70%, or same slot missed 3+ times."""
    if adherence_7d < 0.70:
        return RiskFlagResult(
            rule_code="R1_ADHERENCE_DROP",
            severity=RiskSeverity.high if adherence_7d < 0.50 else RiskSeverity.warning,
            message=f"{ADVISORY_NOTICE} 7-day medication adherence has dropped to {int(adherence_7d * 100)}%.",
            evidence={
                "adherence_7d": round(adherence_7d, 2),
                "threshold": 0.70,
            },
        )

    for slot, misses in slot_misses_7d.items():
        if misses >= 3:
            return RiskFlagResult(
                rule_code="R1_ADHERENCE_DROP",
                severity=RiskSeverity.warning,
                message=f"{ADVISORY_NOTICE} The {slot} dose slot was missed {misses} times over the past 7 days.",
                evidence={
                    "slot": slot,
                    "misses_7d": misses,
                    "threshold": 3,
                },
            )

    return None


def check_r2_refill_soon(
    stock_count: float,
    doses_per_day: float,
    refill_threshold_days: int = 5,
    medication_name: str = "Medication",
) -> RiskFlagResult | None:
    """R2 REFILL_SOON: remaining stock lasts <= refill_threshold_days."""
    if doses_per_day <= 0:
        return None

    days_remaining = stock_count / doses_per_day
    if days_remaining <= refill_threshold_days:
        severity = RiskSeverity.high if days_remaining <= 2 else RiskSeverity.warning
        return RiskFlagResult(
            rule_code="R2_REFILL_SOON",
            severity=severity,
            message=f"{ADVISORY_NOTICE} {medication_name} has approximately {int(days_remaining)} days of doses remaining ({stock_count:.0f} units).",
            evidence={
                "stock_count": stock_count,
                "doses_per_day": doses_per_day,
                "days_remaining": round(days_remaining, 1),
                "threshold_days": refill_threshold_days,
            },
        )

    return None


def check_r3_miss_and_vitals(
    critical_missed_24h: bool,
    resting_hr: float | None,
    hr_7d_baseline: float | None,
) -> RiskFlagResult | None:
    """R3 MISS_AND_VITALS: Critical dose missed in 24h and resting HR 15% above 7d baseline."""
    if not critical_missed_24h or resting_hr is None or hr_7d_baseline is None or hr_7d_baseline <= 0:
        return None

    elevation = (resting_hr - hr_7d_baseline) / hr_7d_baseline
    if elevation >= 0.15:
        return RiskFlagResult(
            rule_code="R3_MISS_AND_VITALS",
            severity=RiskSeverity.high,
            message=(
                f"{ADVISORY_NOTICE} A critical medication was missed in the last 24h, and recorded resting heart rate "
                f"({int(resting_hr)} bpm) is elevated {int(elevation * 100)}% above the 7-day baseline."
            ),
            evidence={
                "critical_missed_24h": True,
                "resting_hr": resting_hr,
                "baseline_hr": hr_7d_baseline,
                "elevation_pct": round(elevation * 100, 1),
            },
        )

    return None


def check_r4_poor_sleep(
    sleep_hours_last_2_nights: Sequence[float],
) -> RiskFlagResult | None:
    """R4 POOR_SLEEP: Under 5 hours of sleep for 2 consecutive recorded nights."""
    if len(sleep_hours_last_2_nights) < 2:
        return None

    recent_two = sleep_hours_last_2_nights[-2:]
    if all(h < 5.0 for h in recent_two):
        return RiskFlagResult(
            rule_code="R4_POOR_SLEEP",
            severity=RiskSeverity.info,
            message=(
                f"{ADVISORY_NOTICE} Less than 5 hours of sleep recorded for two consecutive nights "
                f"({recent_two[0]}h, {recent_two[1]}h). Fatigue may increase risk of missing morning routines."
            ),
            evidence={
                "sleep_hours": list(recent_two),
                "threshold_hours": 5.0,
            },
        )

    return None


def check_r5_inactivity(
    last_activity_at: datetime | None,
    wake_time: time,
    now: datetime,
) -> RiskFlagResult | None:
    """R5 INACTIVITY: No check-in or app activity by wake_time + 3 hours."""
    # Compare only within today
    now_time = now.time()
    wake_minutes = wake_time.hour * 60 + wake_time.minute
    now_minutes = now_time.hour * 60 + now_time.minute

    # If it is at least 3 hours (180 mins) past wake_time today
    if now_minutes >= wake_minutes + 180:
        if last_activity_at is None or (now - last_activity_at).total_seconds() > 180 * 60:
            return RiskFlagResult(
                rule_code="R5_INACTIVITY",
                severity=RiskSeverity.high,
                message=(
                    f"{ADVISORY_NOTICE} No activity or dose confirmation recorded 3 hours after scheduled wake time "
                    f"({wake_time.strftime('%H:%M')}). Caretaker check-in recommended."
                ),
                evidence={
                    "wake_time": wake_time.strftime("%H:%M"),
                    "hours_elapsed": round((now_minutes - wake_minutes) / 60.0, 1),
                },
            )

    return None


def check_r6_duplicate_or_interaction(
    new_med_name: str,
    existing_med_names: Sequence[str],
    interaction_rules: Sequence[dict],
) -> RiskFlagResult | None:
    """R6 DUPLICATE_OR_INTERACTION: Duplicate drug name or known curated interaction pair."""
    new_clean = new_med_name.strip().lower()

    # 1. Exact or near duplicate check
    for existing in existing_med_names:
        if existing.strip().lower() == new_clean:
            return RiskFlagResult(
                rule_code="R6_DUPLICATE_MEDICATION",
                severity=RiskSeverity.high,
                message=f"{ADVISORY_NOTICE} A medication named '{existing}' is already in the active schedule. Please check for accidental duplicate entry.",
                evidence={
                    "duplicate_name": existing,
                },
            )

    # 2. Curated interaction check
    for rule in interaction_rules:
        drug_a = rule.get("drug_a", "").lower()
        drug_b = rule.get("drug_b", "").lower()
        if (new_clean in drug_a and any(drug_b in e.lower() for e in existing_med_names)) or (
            new_clean in drug_b and any(drug_a in e.lower() for e in existing_med_names)
        ):
            sev_str = rule.get("severity", "warning").lower()
            severity = RiskSeverity.high if "high" in sev_str else RiskSeverity.warning
            return RiskFlagResult(
                rule_code="R6_INTERACTION_ADVISORY",
                severity=severity,
                message=f"{ADVISORY_NOTICE} Known advisory interaction: {rule.get('note', '')}",
                evidence={
                    "drug_pair": [rule.get("drug_a"), rule.get("drug_b")],
                    "severity": sev_str,
                    "curated_note": rule.get("note"),
                },
            )

    return None
