/**
 * CareCircle Session & Role Management
 */

import { Role, Member } from '../api/types';
import { mockMembers } from '../api/mockData';

const ROLE_STORAGE_KEY = 'carecircle_active_role';
const MEMBER_STORAGE_KEY = 'carecircle_active_member';

export function getActiveRole(): Role {
  if (typeof window === 'undefined') return 'elder';
  const stored = localStorage.getItem(ROLE_STORAGE_KEY) as Role;
  if (stored && ['elder', 'caretaker', 'family', 'doctor'].includes(stored)) {
    return stored;
  }
  return 'elder';
}

export function setActiveRole(role: Role): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(ROLE_STORAGE_KEY, role);
  // Match corresponding mock member
  const member = mockMembers.find((m) => m.role === role) || mockMembers[0];
  localStorage.setItem(MEMBER_STORAGE_KEY, JSON.stringify(member));
  // Dispatch custom event for UI updates
  window.dispatchEvent(new Event('carecircle_auth_change'));
}

export function getCurrentMember(): Member {
  if (typeof window === 'undefined') return mockMembers[0];
  const stored = localStorage.getItem(MEMBER_STORAGE_KEY);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      // Fallback
    }
  }
  const role = getActiveRole();
  return mockMembers.find((m) => m.role === role) || mockMembers[0];
}

export function isAuthorizedForRole(requiredRole: Role, userRole: Role): boolean {
  if (userRole === requiredRole) return true;
  // Caretaker can see caretaker routes; elder can see elder routes; family can see family routes
  return false;
}

export function logout(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(ROLE_STORAGE_KEY);
  localStorage.removeItem(MEMBER_STORAGE_KEY);
  window.location.href = '/login';
}

