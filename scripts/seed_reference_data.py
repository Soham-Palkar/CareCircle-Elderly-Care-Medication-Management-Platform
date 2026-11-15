"""Seed clinical reference data (Drug Interaction Rules) for production or development.

This script contains NO demo records, NO user data, and NO passcodes.
It only populates the curated interaction knowledge base needed by Rule R6.
Idempotent: skips rules that are already present.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid

# Ensure backend is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.interaction_rule import InteractionRule


async def seed_reference_data() -> None:
    rules_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "backend",
            "app",
            "db",
            "seed_data",
            "interaction_rules.json",
        )
    )

    if not os.path.exists(rules_path):
        print(f"Error: interaction rules file not found at {rules_path}")
        sys.exit(1)

    with open(rules_path, "r", encoding="utf-8") as f:
        rules = json.load(f)

    inserted = 0
    async with AsyncSessionLocal() as session:
        for r in rules:
            drug_a = r["drug_a"].strip()
            drug_b = r["drug_b"].strip()

            # Check if this pair already exists (either orientation)
            stmt = select(InteractionRule).where(
                (InteractionRule.drug_a.ilike(drug_a) & InteractionRule.drug_b.ilike(drug_b))
                | (InteractionRule.drug_a.ilike(drug_b) & InteractionRule.drug_b.ilike(drug_a))
            )
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()

            if not existing:
                rule_obj = InteractionRule(
                    id=uuid.uuid4(),
                    drug_a=drug_a,
                    drug_b=drug_b,
                    severity=r.get("severity", "moderate"),
                    note=r.get("note", ""),
                )
                session.add(rule_obj)
                inserted += 1

        if inserted > 0:
            await session.commit()
            print(f"Successfully seeded {inserted} clinical interaction rules.")
        else:
            print("All reference interaction rules are already present in the database.")


if __name__ == "__main__":
    asyncio.run(seed_reference_data())
