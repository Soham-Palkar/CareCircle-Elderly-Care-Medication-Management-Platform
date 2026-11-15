"""Digital Twin Guardian service: unified profile, explainable rules, and forecasts."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.forecast import SlotHistory, build_forecast
from app.domain.risk_rules import (
    check_r1_adherence_drop,
    check_r2_refill_soon,
    check_r3_miss_and_vitals,
    check_r4_poor_sleep,
    check_r5_inactivity,
)
from app.domain.types import ReadingKind, ReadingSource
from app.models.health_reading import HealthReading
from app.models.risk_flag import RiskFlag
from app.repositories.appointment_repo import AppointmentRepository
from app.repositories.dose_repo import DoseRepository
from app.repositories.flag_repo import FlagRepository
from app.repositories.medication_repo import MedicationRepository
from app.repositories.reading_repo import ReadingRepository


class TwinService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.reading_repo = ReadingRepository(db, circle_id)
        self.flag_repo = FlagRepository(db, circle_id)
        self.dose_repo = DoseRepository(db, circle_id)
        self.med_repo = MedicationRepository(db, circle_id)
        self.appt_repo = AppointmentRepository(db, circle_id)

    async def record_reading(
        self,
        recipient_id: UUID,
        kind: str,
        value: float,
        source: str = "manual",
        recorded_at: datetime | None = None,
    ) -> HealthReading:
        reading = await self.reading_repo.create(
            recipient_id=recipient_id,
            data={
                "kind": ReadingKind(kind),
                "value": value,
                "source": ReadingSource(source),
                "recorded_at": recorded_at or datetime.now(timezone.utc),
            },
        )
        await self.db.commit()
        return reading

    async def evaluate_rules(self, recipient_id: UUID) -> list[RiskFlag]:
        created_flags: list[RiskFlag] = []
        now = datetime.now(timezone.utc)
        today = now.date()

        # R1: Adherence drop
        adh_data = await self.dose_repo.get_adherence_7d(recipient_id, today)
        r1_result = check_r1_adherence_drop(adh_data["adherence"], {})
        if r1_result and not await self.flag_repo.exists_open(recipient_id, r1_result.rule_code):
            flag = await self.flag_repo.create(recipient_id, {
                "rule_code": r1_result.rule_code,
                "severity": r1_result.severity.value,
                "message": r1_result.message,
                "evidence": r1_result.evidence,
            })
            created_flags.append(flag)

        # R2: Refill soon
        active_meds = await self.med_repo.list_active(recipient_id)
        for med in active_meds:
            # Estimate daily doses (assume 1 dose/day if no schedules)
            doses_day = float(len(med.schedules)) if med.schedules else 1.0
            r2_result = check_r2_refill_soon(
                stock_count=float(med.stock_count),
                doses_per_day=doses_day,
                refill_threshold_days=med.refill_threshold_days,
                medication_name=med.name,
            )
            if r2_result and not await self.flag_repo.exists_open(recipient_id, f"R2_{med.name}"):
                flag = await self.flag_repo.create(recipient_id, {
                    "rule_code": f"R2_{med.name}",
                    "severity": r2_result.severity.value,
                    "message": r2_result.message,
                    "evidence": r2_result.evidence,
                })
                created_flags.append(flag)

        # R3: Miss & vitals
        hr_reading = await self.reading_repo.get_latest_by_kind(recipient_id, ReadingKind.heart_rate)
        hr_baseline = await self.reading_repo.get_7d_baseline(recipient_id, ReadingKind.heart_rate)
        # Check if any dose was missed in 24h
        critical_missed = adh_data["missed"] > 0
        r3_result = check_r3_miss_and_vitals(
            critical_missed_24h=critical_missed,
            resting_hr=float(hr_reading.value) if hr_reading else None,
            hr_7d_baseline=hr_baseline,
        )
        if r3_result and not await self.flag_repo.exists_open(recipient_id, r3_result.rule_code):
            flag = await self.flag_repo.create(recipient_id, {
                "rule_code": r3_result.rule_code,
                "severity": r3_result.severity.value,
                "message": r3_result.message,
                "evidence": r3_result.evidence,
            })
            created_flags.append(flag)

        # R4: Poor sleep
        sleep_readings = await self.reading_repo.get_history(recipient_id, ReadingKind.sleep_hours, days=3)
        sleep_hours = [float(r.value) for r in sleep_readings]
        r4_result = check_r4_poor_sleep(sleep_hours)
        if r4_result and not await self.flag_repo.exists_open(recipient_id, r4_result.rule_code):
            flag = await self.flag_repo.create(recipient_id, {
                "rule_code": r4_result.rule_code,
                "severity": r4_result.severity.value,
                "message": r4_result.message,
                "evidence": r4_result.evidence,
            })
            created_flags.append(flag)

        await self.db.commit()
        return created_flags

    async def get_forecast(self, recipient_id: UUID) -> list[dict]:
        now = datetime.now(timezone.utc)
        # Fetch next 48h scheduled events
        events = await self.dose_repo.list_for_recipient(
            recipient_id,
            from_dt=now,
            to_dt=now + timedelta(hours=48),
        )

        upcoming_slots = []
        for ev in events:
            hour = ev.scheduled_at.hour
            label = "Morning" if hour < 12 else "Afternoon" if hour < 17 else "Evening" if hour < 21 else "Bedtime"
            upcoming_slots.append((label, ev.scheduled_at))

        # Dummy or stored histories for demo forecast
        sample_histories = [
            SlotHistory(slot_label="Evening", weekday=now.weekday(), missed=3, total=7),
            SlotHistory(slot_label="Morning", weekday=now.weekday(), missed=1, total=7),
            SlotHistory(slot_label="Afternoon", weekday=now.weekday(), missed=0, total=7),
        ]

        forecast_slots = build_forecast(sample_histories, upcoming_slots)
        return [
            {
                "slot_label": f.slot_label,
                "scheduled_at": f.scheduled_at,
                "miss_risk": f.miss_risk,
                "explanation": f.explanation,
                "risk_level": f.risk_level,
            }
            for f in forecast_slots
        ]

    async def get_profile(self, recipient_id: UUID) -> dict[str, Any]:
        latest_readings = {}
        for k in ReadingKind:
            r = await self.reading_repo.get_latest_by_kind(recipient_id, k)
            if r:
                latest_readings[k.value] = {
                    "id": r.id,
                    "recipient_id": r.recipient_id,
                    "kind": r.kind.value,
                    "value": r.value,
                    "recorded_at": r.recorded_at,
                    "source": r.source.value,
                }

        open_flags = await self.flag_repo.get_open_flags(recipient_id)
        forecast_slots = await self.get_forecast(recipient_id)
        appts = await self.appt_repo.list_upcoming(recipient_id, datetime.now(timezone.utc))
        adh = await self.dose_repo.get_adherence_7d(recipient_id, datetime.now(timezone.utc).date())

        return {
            "recipient_id": recipient_id,
            "latest_readings": latest_readings,
            "open_flags": open_flags,
            "forecast_24h": forecast_slots,
            "upcoming_appointments": appts,
            "adherence_7d": adh["adherence"],
            "advisory_notice": "Advisory: this health profile is for care coordination only. Discuss any concerns with your doctor.",
        }
