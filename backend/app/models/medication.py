"""Medication entity."""

from __future__ import annotations

import enum
import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class MedicationCriticality(str, enum.Enum):
    normal = "normal"
    critical = "critical"


class MedicationStatus(str, enum.Enum):
    active = "active"
    archived = "archived"


class MedicationSource(str, enum.Enum):
    manual = "manual"
    scan = "scan"


class Medication(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "medications"

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_recipients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    strength: Mapped[str] = mapped_column(String(50), nullable=False)
    form: Mapped[str] = mapped_column(String(50), default="tablet", nullable=False)
    instructions: Mapped[str] = mapped_column(Text, default="", nullable=False)
    purpose_card: Mapped[dict] = mapped_column(
        JSONB,
        default=lambda: {
            "purpose": "",
            "instructions": "",
            "food_warning": "",
            "cautions": "",
            "disclaimer": "Advisory information only. Follow your prescribing doctor's exact instructions.",
        },
        nullable=False,
    )
    criticality: Mapped[MedicationCriticality] = mapped_column(
        Enum(MedicationCriticality, name="medication_criticality_enum", values_callable=lambda x: [e.value for e in x]),
        default=MedicationCriticality.normal,
        nullable=False,
    )
    dose_quantity: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("1.0"), nullable=False)
    stock_count: Mapped[Decimal] = mapped_column(Numeric(7, 2), default=Decimal("0.0"), nullable=False)
    refill_threshold_days: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    status: Mapped[MedicationStatus] = mapped_column(
        Enum(MedicationStatus, name="medication_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=MedicationStatus.active,
        nullable=False,
        index=True,
    )
    source: Mapped[MedicationSource] = mapped_column(
        Enum(MedicationSource, name="medication_source_enum", values_callable=lambda x: [e.value for e in x]),
        default=MedicationSource.manual,
        nullable=False,
    )
    confirmed_with_doctor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    recipient: Mapped[CareRecipient] = relationship("CareRecipient", back_populates="medications")
    schedules: Mapped[list[MedicationSchedule]] = relationship("MedicationSchedule", back_populates="medication")
    dose_events: Mapped[list[DoseEvent]] = relationship("DoseEvent", back_populates="medication")
    proposals: Mapped[list[ScheduleProposal]] = relationship("ScheduleProposal", back_populates="medication")
