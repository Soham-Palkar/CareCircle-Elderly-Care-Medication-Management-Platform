"""Appointment entity."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class AppointmentStatus(str, enum.Enum):
    upcoming = "upcoming"
    done = "done"
    cancelled = "cancelled"


class Appointment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_recipient_scheduled", "recipient_id", "scheduled_at"),
    )

    circle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_circles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_recipients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doctor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    location: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointment_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=AppointmentStatus.upcoming,
        nullable=False,
        index=True,
    )
    reminder_offsets_min: Mapped[list[int]] = mapped_column(
        JSONB,
        default=lambda: [1440, 120],  # 24h and 2h before
        nullable=False,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    recipient: Mapped[CareRecipient] = relationship("CareRecipient", back_populates="appointments")
