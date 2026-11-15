"""DoseEvent entity tracking every scheduled and recorded medication dose."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class DoseState(str, enum.Enum):
    scheduled = "scheduled"
    reminded = "reminded"
    snoozed = "snoozed"
    taken = "taken"
    taken_late = "taken_late"
    skipped = "skipped"
    missed = "missed"


class DoseRecordedVia(str, enum.Enum):
    app = "app"
    voice = "voice"
    telegram = "telegram"
    email_link = "email_link"
    caretaker = "caretaker"


class DoseEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "dose_events"
    __table_args__ = (
        UniqueConstraint("schedule_id", "scheduled_at", name="uq_dose_schedule_time"),
        Index("ix_dose_events_state_scheduled_at", "state", "scheduled_at"),
        Index("ix_dose_events_recipient_scheduled", "recipient_id", "scheduled_at"),
    )

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medication_schedules.id", ondelete="CASCADE"),
        nullable=False,
    )
    medication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medications.id", ondelete="CASCADE"),
        nullable=False,
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_recipients.id", ondelete="CASCADE"),
        nullable=False,
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    state: Mapped[DoseState] = mapped_column(
        Enum(DoseState, name="dose_state_enum", values_callable=lambda x: [e.value for e in x]),
        default=DoseState.scheduled,
        nullable=False,
    )
    escalation_level: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    snooze_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    taken_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
    )
    recorded_via: Mapped[DoseRecordedVia] = mapped_column(
        Enum(DoseRecordedVia, name="dose_recorded_via_enum", values_callable=lambda x: [e.value for e in x]),
        default=DoseRecordedVia.app,
        nullable=False,
    )
    skip_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True, index=True)

    # Relationships
    schedule: Mapped[MedicationSchedule] = relationship("MedicationSchedule", back_populates="dose_events")
    medication: Mapped[Medication] = relationship("Medication", back_populates="dose_events")
