"""Simulate live biometric readings for the Digital Twin during demos."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
import os
import random
import sys
import uuid

# Ensure backend is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.recipient import CareRecipient
from app.models.health_reading import HealthReading, ReadingKind, ReadingSource


async def simulate_once() -> None:
    async with AsyncSessionLocal() as session:
        # Find recipient
        res = await session.execute(select(CareRecipient))
        recipient = res.scalars().first()
        if not recipient:
            print("No CareRecipient found in database. Please run scripts/seed_demo.py first.")
            return

        now = datetime.now(timezone.utc)
        # Generate simulated values
        sim_hr = Decimal(str(random.randint(68, 88)))
        sim_steps = Decimal(str(random.randint(2000, 5500)))
        sim_sleep = Decimal(str(round(random.uniform(5.5, 8.0), 1)))

        readings = [
            HealthReading(
                id=uuid.uuid4(),
                recipient_id=recipient.id,
                kind=ReadingKind.heart_rate,
                value=sim_hr,
                recorded_at=now,
                source=ReadingSource.simulated,
            ),
            HealthReading(
                id=uuid.uuid4(),
                recipient_id=recipient.id,
                kind=ReadingKind.steps,
                value=sim_steps,
                recorded_at=now,
                source=ReadingSource.simulated,
            ),
            HealthReading(
                id=uuid.uuid4(),
                recipient_id=recipient.id,
                kind=ReadingKind.sleep_hours,
                value=sim_sleep,
                recorded_at=now,
                source=ReadingSource.simulated,
            ),
        ]

        session.add_all(readings)
        await session.commit()
        print(f"Simulated readings saved: HR={sim_hr} bpm, Steps={sim_steps}, Sleep={sim_sleep}h (Source: simulated)")


if __name__ == "__main__":
    asyncio.run(simulate_once())
