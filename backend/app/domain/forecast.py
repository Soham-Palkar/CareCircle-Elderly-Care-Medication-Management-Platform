"""forecast.py — Per-slot miss risk forecasting using Laplace smoothing.

Formula:
    miss_risk = (missed + 1) / (total + 2)
Where:
    - missed = count of missed doses for this slot / weekday over history
    - total  = count of all scheduled occurrences for this slot / weekday
    - Laplace smoothing prevents 0% or 100% certainty from small sample sizes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from app.domain.types import ForecastSlot


@dataclass(frozen=True)
class SlotHistory:
    slot_label: str  # e.g. "morning", "afternoon", "evening", "bedtime"
    weekday: int  # 0=Monday ... 6=Sunday
    missed: int
    total: int


def compute_miss_risk(missed: int, total: int) -> float:
    """Laplace-smoothed probability of a missed dose."""
    return (missed + 1.0) / (total + 2.0)


def classify_risk(prob: float) -> str:
    """Return low, medium, or high string."""
    if prob < 0.30:
        return "low"
    elif prob < 0.60:
        return "medium"
    return "high"


WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def build_forecast(
    slot_histories: Sequence[SlotHistory],
    upcoming_slots: Sequence[tuple[str, datetime]],
) -> list[ForecastSlot]:
    """Build ForecastSlot objects for upcoming slots in the next 24-48 hours."""
    # Index histories by (slot_label.lower(), weekday)
    history_map: dict[tuple[str, int], SlotHistory] = {
        (h.slot_label.lower(), h.weekday): h for h in slot_histories
    }

    forecasts: list[ForecastSlot] = []
    for slot_label, scheduled_at in upcoming_slots:
        wday = scheduled_at.weekday()
        key = (slot_label.lower(), wday)
        hist = history_map.get(key)

        if hist and hist.total > 0:
            risk = compute_miss_risk(hist.missed, hist.total)
            wday_name = WEEKDAY_NAMES[wday]
            explanation = (
                f"Historical adherence for {slot_label.title()} doses on {wday_name}s: "
                f"missed {hist.missed} of {hist.total} scheduled occasions."
            )
        else:
            # Prior with no history: 1/2 = 0.50
            risk = 0.33
            explanation = f"Baseline forecast for {slot_label.title()} dose (limited past history)."

        level = classify_risk(risk)
        forecasts.append(
            ForecastSlot(
                slot_label=slot_label,
                scheduled_at=scheduled_at,
                miss_risk=round(risk, 2),
                explanation=explanation,
                risk_level=level,
            )
        )

    return forecasts
