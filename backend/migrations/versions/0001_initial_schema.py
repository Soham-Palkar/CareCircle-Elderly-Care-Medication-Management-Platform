"""Initial schema migration for CareCircle platform.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-15 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Dialect-adaptive types
JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
UUID_TYPE = sa.UUID(as_uuid=True)


def upgrade() -> None:
    # 1. care_circles
    op.create_table(
        "care_circles",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("circle_code", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_care_circles_circle_code", "care_circles", ["circle_code"], unique=True)

    # 2. care_recipients
    op.create_table(
        "care_recipients",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("circle_id", UUID_TYPE, sa.ForeignKey("care_circles.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("wake_time", sa.Time(), nullable=True),
        sa.Column("sleep_time", sa.Time(), nullable=True),
        sa.Column("routine_times", JSON_TYPE, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 3. members
    op.create_table(
        "members",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("circle_id", UUID_TYPE, sa.ForeignKey("care_circles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("passcode_hash", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("telegram_chat_id", sa.BigInteger(), nullable=True),
        sa.Column("notify_prefs", JSON_TYPE, nullable=False),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_members_circle_id", "members", ["circle_id"])
    op.create_index("ix_members_telegram_chat_id", "members", ["telegram_chat_id"])

    # 4. member_permissions
    op.create_table(
        "member_permissions",
        sa.Column("member_id", UUID_TYPE, sa.ForeignKey("members.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("can_view_meds", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("can_edit_meds", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("can_mark_doses", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("can_view_appointments", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("can_edit_appointments", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("can_view_health", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("receives_alerts", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("alert_level_min", sa.Integer(), nullable=False, server_default="1"),
    )

    # 5. invites
    op.create_table(
        "invites",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("circle_id", UUID_TYPE, sa.ForeignKey("care_circles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("code_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", UUID_TYPE, sa.ForeignKey("members.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_invites_circle_id", "invites", ["circle_id"])
    op.create_index("ix_invites_code_hash", "invites", ["code_hash"])

    # 6. medications
    op.create_table(
        "medications",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("recipient_id", UUID_TYPE, sa.ForeignKey("care_recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("strength", sa.String(50), nullable=False),
        sa.Column("form", sa.String(50), nullable=False, server_default="tablet"),
        sa.Column("instructions", sa.Text(), nullable=False, server_default=""),
        sa.Column("purpose_card", JSON_TYPE, nullable=False),
        sa.Column("criticality", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("dose_quantity", sa.Numeric(5, 2), nullable=False, server_default="1.0"),
        sa.Column("stock_count", sa.Numeric(7, 2), nullable=False, server_default="0.0"),
        sa.Column("refill_threshold_days", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("source", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("confirmed_with_doctor", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_by", UUID_TYPE, sa.ForeignKey("members.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_medications_recipient_id", "medications", ["recipient_id"])
    op.create_index("ix_medications_status", "medications", ["status"])

    # 7. medication_schedules
    op.create_table(
        "medication_schedules",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("medication_id", UUID_TYPE, sa.ForeignKey("medications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False, server_default="fixed_time"),
        sa.Column("time_of_day", sa.Time(), nullable=True),
        sa.Column("anchor", sa.String(50), nullable=True),
        sa.Column("anchor_offset_min", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("days_of_week", sa.SmallInteger(), nullable=False, server_default="127"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("grace_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("supersedes_id", UUID_TYPE, sa.ForeignKey("medication_schedules.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_medication_schedules_medication_id", "medication_schedules", ["medication_id"])
    op.create_index("ix_medication_schedules_is_active", "medication_schedules", ["is_active"])

    # 8. dose_events
    op.create_table(
        "dose_events",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("schedule_id", UUID_TYPE, sa.ForeignKey("medication_schedules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("medication_id", UUID_TYPE, sa.ForeignKey("medications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_id", UUID_TYPE, sa.ForeignKey("care_recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(20), nullable=False, server_default="scheduled"),
        sa.Column("escalation_level", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("snooze_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recorded_by", UUID_TYPE, sa.ForeignKey("members.id", ondelete="SET NULL"), nullable=True),
        sa.Column("recorded_via", sa.String(20), nullable=False, server_default="app"),
        sa.Column("skip_reason", sa.String(255), nullable=True),
        sa.Column("idempotency_key", sa.String(100), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("schedule_id", "scheduled_at", name="uq_dose_schedule_time"),
    )
    op.create_index("ix_dose_events_state_scheduled_at", "dose_events", ["state", "scheduled_at"])
    op.create_index("ix_dose_events_recipient_scheduled", "dose_events", ["recipient_id", "scheduled_at"])
    op.create_index("ix_dose_events_idempotency_key", "dose_events", ["idempotency_key"])

    # 9. appointments
    op.create_table(
        "appointments",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("circle_id", UUID_TYPE, sa.ForeignKey("care_circles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_id", UUID_TYPE, sa.ForeignKey("care_recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doctor_name", sa.String(100), nullable=False),
        sa.Column("specialty", sa.String(100), nullable=False, server_default=""),
        sa.Column("location", sa.String(255), nullable=False, server_default=""),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="upcoming"),
        sa.Column("reminder_offsets_min", JSON_TYPE, nullable=False),
        sa.Column("created_by", UUID_TYPE, sa.ForeignKey("members.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_appointments_circle_id", "appointments", ["circle_id"])
    op.create_index("ix_appointments_recipient_id", "appointments", ["recipient_id"])
    op.create_index("ix_appointments_status", "appointments", ["status"])
    op.create_index("ix_appointments_recipient_scheduled", "appointments", ["recipient_id", "scheduled_at"])

    # 10. notifications (reliable outbox)
    op.create_table(
        "notifications",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("member_id", UUID_TYPE, sa.ForeignKey("members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("circle_id", UUID_TYPE, sa.ForeignKey("care_circles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("payload", JSON_TYPE, nullable=False),
        sa.Column("dedupe_key", sa.String(255), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("related_event_id", UUID_TYPE, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notifications_member_id", "notifications", ["member_id"])
    op.create_index("ix_notifications_circle_id", "notifications", ["circle_id"])
    op.create_index("ix_notifications_status", "notifications", ["status"])
    op.create_index("ix_notifications_dedupe_key", "notifications", ["dedupe_key"])
    op.create_index("ix_notifications_pending", "notifications", ["status", "next_attempt_at"])

    # 11. escalation_policies
    op.create_table(
        "escalation_policies",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("recipient_id", UUID_TYPE, sa.ForeignKey("care_recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("criticality", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("level", sa.SmallInteger(), nullable=False),
        sa.Column("delay_minutes", sa.Integer(), nullable=False),
        sa.Column("target_role", sa.String(20), nullable=False),
    )
    op.create_index("ix_escalation_policies_recipient_id", "escalation_policies", ["recipient_id"])

    # 12. health_readings
    op.create_table(
        "health_readings",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("recipient_id", UUID_TYPE, sa.ForeignKey("care_recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("value", sa.Numeric(8, 2), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(20), nullable=False, server_default="manual"),
    )
    op.create_index("ix_health_readings_recipient_id", "health_readings", ["recipient_id"])
    op.create_index("ix_health_readings_recipient_kind", "health_readings", ["recipient_id", "kind", "recorded_at"])

    # 13. risk_flags
    op.create_table(
        "risk_flags",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("recipient_id", UUID_TYPE, sa.ForeignKey("care_recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rule_code", sa.String(20), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("evidence", JSON_TYPE, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_risk_flags_recipient_id", "risk_flags", ["recipient_id"])
    op.create_index("ix_risk_flags_status", "risk_flags", ["status"])

    # 14. schedule_proposals
    op.create_table(
        "schedule_proposals",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("medication_id", UUID_TYPE, sa.ForeignKey("medications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("proposed_by", UUID_TYPE, sa.ForeignKey("members.id", ondelete="SET NULL"), nullable=True),
        sa.Column("change", JSON_TYPE, nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("decided_by", UUID_TYPE, sa.ForeignKey("members.id", ondelete="SET NULL"), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_schedule_proposals_medication_id", "schedule_proposals", ["medication_id"])
    op.create_index("ix_schedule_proposals_status", "schedule_proposals", ["status"])

    # 15. scan_drafts
    op.create_table(
        "scan_drafts",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("recipient_id", UUID_TYPE, sa.ForeignKey("care_recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by", UUID_TYPE, sa.ForeignKey("members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("extracted", JSON_TYPE, nullable=False),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=False, server_default="0.0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_scan_drafts_recipient_id", "scan_drafts", ["recipient_id"])
    op.create_index("ix_scan_drafts_status", "scan_drafts", ["status"])

    # 16. streaks
    op.create_table(
        "streaks",
        sa.Column("recipient_id", UUID_TYPE, sa.ForeignKey("care_recipients.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("best_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_date", sa.Date(), nullable=True),
    )

    # 17. rewards
    op.create_table(
        "rewards",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("recipient_id", UUID_TYPE, sa.ForeignKey("care_recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("threshold_days", sa.Integer(), nullable=False),
        sa.Column("reward_type", sa.String(20), nullable=False),
        sa.Column("reward_ref", sa.String(255), nullable=False, server_default=""),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_rewards_recipient_id", "rewards", ["recipient_id"])

    # 18. adherence_daily
    op.create_table(
        "adherence_daily",
        sa.Column("recipient_id", UUID_TYPE, sa.ForeignKey("care_recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("scheduled_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("taken_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("missed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("recipient_id", "date", name="pk_adherence_daily"),
    )

    # 19. interaction_rules
    op.create_table(
        "interaction_rules",
        sa.Column("id", UUID_TYPE, primary_key=True),
        sa.Column("drug_a", sa.String(100), nullable=False),
        sa.Column("drug_b", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="moderate"),
        sa.Column("note", sa.Text(), nullable=False),
    )
    op.create_index("ix_interaction_rules_drug_a", "interaction_rules", ["drug_a"])
    op.create_index("ix_interaction_rules_drug_b", "interaction_rules", ["drug_b"])

    # 20. audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("circle_id", UUID_TYPE, nullable=False),
        sa.Column("actor_member_id", UUID_TYPE, nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", UUID_TYPE, nullable=False),
        sa.Column("before", JSON_TYPE, nullable=True),
        sa.Column("after", JSON_TYPE, nullable=True),
        sa.Column("ip", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_log_circle_id", "audit_log", ["circle_id"])
    op.create_index("ix_audit_log_circle_created", "audit_log", ["circle_id", "created_at"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("interaction_rules")
    op.drop_table("adherence_daily")
    op.drop_table("rewards")
    op.drop_table("streaks")
    op.drop_table("scan_drafts")
    op.drop_table("schedule_proposals")
    op.drop_table("risk_flags")
    op.drop_table("health_readings")
    op.drop_table("escalation_policies")
    op.drop_table("notifications")
    op.drop_table("appointments")
    op.drop_table("dose_events")
    op.drop_table("medication_schedules")
    op.drop_table("medications")
    op.drop_table("invites")
    op.drop_table("member_permissions")
    op.drop_table("members")
    op.drop_table("care_recipients")
    op.drop_table("care_circles")
