"""Unit tests for security functions (Argon2id, JWT tokens, circle codes, HMAC tokens)."""

import uuid
import pytest
from app.core.security import (
    create_access_token,
    create_action_token,
    create_refresh_token,
    decode_token,
    hash_passcode,
    verify_action_token,
    verify_passcode,
)
from app.services.auth_service import _generate_circle_code, _generate_invite_code


def test_argon2id_hashing():
    passcode = "123456"
    h = hash_passcode(passcode)
    assert h != passcode
    assert h.startswith("$argon2id$")
    assert verify_passcode(passcode, h) is True
    assert verify_passcode("wrong654", h) is False


def test_circle_code_generation():
    code = _generate_circle_code()
    assert len(code) == 9  # 4 letters, hyphen, 4 digits (e.g. ABCD-1234)
    assert "-" in code
    letters, digits = code.split("-")
    assert letters.isalpha() and letters.isupper()
    assert digits.isdigit()


def test_invite_code_generation():
    invite = _generate_invite_code()
    assert len(invite) == 10
    assert invite.isalnum()


def test_jwt_access_and_refresh_tokens():
    cid = uuid.uuid4()
    mid = uuid.uuid4()
    token = create_access_token(member_id=mid, circle_id=cid, role="elder")
    payload = decode_token(token)
    assert payload is not None
    assert payload["circle_id"] == str(cid)
    assert payload["sub"] == str(mid)
    assert payload["role"] == "elder"
    assert payload["type"] == "access"

    refresh = create_refresh_token(member_id=mid)
    r_payload = decode_token(refresh)
    assert r_payload is not None
    assert r_payload["sub"] == str(mid)
    assert r_payload["type"] == "refresh"


def test_hmac_action_tokens():
    eid = uuid.uuid4()
    mid = uuid.uuid4()

    token = create_action_token(dose_event_id=eid, action="taken", member_id=mid)
    assert isinstance(token, str)

    # Valid verification
    payload = verify_action_token(token)
    assert payload is not None
    assert payload["dose_event_id"] == str(eid)
    assert payload["action"] == "taken"
    assert payload["member_id"] == str(mid)

    # Reusing the token fails (single use!)
    with pytest.raises(Exception, match="already been used"):
        verify_action_token(token)

    # Tampered token fails
    tampered = create_action_token(dose_event_id=eid, action="taken", member_id=mid)
    tampered_sig = tampered[:-4] + "abcd"
    with pytest.raises(Exception, match="signature invalid|malformed"):
        verify_action_token(tampered_sig)
