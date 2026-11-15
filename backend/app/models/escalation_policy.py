"""EscalationPolicy entity."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin
from app.models.medication import MedicationCriticality
from app.models.member import Role


class EscalationPolicy(UUIDMixin, Base):
    __tablename__ = "escalation_policies"

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_recipients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criticality: Mapped[MedicationCriticality] = mapped_column(
        Enum(MedicationCriticality, name="escalation_criticality_enum", values_callable=lambda x: [e.value for e in x]),
        default=MedicationCriticality.normal,
        nullable=False,
    )
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    delay_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    target_role: Mapped[Role] = mapped_column(
        Enum(Role, name="escalation_target_role_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
