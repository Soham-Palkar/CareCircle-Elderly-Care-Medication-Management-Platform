"""InteractionRule entity for curated drug interactions."""

from __future__ import annotations

import uuid

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin


class InteractionRule(UUIDMixin, Base):
    __tablename__ = "interaction_rules"

    drug_a: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    drug_b: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="moderate", nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
