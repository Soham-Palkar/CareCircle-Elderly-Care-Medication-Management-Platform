'use client';

import {
  CheckCircle2,
  Clock,
  BellRing,
  AlarmClock,
  SkipForward,
  XCircle,
  RefreshCw,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export type DoseState =
  | 'scheduled'
  | 'reminded'
  | 'snoozed'
  | 'taken'
  | 'taken_late'
  | 'skipped'
  | 'missed';

export interface DoseStateLabelProps {
  state: DoseState;
  /** Additional detail — e.g. the time taken, snooze time, or skip reason */
  detail?: string;
  className?: string;
}

const STATE_CONFIG: Record<
  DoseState,
  {
    label: string;
    Icon: React.ComponentType<any>;
    colorClass: string;
    bgClass: string;
  }
> = {
  scheduled: {
    label: 'Coming up soon',
    Icon: Clock,
    colorClass: 'text-[#5C4A3A]',
    bgClass: 'bg-[#FDF3E7]',
  },
  reminded: {
    label: 'Time to take this',
    Icon: BellRing,
    colorClass: 'text-[#8B4513]',
    bgClass: 'bg-[#FFF3CD]',
  },
  snoozed: {
    label: 'Remind me again at',
    Icon: AlarmClock,
    colorClass: 'text-[#5C4A3A]',
    bgClass: 'bg-[#F5EDE0]',
  },
  taken: {
    label: 'Done! Taken at',
    Icon: CheckCircle2,
    colorClass: 'text-[#2D6A4F]',
    bgClass: 'bg-[#D8F3DC]',
  },
  taken_late: {
    label: 'Taken (a bit late)',
    Icon: CheckCircle2,
    colorClass: 'text-[#5A7A5A]',
    bgClass: 'bg-[#E8F5E9]',
  },
  skipped: {
    label: 'Skipped',
    Icon: SkipForward,
    colorClass: 'text-[#7A5A3A]',
    bgClass: 'bg-[#FFF8E7]',
  },
  missed: {
    label: 'Missed — your caretaker has been notified',
    Icon: XCircle,
    colorClass: 'text-[#8B2500]',
    bgClass: 'bg-[#FFE8E0]',
  },
};

/** Displays dose state using text + icon (never color alone) — WCAG requirement */
export function DoseStateLabel({ state, detail, className }: DoseStateLabelProps) {
  const config = STATE_CONFIG[state] || STATE_CONFIG.scheduled;
  const { label, Icon, colorClass, bgClass } = config;

  const displayLabel =
    state === 'snoozed' && detail
      ? `Remind me again at ${detail}`
      : state === 'taken' && detail
        ? `Done! Taken at ${detail}`
        : state === 'skipped' && detail
          ? `Skipped — ${detail}`
          : label;

  return (
    <span
      role="status"
      aria-label={`Dose status: ${displayLabel}`}
      className={cn(
        'inline-flex items-center gap-2 px-4 py-2 rounded-xl font-semibold text-[20px]',
        bgClass,
        colorClass,
        className,
      )}
    >
      <Icon aria-hidden size={24} />
      <span>{displayLabel}</span>
    </span>
  );
}
