'use client';

import React, { useEffect, useState } from 'react';
import { getActiveRole, setActiveRole } from '@/lib/auth/session';
import { Role } from '@/lib/api/types';
import { ShieldAlert } from 'lucide-react';
import { Button } from '../ui/Button';

export function RoleGuard({
  allowedRoles,
  children,
}: {
  allowedRoles: Role[];
  children: React.ReactNode;
}) {
  const [currentRole, setCurrentRole] = useState<Role | null>(null);

  useEffect(() => {
    setCurrentRole(getActiveRole());

    const handleAuthChange = () => {
      setCurrentRole(getActiveRole());
    };
    window.addEventListener('carecircle_auth_change', handleAuthChange);
    return () => window.removeEventListener('carecircle_auth_change', handleAuthChange);
  }, []);

  if (!currentRole) return null;

  if (!allowedRoles.includes(currentRole)) {
    return (
      <div className="max-w-md mx-auto my-12 p-6 bg-white border border-[#EBE4DB] rounded-xl text-center shadow-2xs">
        <div className="p-3 bg-[#FFF3E0] rounded-lg w-12 h-12 mx-auto flex items-center justify-center text-[#8C4E00] mb-3">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-[#2D2318] mb-1.5">Role Access Scope</h2>
        <p className="text-xs sm:text-sm text-[#5C4A38] mb-5">
          This area is designated for the <strong>{allowedRoles.join(' or ')}</strong> role. You are currently viewing as{' '}
          <strong>{currentRole}</strong>.
        </p>
        <Button
          variant="primary"
          size="md"
          onClick={() => {
            setActiveRole(allowedRoles[0]);
            window.location.reload();
          }}
          className="w-full font-bold"
        >
          Switch to {allowedRoles[0]} View
        </Button>
      </div>
    );
  }

  return <>{children}</>;
}

