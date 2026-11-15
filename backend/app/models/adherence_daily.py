"""AdherenceDaily aggregate table for fast dashboard queries."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AdherenceDaily(Base):
    __tablename__ = "adherence_daily"
    __table_args__ = (
        PrimaryKeyConstraint("recipient_id", "date", name="pk_adherence_daily"),
    )

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_recipients.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    scheduled_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    taken_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    missed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
