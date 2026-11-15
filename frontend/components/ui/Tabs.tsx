'use client';

import React from 'react';
import { cn } from '@/lib/utils';

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

export interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
}

export function Tabs({ tabs, activeTab, onChange, className }: TabsProps) {
  return (
    <div
      role="tablist"
      className={cn(
        'flex items-center gap-2 p-1.5 bg-[#F2EDE6] rounded-2xl overflow-x-auto scrollbar-none',
        className,
      )}
    >
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(tab.id)}
            className={cn(
              'flex items-center gap-2 px-5 py-2.5 rounded-xl text-base font-semibold transition-all whitespace-nowrap',
              'focus:outline-none focus:ring-2 focus:ring-[#C97B4B]',
              isActive
                ? 'bg-white text-[#2D2318] shadow-sm'
                : 'text-[#5C4A38] hover:text-[#2D2318] hover:bg-white/50',
            )}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
}

