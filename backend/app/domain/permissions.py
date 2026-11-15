"""permissions.py — Pure authorization logic and capability matrix.

Principles:
- Elder holds final say over care decisions and data sharing permissions.
- Roles define default capabilities; per-member permissions refine family/caretaker access.
- Doctor access is read-only and roadmap-ready; doctors cannot alter schedules directly.
"""

from __future__ import annotations

from typing import Any

from app.domain.types import Role

# Baseline capabilities by role
ROLE_DEFAULT_PERMISSIONS: dict[Role, dict[str, bool]] = {
    Role.elder: {
        "can_view_meds": True,
        "can_edit_meds": True,
        "can_mark_doses": True,
        "can_view_appointments": True,
        "can_edit_appointments": True,
        "can_view_health": True,
        "can_view_audit": True,
        "can_manage_members": True,
    },
    Role.caretaker: {
        "can_view_meds": True,
        "can_edit_meds": True,
        "can_mark_doses": True,
        "can_view_appointments": True,
        "can_edit_appointments": True,
        "can_view_health": True,
        "can_view_audit": True,
        "can_manage_members": False,
    },
    Role.family: {
        "can_view_meds": False,
        "can_edit_meds": False,
        "can_mark_doses": False,
        "can_view_appointments": False,
        "can_edit_appointments": False,
        "can_view_health": False,
        "can_view_audit": False,
        "can_manage_members": False,
    },
    Role.doctor: {
        "can_view_meds": True,
        "can_edit_meds": False,  # Doctors propose, but do not directly mutate active schedule
        "can_mark_doses": False,
        "can_view_appointments": True,
        "can_edit_appointments": False,
        "can_view_health": True,
        "can_view_audit": False,
        "can_manage_members": False,
    },
}


def has_permission(
    role: Role,
    action: str,
    member_permissions: dict[str, Any] | None = None,
) -> bool:
    """Evaluate whether a role and its custom permissions allow an action."""
    # Elder always has full permission
    if role == Role.elder:
        return True

    # Check custom elder-granted permissions first (if provided)
    if member_permissions and action in member_permissions:
        val = member_permissions[action]
        if isinstance(val, bool):
            # Doctor cannot edit meds or mark doses even if accidentally toggled
            if role == Role.doctor and action in ("can_edit_meds", "can_mark_doses", "can_manage_members"):
                return False
            return val

    # Fall back to role defaults
    defaults = ROLE_DEFAULT_PERMISSIONS.get(role, {})
    return defaults.get(action, False)


def can_approve_proposal(role: Role) -> bool:
    """The elder has the final say on schedule proposals."""
    return role == Role.elder


def can_manage_member(actor_role: Role, target_role: Role) -> bool:
    """Check if an actor can deactivate or update permissions for a target member."""
    if actor_role == Role.elder:
        # Elder can manage anyone except they cannot deactivate their own primary access
        return True
    return False
