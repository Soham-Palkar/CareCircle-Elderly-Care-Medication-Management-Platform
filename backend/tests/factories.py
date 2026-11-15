"""Test data builders and factories for unit and integration testing."""

from datetime import date, datetime, time, timezone
from decimal import Decimal
import uuid

from app.core.security import hash_passcode
from app.models.circle import CareCircle
from app.models.recipient import CareRecipient
from app.models.member import Member, Role
from app.models.permission import MemberPermission
from app.models.medication import Medication, MedicationCriticality, MedicationStatus, MedicationSource
from app.models.schedule import MedicationSchedule, ScheduleKind
from app.models.dose_event import DoseEvent, DoseState, DoseRecordedVia


def make_circle(name: str = "Test Family", circle_code: str | None = None) -> CareCircle:
    code = circle_code or f"TEST-{uuid.uuid4().hex[:6].upper()}"
    return CareCircle(
        id=uuid.uuid4(),
        name=name,
        circle_code=code,
        created_at=datetime.now(timezone.utc),
    )


def make_recipient(circle_id: uuid.UUID, full_name: str = "Elder User") -> CareRecipient:
    return CareRecipient(
        id=uuid.uuid4(),
        circle_id=circle_id,
        full_name=full_name,
        date_of_birth=date(1950, 1, 1),
        timezone="Asia/Kolkata",
        language="en",
        wake_time=time(7, 0),
        sleep_time=time(22, 0),
        routine_times={
            "wake": "07:00",
            "breakfast": "08:30",
            "lunch": "13:30",
            "dinner": "20:30",
            "bedtime": "22:00",
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_member(
    circle_id: uuid.UUID,
    display_name: str = "Test Member",
    role: Role = Role.elder,
    passcode: str = "123456",
) -> Member:
    return Member(
        id=uuid.uuid4(),
        circle_id=circle_id,
        display_name=display_name,
        role=role,
        passcode_hash=hash_passcode(passcode),
        email=f"{display_name.lower().replace(' ', '.')}@example.com",
        notify_prefs={"email_enabled": True, "telegram_enabled": False},
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_medication(
    recipient_id: uuid.UUID,
    name: str = "Metformin",
    strength: str = "500mg",
    criticality: MedicationCriticality = MedicationCriticality.normal,
    stock_count: Decimal = Decimal("30.0"),
) -> Medication:
    return Medication(
        id=uuid.uuid4(),
        recipient_id=recipient_id,
        name=name,
        strength=strength,
        form="tablet",
        instructions="Take with meals",
        criticality=criticality,
        dose_quantity=Decimal("1.0"),
        stock_count=stock_count,
        refill_threshold_days=5,
        status=MedicationStatus.active,
        source=MedicationSource.manual,
        confirmed_with_doctor=True,
        purpose_card={
            "purpose": "Blood sugar regulation",
            "instructions": "Take with meal",
            "food_warning": "Take immediately after food",
            "cautions": "None",
            "disclaimer": "Advisory information only.",
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_dose_event(
    schedule_id: uuid.UUID,
    medication_id: uuid.UUID,
    recipient_id: uuid.UUID,
    scheduled_at: datetime,
    state: DoseState = DoseState.scheduled,
) -> DoseEvent:
    return DoseEvent(
        id=uuid.uuid4(),
        schedule_id=schedule_id,
        medication_id=medication_id,
        recipient_id=recipient_id,
        scheduled_at=scheduled_at,
        state=state,
        escalation_level=0,
        recorded_via=DoseRecordedVia.app,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
