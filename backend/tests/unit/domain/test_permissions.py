"""Unit tests for role authorization and permission evaluation."""

import pytest
from app.domain.types import Role
from app.domain.permissions import (
    can_approve_proposal,
    can_manage_member,
    has_permission,
    ROLE_DEFAULT_PERMISSIONS,
)


def test_elder_has_all_permissions():
    actions = [
        "can_view_meds",
        "can_edit_meds",
        "can_mark_doses",
        "can_view_appointments",
        "can_edit_appointments",
        "can_view_health",
        "can_view_audit",
        "can_manage_members",
        "arbitrary_future_action",
    ]
    for action in actions:
        assert has_permission(Role.elder, action) is True


def test_caretaker_default_permissions():
    assert has_permission(Role.caretaker, "can_view_meds") is True
    assert has_permission(Role.caretaker, "can_edit_meds") is True
    assert has_permission(Role.caretaker, "can_mark_doses") is True
    assert has_permission(Role.caretaker, "can_manage_members") is False


def test_family_default_permissions_are_restrictive():
    # Family starts with no med/appointment editing or health viewing
    assert has_permission(Role.family, "can_view_meds") is False
    assert has_permission(Role.family, "can_edit_meds") is False
    assert has_permission(Role.family, "can_mark_doses") is False
    assert has_permission(Role.family, "can_view_health") is False


def test_elder_granted_permissions_for_family():
    # When elder grants view permissions to family member
    custom_perms = {
        "can_view_meds": True,
        "can_view_appointments": True,
        "can_edit_meds": False,
    }
    assert has_permission(Role.family, "can_view_meds", member_permissions=custom_perms) is True
    assert has_permission(Role.family, "can_view_appointments", member_permissions=custom_perms) is True
    assert has_permission(Role.family, "can_edit_meds", member_permissions=custom_perms) is False


def test_doctor_safety_guards():
    # Doctors can view meds and health
    assert has_permission(Role.doctor, "can_view_meds") is True
    assert has_permission(Role.doctor, "can_view_health") is True

    # Doctors CANNOT edit meds, mark doses, or manage members, even if accidentally toggled in custom perms
    accidental_perms = {
        "can_edit_meds": True,
        "can_mark_doses": True,
        "can_manage_members": True,
    }
    assert has_permission(Role.doctor, "can_edit_meds", member_permissions=accidental_perms) is False
    assert has_permission(Role.doctor, "can_mark_doses", member_permissions=accidental_perms) is False
    assert has_permission(Role.doctor, "can_manage_members", member_permissions=accidental_perms) is False


def test_elder_final_say_on_proposals():
    # Only elder can approve proposals
    assert can_approve_proposal(Role.elder) is True
    assert can_approve_proposal(Role.caretaker) is False
    assert can_approve_proposal(Role.family) is False
    assert can_approve_proposal(Role.doctor) is False


def test_can_manage_member():
    assert can_manage_member(Role.elder, Role.caretaker) is True
    assert can_manage_member(Role.elder, Role.family) is True
    assert can_manage_member(Role.caretaker, Role.family) is False
    assert can_manage_member(Role.family, Role.doctor) is False
