"""MemberPermission entity managed by the elder."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MemberPermission(Base):
    __tablename__ = "member_permissions"

    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        primary_key=True,
    )
    can_view_meds: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_edit_meds: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_mark_doses: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_view_appointments: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_edit_appointments: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_view_health: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    receives_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    alert_level_min: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    member: Mapped[Member] = relationship("Member", back_populates="permissions")
