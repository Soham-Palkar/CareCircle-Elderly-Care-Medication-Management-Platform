import React from 'react';
import { FamilyNav } from '@/components/family/FamilyNav';
import { RoleGuard } from '@/components/common/RoleGuard';

export default function FamilyLayout({ children }: { children: React.ReactNode }) {
  return (
    <RoleGuard allowedRoles={['family']}>
      <div className="min-h-screen bg-[#FAF8F5]">
        <FamilyNav />
        <main className="max-w-4xl mx-auto p-4 sm:p-8">{children}</main>
      </div>
    </RoleGuard>
  );
}

