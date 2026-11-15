"""CareRecipient entity representing the elderly individual."""

from __future__ import annotations

import uuid
from datetime import date, time

from sqlalchemy import Date, ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class CareRecipient(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "care_recipients"

    circle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_circles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    wake_time: Mapped[time | None] = mapped_column(Time, default=time(7, 0), nullable=True)
    sleep_time: Mapped[time | None] = mapped_column(Time, default=time(22, 0), nullable=True)
    routine_times: Mapped[dict] = mapped_column(
        JSONB,
        default=lambda: {
            "wake": "07:00",
            "breakfast": "08:30",
            "lunch": "13:30",
            "dinner": "20:30",
            "bedtime": "22:00",
        },
        nullable=False,
    )

    # Relationships
    circle: Mapped[CareCircle] = relationship("CareCircle", back_populates="recipient")
    medications: Mapped[list[Medication]] = relationship("Medication", back_populates="recipient")
    appointments: Mapped[list[Appointment]] = relationship("Appointment", back_populates="recipient")
    health_readings: Mapped[list[HealthReading]] = relationship("HealthReading", back_populates="recipient")
    risk_flags: Mapped[list[RiskFlag]] = relationship("RiskFlag", back_populates="recipient")
    streak: Mapped[Streak] = relationship("Streak", back_populates="recipient", uselist=False)
