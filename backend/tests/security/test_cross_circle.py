"""Security tests for tenant isolation, RBAC boundaries, and token replay prevention."""

import uuid
import pytest
from app.core.security import create_access_token, create_action_token, verify_action_token
from app.domain.permissions import can_approve_proposal, has_permission
from app.domain.types import Role


def test_cross_circle_isolation_in_token_claims():
    circle_a = uuid.uuid4()
    circle_b = uuid.uuid4()
    member_a = uuid.uuid4()

    token_a = create_access_token(member_id=member_a, circle_id=circle_a, role="elder")
    from app.core.security import decode_token
    payload = decode_token(token_a)

    # Session strictly bounds the user to circle_a
    assert payload["circle_id"] == str(circle_a)
    assert payload["circle_id"] != str(circle_b)


def test_doctor_cannot_directly_modify_active_schedules():
    # Clinical safety rule: Doctors must never alter medication schedules directly.
    # Proposals only; elder holds final approval.
    assert has_permission(Role.doctor, "can_edit_meds") is False
    assert has_permission(Role.doctor, "can_mark_doses") is False
    assert can_approve_proposal(Role.doctor) is False


def test_action_token_replay_attack_prevention():
    event_id = uuid.uuid4()
    member_id = uuid.uuid4()

    # Create signed single-use action link token
    token = create_action_token(dose_event_id=event_id, action="taken", member_id=member_id)

    # First consumption succeeds
    payload = verify_action_token(token)
    assert payload["action"] == "taken"

    # Second consumption MUST raise UnauthorizedError (prevent double-submit or replay)
    with pytest.raises(Exception, match="already been used"):
        verify_action_token(token)


def test_action_token_tampering_rejected():
    event_id = uuid.uuid4()
    member_id = uuid.uuid4()

    token = create_action_token(dose_event_id=event_id, action="taken", member_id=member_id)
    # Tamper with the encoded payload part
    parts = token.split(".")
    tampered_token = f"dGFtcGVyZWQ.{parts[1]}"

    with pytest.raises(Exception):
        verify_action_token(tampered_token)
