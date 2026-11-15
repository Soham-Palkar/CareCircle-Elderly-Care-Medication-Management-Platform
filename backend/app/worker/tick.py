"""Worker tick job: Due-soon alerts, grace periods, and escalation progression."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.domain.escalation import get_next_escalation, should_mark_missed
from app.domain.types import DoseState, MedCriticality, Role
from app.models.dose_event import DoseEvent
from app.models.medication import Medication
from app.models.member import Member
from app.models.notification import NotificationChannel, NotificationType
from app.models.recipient import CareRecipient
from app.services.notification_service import NotificationService
from app.services.realtime import realtime_broker

settings = get_settings()


async def process_scheduler_tick(db: AsyncSession) -> dict[str, int]:
    """Execute one 30-second tick across all circles:
    1. Due-soon: scheduled events within lead_time move to reminded and notify elder.
    2. Overdue: unresolved events exceeding grace period move to missed.
    3. Escalation: evaluate escalation policy levels for unresolved events.
    """
    now = datetime.now(timezone.utc)
    lead_time = timedelta(minutes=settings.reminder_lead_minutes)

    stats = {
        "reminded": 0,
        "missed": 0,
        "escalations": 0,
    }

    # ── 1. Due soon ──────────────────────────────────────────────────────────
    stmt = (
        select(DoseEvent)
        .where(
            DoseEvent.state == DoseState.scheduled,
            DoseEvent.scheduled_at <= now + lead_time,
        )
        .options(selectinload(DoseEvent.medication), selectinload(DoseEvent.schedule))
    )
    res = await db.execute(stmt)
    due_events = list(res.scalars().all())

    for ev in due_events:
        ev.state = DoseState.reminded
        stats["reminded"] += 1

        # Enqueue initial reminder for the elder
        r_stmt = select(CareRecipient).where(CareRecipient.id == ev.recipient_id)
        recipient = (await db.execute(r_stmt)).scalar_one_or_none()
        if recipient:
            m_stmt = select(Member).where(
                Member.circle_id == recipient.circle_id,
                Member.role == Role.elder,
                Member.is_active.is_(True),
            )
            elder = (await db.execute(m_stmt)).scalar_one_or_none()
            if elder:
                notif_svc = NotificationService(db, recipient.circle_id)
                med_name = ev.medication.name if ev.medication else "Medication"
                time_str = ev.scheduled_at.strftime("%I:%M %p")
                await notif_svc.enqueue(
                    member_id=elder.id,
                    channel=NotificationChannel.email,
                    notif_type=NotificationType.dose_due,
                    payload={
                        "subject": f"Reminder: Time for {med_name} ({time_str})",
                        "medication_name": med_name,
                        "scheduled_time": time_str,
                        "dose_event_id": str(ev.id),
                    },
                    dedupe_key=f"{ev.id}:dose_due:0",
                    related_event_id=ev.id,
                )
                await realtime_broker.publish(
                    recipient.circle_id,
                    {"type": "dose_reminded", "dose_id": str(ev.id)},
                )

    # ── 2. Grace period / Overdue -> Missed ──────────────────────────────────
    unresolved_stmt = (
        select(DoseEvent)
        .where(DoseEvent.state.in_([DoseState.reminded, DoseState.snoozed]))
        .options(selectinload(DoseEvent.medication), selectinload(DoseEvent.schedule))
    )
    unresolved = list((await db.execute(unresolved_stmt)).scalars().all())

    for ev in unresolved:
        grace = ev.schedule.grace_minutes if ev.schedule else settings.default_grace_minutes
        if should_mark_missed(DoseState(ev.state.value), ev.scheduled_at, now, grace):
            ev.state = DoseState.missed
            stats["missed"] += 1

            r_stmt = select(CareRecipient).where(CareRecipient.id == ev.recipient_id)
            recipient = (await db.execute(r_stmt)).scalar_one_or_none()
            if recipient:
                await realtime_broker.publish(
                    recipient.circle_id,
                    {"type": "dose_missed", "dose_id": str(ev.id)},
                )

        # ── 3. Escalation check ──────────────────────────────────────────────
        crit = MedCriticality.critical if ev.medication and ev.medication.criticality.value == "critical" else MedCriticality.normal
        action = get_next_escalation(
            current_level=ev.escalation_level,
            due_time=ev.scheduled_at,
            now=now,
            criticality=crit,
        )
        if action:
            ev.escalation_level = action.level
            stats["escalations"] += 1

            r_stmt = select(CareRecipient).where(CareRecipient.id == ev.recipient_id)
            recipient = (await db.execute(r_stmt)).scalar_one_or_none()
            if recipient:
                # Find members matching target_role
                m_stmt = select(Member).where(
                    Member.circle_id == recipient.circle_id,
                    Member.role == Role(action.target_role.value),
                    Member.is_active.is_(True),
                )
                target_members = list((await db.execute(m_stmt)).scalars().all())
                notif_svc = NotificationService(db, recipient.circle_id)
                med_name = ev.medication.name if ev.medication else "Medication"

                for tm in target_members:
                    await notif_svc.enqueue(
                        member_id=tm.id,
                        channel=NotificationChannel.email,
                        notif_type=NotificationType(action.notify_type),
                        payload={
                            "subject": f"CareCircle Alert: {med_name} missed ({action.description})",
                            "medication_name": med_name,
                            "level": action.level,
                            "dose_event_id": str(ev.id),
                        },
                        dedupe_key=f"{ev.id}:{action.notify_type}:{action.level}:{tm.id}",
                        related_event_id=ev.id,
                    )

    await db.commit()
    return stats
