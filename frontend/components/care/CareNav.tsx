'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Pill,
  Camera,
  Calendar,
  BarChart3,
  Cpu,
  Sparkles,
  Users,
  ShieldAlert,
  Settings,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const CARE_NAV_ITEMS = [
  { href: '/care', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/care/medications', icon: Pill, label: 'Medications' },
  { href: '/care/scan', icon: Camera, label: 'Scan Rx / Box' },
  { href: '/care/appointments', icon: Calendar, label: 'Appointments' },
  { href: '/care/adherence', icon: BarChart3, label: 'Adherence' },
  { href: '/care/twin', icon: Cpu, label: 'Digital Twin' },
  { href: '/care/proposals', icon: Sparkles, label: 'Proposals' },
  { href: '/care/members', icon: Users, label: 'Members' },
  { href: '/care/audit', icon: ShieldAlert, label: 'Audit Log' },
  { href: '/care/settings', icon: Settings, label: 'Settings' },
];

export function CareNav() {
  const pathname = usePathname();

  return (
    <aside
      aria-label="Caretaker tools navigation"
      className="w-full lg:w-56 bg-white border-b lg:border-b-0 lg:border-r border-[#EBE4DB] shrink-0 p-3"
    >
      <div className="flex lg:flex-col gap-1 overflow-x-auto lg:overflow-visible pb-1 lg:pb-0 scrollbar-none">
        {CARE_NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-colors whitespace-nowrap',
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
    </aside>
  );
}
