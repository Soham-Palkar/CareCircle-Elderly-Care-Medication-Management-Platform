import React from 'react';
import { CareNav } from '@/components/care/CareNav';
import { RoleGuard } from '@/components/common/RoleGuard';

export default function CareLayout({ children }: { children: React.ReactNode }) {
  return (
    <RoleGuard allowedRoles={['caretaker']}>
      <div className="min-h-screen bg-[#FAF8F5] flex flex-col lg:flex-row">
        <CareNav />
        <main className="flex-1 max-w-6xl p-4 sm:p-6 lg:p-8 overflow-y-auto min-w-0">
          {children}
        </main>
      </div>
    </RoleGuard>
  );
}
