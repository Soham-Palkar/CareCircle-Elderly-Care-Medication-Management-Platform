'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Heart, Pill, Calendar, Bell } from 'lucide-react';
import { cn } from '@/lib/utils';

const FAMILY_NAV_ITEMS = [
  { href: '/family', icon: Heart, label: 'Today’s Status' },
  { href: '/family/medications', icon: Pill, label: 'Medications' },
  { href: '/family/appointments', icon: Calendar, label: 'Appointments' },
  { href: '/family/alerts', icon: Bell, label: 'Alerts & History' },
];

export function FamilyNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Family navigation"
      className="bg-white border-b border-[#EBE4DB] px-4 py-2 shadow-2xs"
    >
      <div className="max-w-4xl mx-auto flex items-center justify-around sm:justify-start gap-2 overflow-x-auto">
        {FAMILY_NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition-colors whitespace-nowrap',
                'focus:outline-none focus:ring-2 focus:ring-[#C97B4B]',
                isActive
                  ? 'bg-[#FFF3E0] text-[#8C4E00] border border-[#FFD59E] font-bold'
                  : 'text-[#5C4A38] hover:bg-[#FAF8F5] hover:text-[#2D2318]',
              )}
            >
              <Icon className="w-4 h-4 shrink-0" aria-hidden />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
