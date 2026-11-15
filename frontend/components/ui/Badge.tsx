'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { CheckCircle2, Clock, AlertTriangle, AlertCircle, XCircle, Sparkles } from 'lucide-react';
import { DoseState } from '@/lib/api/types';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'taken' | 'due' | 'snoozed' | 'skipped' | 'missed' | 'warning' | 'info' | 'simulated';
  icon?: React.ReactNode;
}

export function Badge({ className, variant = 'info', icon, children, ...props }: BadgeProps) {
  const styles = {
    taken: 'bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784]',
    due: 'bg-[#FFF3E0] text-[#8C4E00] border border-[#FFB74D]',
    snoozed: 'bg-[#F2EDE6] text-[#5C4A38] border border-[#D6CCC0]',
    skipped: 'bg-[#F9ECEC] text-[#8C2D2D] border border-[#D6CCC0]',
    missed: 'bg-[#FAEAEA] text-[#B71C1C] border border-[#E57373]',
    warning: 'bg-[#FFF3E0] text-[#8C4E00] border border-[#FFB74D]',
    info: 'bg-[#F0F4F8] text-[#1E3A8A] border border-[#BFDBFE]',
    simulated: 'bg-[#FDF3EB] text-[#8C4E00] border border-dashed border-[#C97B4B]',
  };

  const defaultIcons = {
    taken: <CheckCircle2 className="w-3.5 h-3.5" aria-hidden />,
    due: <Clock className="w-3.5 h-3.5" aria-hidden />,
    snoozed: <Clock className="w-3.5 h-3.5" aria-hidden />,
    skipped: <XCircle className="w-3.5 h-3.5" aria-hidden />,
    missed: <AlertCircle className="w-3.5 h-3.5" aria-hidden />,
    warning: <AlertTriangle className="w-3.5 h-3.5" aria-hidden />,
    info: <Sparkles className="w-3.5 h-3.5" aria-hidden />,
    simulated: <Sparkles className="w-3.5 h-3.5" aria-hidden />,
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-xs font-semibold tracking-wide',
        styles[variant],
        className,
      )}
      {...props}
    >
      {icon || defaultIcons[variant]}
      <span>{children}</span>
    </span>
  );
}

export function DoseStateBadge({ state, className }: { state: DoseState; className?: string }) {
  const labels: Record<DoseState, { text: string; variant: BadgeProps['variant'] }> = {
    scheduled: { text: 'Scheduled', variant: 'info' },
    reminded: { text: 'Time to take', variant: 'due' },
    snoozed: { text: 'Snoozed', variant: 'snoozed' },
    taken: { text: 'Taken', variant: 'taken' },
    taken_late: { text: 'Taken (Late)', variant: 'taken' },
    skipped: { text: 'Skipped', variant: 'skipped' },
    missed: { text: 'Missed', variant: 'missed' },
  };

  const item = labels[state] || { text: state, variant: 'info' };

  return (
    <Badge variant={item.variant} className={className}>
      {item.text}
    </Badge>
  );
}
