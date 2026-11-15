"""MedicationSchedule entity supporting versioning and routine anchors."""

from __future__ import annotations

import enum
import uuid
from datetime import date, time

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, SmallInteger, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ScheduleKind(str, enum.Enum):
    fixed_time = "fixed_time"
    routine_anchor = "routine_anchor"


class MedicationSchedule(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "medication_schedules"

    medication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[ScheduleKind] = mapped_column(
        Enum(ScheduleKind, name="schedule_kind_enum", values_callable=lambda x: [e.value for e in x]),
        default=ScheduleKind.fixed_time,
        nullable=False,
    )
    time_of_day: Mapped[time | None] = mapped_column(Time, nullable=True)
    anchor: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. "breakfast", "dinner"
    anchor_offset_min: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    days_of_week: Mapped[int] = mapped_column(SmallInteger, default=127, nullable=False)  # Bitmask (127 = all 7 days)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    grace_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medication_schedules.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    medication: Mapped[Medication] = relationship("Medication", back_populates="schedules")
    dose_events: Mapped[list[DoseEvent]] = relationship("DoseEvent", back_populates="schedule")
