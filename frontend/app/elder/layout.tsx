import React from 'react';
import { ElderNav } from '@/components/elder/ElderNav';
import { RoleGuard } from '@/components/common/RoleGuard';

export default function ElderLayout({ children }: { children: React.ReactNode }) {
  return (
    <RoleGuard allowedRoles={['elder']}>
      <div className="min-h-screen bg-[#FAF8F5] pb-32">
        <a
          href="#main-elder-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 bg-[#C97B4B] text-white px-6 py-3 rounded-xl font-bold text-xl"
        >
          Skip to main content
        </a>
        <main id="main-elder-content" className="max-w-3xl mx-auto px-4 sm:px-6 pt-6">
          {children}
        </main>
        <ElderNav />
      </div>
    </RoleGuard>
  );
}

