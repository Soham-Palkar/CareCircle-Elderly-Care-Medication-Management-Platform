"""Seed demo data for CareCircle platform.

Creates:
- Demo CareCircle: 'Sharma Family' (code: 'DEMO-CIRCLE')
- Recipient: Devi Sharma
- 3 Members: Devi (elder), Priya (caretaker), Raj (family)
- 4 Medications with Schedules (Metformin, Amlodipine, Atorvastatin, Vitamin D3)
- 14 Days of Dose History (realistic adherence pattern)
- Baseline Health Readings (heart rate, sleep, steps)
- Upcoming Appointment with Dr. Ananya Sen
- Curated Interaction Rules
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
import json
import os
import sys
import uuid

# Ensure backend is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import select
from app.core.security import hash_passcode
from app.db.session import AsyncSessionLocal
from app.models.circle import CareCircle
from app.models.recipient import CareRecipient
from app.models.member import Member, Role
from app.models.permission import MemberPermission
from app.models.medication import Medication, MedicationCriticality, MedicationStatus, MedicationSource
from app.models.schedule import MedicationSchedule, ScheduleKind
from app.models.dose_event import DoseEvent, DoseState, DoseRecordedVia
from app.models.appointment import Appointment, AppointmentStatus
from app.models.health_reading import HealthReading, ReadingKind, ReadingSource
from app.models.interaction_rule import InteractionRule
from app.models.streak import Streak
from app.models.adherence_daily import AdherenceDaily


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        res = await session.execute(select(CareCircle).where(CareCircle.circle_code == "DEMO-CIRCLE"))
        existing = res.scalar_one_or_none()
        if existing:
            print("Demo circle 'DEMO-CIRCLE' already exists. Skipping seed.")
            return

        print("Seeding CareCircle demo data...")
        now_utc = datetime.now(timezone.utc)
        today = now_utc.date()

        # 1. Circle
        circle = CareCircle(
            id=uuid.uuid4(),
            name="Sharma Family",
            circle_code="DEMO-CIRCLE",
            created_at=now_utc - timedelta(days=30),
        )
        session.add(circle)
        await session.flush()

        # 2. Recipient
        recipient = CareRecipient(
            id=uuid.uuid4(),
            circle_id=circle.id,
            full_name="Devi Sharma",
            date_of_birth=date(1952, 4, 15),
            timezone="Asia/Kolkata",
            language="en",
            wake_time=time(7, 0),
            sleep_time=time(22, 0),
            routine_times={
                "wake": "07:00",
                "breakfast": "08:30",
                "lunch": "13:30",
                "dinner": "20:30",
                "bedtime": "22:00",
            },
            created_at=now_utc - timedelta(days=30),
            updated_at=now_utc - timedelta(days=30),
        )
        session.add(recipient)
        await session.flush()

        # Streak
        streak = Streak(
            recipient_id=recipient.id,
            current_streak=5,
            best_streak=12,
            last_date=today - timedelta(days=1),
        )
        session.add(streak)

        # 3. Members
        passcode_hash = hash_passcode("123456")

        # Elder: Devi
        elder = Member(
            id=uuid.uuid4(),
            circle_id=circle.id,
            display_name="Devi Sharma",
            role=Role.elder,
            passcode_hash=passcode_hash,
            email="devi@example.com",
            notify_prefs={"email_enabled": True, "telegram_enabled": False},
            created_at=now_utc - timedelta(days=30),
            updated_at=now_utc - timedelta(days=30),
        )
        session.add(elder)
        await session.flush()

        elder_perms = MemberPermission(
            member_id=elder.id,
            can_view_meds=True,
            can_edit_meds=True,
            can_mark_doses=True,
            can_view_appointments=True,
            can_edit_appointments=True,
            can_view_health=True,
            receives_alerts=True,
            alert_level_min=1,
        )
        session.add(elder_perms)

        # Caretaker: Priya
        caretaker = Member(
            id=uuid.uuid4(),
            circle_id=circle.id,
            display_name="Priya Sharma",
            role=Role.caretaker,
            passcode_hash=passcode_hash,
            email="priya@example.com",
            notify_prefs={"email_enabled": True, "telegram_enabled": False},
            created_at=now_utc - timedelta(days=30),
            updated_at=now_utc - timedelta(days=30),
        )
        session.add(caretaker)
        await session.flush()

        caretaker_perms = MemberPermission(
            member_id=caretaker.id,
            can_view_meds=True,
            can_edit_meds=True,
            can_mark_doses=True,
            can_view_appointments=True,
            can_edit_appointments=True,
            can_view_health=True,
            receives_alerts=True,
            alert_level_min=1,
        )
        session.add(caretaker_perms)

        # Family: Raj
        family = Member(
            id=uuid.uuid4(),
            circle_id=circle.id,
            display_name="Raj Sharma",
            role=Role.family,
            passcode_hash=passcode_hash,
            email="raj@example.com",
            notify_prefs={"email_enabled": True, "telegram_enabled": False},
            created_at=now_utc - timedelta(days=30),
            updated_at=now_utc - timedelta(days=30),
        )
        session.add(family)
        await session.flush()

        family_perms = MemberPermission(
            member_id=family.id,
            can_view_meds=True,
            can_edit_meds=False,
            can_mark_doses=False,
            can_view_appointments=True,
            can_edit_appointments=False,
            can_view_health=False,
            receives_alerts=True,
            alert_level_min=2,
        )
        session.add(family_perms)

        # 4. Medications & Schedules
        meds_data = [
            {
                "name": "Metformin",
                "strength": "500mg",
                "instructions": "Take with breakfast and dinner",
                "criticality": MedicationCriticality.normal,
                "dose_quantity": Decimal("1.0"),
                "stock_count": Decimal("38.0"),
                "refill_threshold_days": 5,
                "purpose": "Blood sugar regulation",
                "food_warning": "Take immediately after food",
                "schedules": [
                    {"kind": ScheduleKind.routine_anchor, "anchor": "breakfast", "time": None},
                    {"kind": ScheduleKind.routine_anchor, "anchor": "dinner", "time": None},
                ],
            },
            {
                "name": "Amlodipine",
                "strength": "5mg",
                "instructions": "Take every morning at 8:00 AM",
                "criticality": MedicationCriticality.critical,
                "dose_quantity": Decimal("1.0"),
                "stock_count": Decimal("24.0"),
                "refill_threshold_days": 7,
                "purpose": "Blood pressure management",
                "food_warning": "Can be taken with or without food",
                "schedules": [
                    {"kind": ScheduleKind.fixed_time, "anchor": None, "time": time(8, 0)},
                ],
            },
            {
                "name": "Atorvastatin",
                "strength": "20mg",
                "instructions": "Take at bedtime",
                "criticality": MedicationCriticality.normal,
                "dose_quantity": Decimal("1.0"),
                "stock_count": Decimal("18.0"),
                "refill_threshold_days": 5,
                "purpose": "Cholesterol control",
                "food_warning": "Take at bedtime with water",
                "schedules": [
                    {"kind": ScheduleKind.routine_anchor, "anchor": "bedtime", "time": None},
                ],
            },
            {
                "name": "Vitamin D3",
                "strength": "1000 IU",
                "instructions": "Take after lunch",
                "criticality": MedicationCriticality.normal,
                "dose_quantity": Decimal("1.0"),
                "stock_count": Decimal("3.0"),  # Low stock to test R2 refill warning!
                "refill_threshold_days": 5,
                "purpose": "Bone density support",
                "food_warning": "Take with meal containing dietary fat",
                "schedules": [
                    {"kind": ScheduleKind.routine_anchor, "anchor": "lunch", "time": None},
                ],
            },
        ]

        created_schedules: list[tuple[Medication, MedicationSchedule]] = []

        for m_data in medss_data if "medss_data" in locals() else meds_data:
            med = Medication(
                id=uuid.uuid4(),
                recipient_id=recipient.id,
                name=m_data["name"],
                strength=m_data["strength"],
                form="tablet",
                instructions=m_data["instructions"],
                criticality=m_data["criticality"],
                dose_quantity=m_data["dose_quantity"],
                stock_count=m_data["stock_count"],
                refill_threshold_days=m_data["refill_threshold_days"],
                status=MedicationStatus.active,
                source=MedicationSource.manual,
                confirmed_with_doctor=True,
                purpose_card={
                    "purpose": m_data["purpose"],
                    "instructions": m_data["instructions"],
                    "food_warning": m_data["food_warning"],
                    "cautions": "Follow prescription directions carefully.",
                    "disclaimer": "Advisory information only. Follow your prescribing doctor's exact instructions.",
                },
                created_by=caretaker.id,
                created_at=now_utc - timedelta(days=20),
                updated_at=now_utc - timedelta(days=20),
            )
            session.add(med)
            await session.flush()

            for s_info in m_data["schedules"]:
                sched = MedicationSchedule(
                    id=uuid.uuid4(),
                    medication_id=med.id,
                    kind=s_info["kind"],
                    time_of_day=s_info["time"],
                    anchor=s_info["anchor"],
                    anchor_offset_min=0,
                    days_of_week=127,
                    start_date=today - timedelta(days=20),
                    grace_minutes=60,
                    is_active=True,
                    created_at=now_utc - timedelta(days=20),
                    updated_at=now_utc - timedelta(days=20),
                )
                session.add(sched)
                await session.flush()
                created_schedules.append((med, sched))

        # 5. 14 Days of Dose History
        # Generate dose events for the last 14 days
        for day_offset in range(14, 0, -1):
            past_date = today - timedelta(days=day_offset)
            daily_taken = 0
            daily_scheduled = 0

            for med, sched in created_schedules:
                daily_scheduled += 1
                # Realistic adherence: ~85% taken, occasional snooze or miss on evening dose
                sched_hour = 8 if sched.time_of_day else (
                    8 if sched.anchor == "breakfast" else (
                        13 if sched.anchor == "lunch" else (
                            20 if sched.anchor == "dinner" else 22
                        )
                    )
                )
                sched_dt = datetime(past_date.year, past_date.month, past_date.day, sched_hour, 0, tzinfo=timezone.utc)

                # Simulate miss on day 3 and 7 for evening dose
                is_miss = (day_offset in (3, 7)) and (sched.anchor in ("dinner", "bedtime"))
                if is_miss:
                    state = DoseState.missed
                    taken_at = None
                else:
                    state = DoseState.taken
                    taken_at = sched_dt + timedelta(minutes=15)
                    daily_taken += 1

                event = DoseEvent(
                    id=uuid.uuid4(),
                    schedule_id=sched.id,
                    medication_id=med.id,
                    recipient_id=recipient.id,
                    scheduled_at=sched_dt,
                    state=state,
                    escalation_level=2 if is_miss else 0,
                    taken_at=taken_at,
                    recorded_by=elder.id if state == DoseState.taken else None,
                    recorded_via=DoseRecordedVia.app,
                    created_at=sched_dt,
                    updated_at=sched_dt,
                )
                session.add(event)

            # Record daily aggregate
            adh_record = AdherenceDaily(
                recipient_id=recipient.id,
                date=past_date,
                scheduled_count=daily_scheduled,
                taken_count=daily_taken,
                missed_count=daily_scheduled - daily_taken,
            )
            session.add(adh_record)

        # 6. Appointments
        appt = Appointment(
            id=uuid.uuid4(),
            circle_id=circle.id,
            recipient_id=recipient.id,
            doctor_name="Dr. Ananya Sen",
            specialty="Cardiologist",
            location="Apollo Heart Centre, Clinic 302",
            scheduled_at=now_utc + timedelta(days=4, hours=2),
            notes="Routine blood pressure checkup and lipid panel review.",
            status=AppointmentStatus.upcoming,
            reminder_offsets_min=[1440, 120],
            created_by=caretaker.id,
            created_at=now_utc - timedelta(days=5),
            updated_at=now_utc - timedelta(days=5),
        )
        session.add(appt)

        # 7. Health Readings (Baseline vitals for digital twin)
        readings_data = [
            (ReadingKind.heart_rate, Decimal("72.0"), ReadingSource.device),
            (ReadingKind.heart_rate, Decimal("74.0"), ReadingSource.device),
            (ReadingKind.sleep_hours, Decimal("6.8"), ReadingSource.device),
            (ReadingKind.sleep_hours, Decimal("7.1"), ReadingSource.device),
            (ReadingKind.steps, Decimal("3800.0"), ReadingSource.device),
            (ReadingKind.bp_sys, Decimal("128.0"), ReadingSource.manual),
            (ReadingKind.bp_dia, Decimal("82.0"), ReadingSource.manual),
        ]
        for kind, val, src in readings_data:
            reading = HealthReading(
                id=uuid.uuid4(),
                recipient_id=recipient.id,
                kind=kind,
                value=val,
                recorded_at=now_utc - timedelta(hours=6),
                source=src,
            )
            session.add(reading)

        # 8. Load Curated Drug Interaction Rules
        rules_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "backend", "app", "db", "seed_data", "interaction_rules.json")
        )
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8") as f:
                rules = json.load(f)
                for r in rules:
                    rule_obj = InteractionRule(
                        id=uuid.uuid4(),
                        drug_a=r["drug_a"],
                        drug_b=r["drug_b"],
                        severity=r.get("severity", "moderate"),
                        note=r.get("note", ""),
                    )
                    session.add(rule_obj)

        await session.commit()
        print("Demo seed complete! Circle code: DEMO-CIRCLE, Passcode: 123456")


if __name__ == "__main__":
    asyncio.run(seed())
