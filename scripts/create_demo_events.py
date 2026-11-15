"""Create dose events due in 1 to 2 minutes for the live escalation demo."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import os
import sys
import uuid

# Ensure backend is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.medication import Medication
from app.models.schedule import MedicationSchedule
from app.models.dose_event import DoseEvent, DoseState, DoseRecordedVia


def check_not_production() -> None:
    env = os.environ.get("APP_ENV", os.environ.get("ENV", "dev")).strip().lower()
    if env in ("prod", "production"):
        print("ERROR: Safety Guard: create_demo_events.py cannot be executed in a production environment (APP_ENV=production). Aborting.")
        sys.exit(1)


async def create_demo_event() -> None:
    check_not_production()
    async with AsyncSessionLocal() as session:
        # Find active medication schedule
        res = await session.execute(
            select(Medication, MedicationSchedule)
            .join(MedicationSchedule, Medication.id == MedicationSchedule.medication_id)
            .where(MedicationSchedule.is_active == True)
        )
        row = res.first()
        if not row:
            print("No active medication schedule found. Run seed_demo.py first.")
            return

        med, sched = row
        now = datetime.now(timezone.utc)
        # Scheduled 1 minute ago so it's immediately due for reminder
        due_time = now - timedelta(minutes=1)

        event = DoseEvent(
            id=uuid.uuid4(),
            schedule_id=sched.id,
            medication_id=med.id,
            recipient_id=med.recipient_id,
            scheduled_at=due_time,
            state=DoseState.scheduled,
            escalation_level=0,
            recorded_via=DoseRecordedVia.app,
            created_at=now,
            updated_at=now,
        )

        session.add(event)
        await session.commit()
        print(f"Created demo dose event {event.id} for {med.name} due at {due_time.isoformat()}")


if __name__ == "__main__":
    asyncio.run(create_demo_event())
