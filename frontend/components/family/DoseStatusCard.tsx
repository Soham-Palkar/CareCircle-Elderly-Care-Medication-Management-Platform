'use client';

import { cn } from '@/lib/utils';
import { CheckCircle2, Clock3, AlertCircle } from 'lucide-react';

export type DoseStatus = 'taken' | 'taken_late' | 'missed' | 'scheduled' | 'skipped';

export interface DoseStatusInfo {
  id: string;
  medicineName: string;
  scheduledTime: string; // display string e.g. "8:00 AM"
  status: DoseStatus;
}

interface DoseStatusCardProps {
  dose: DoseStatusInfo;
  className?: string;
}

const STATUS_CONFIG: Record<DoseStatus, { label: string; icon: React.ElementType; iconClass: string; cardClass: string }> = {
  taken: {
    label: 'Taken',
    icon: CheckCircle2,
    iconClass: 'text-[#2D6A4F]',
    cardClass: 'bg-[#F0F7F2] border-[#A8D5B5]',
  },
  taken_late: {
    label: 'Taken (late)',
    icon: CheckCircle2,
    iconClass: 'text-[#7A6A14]',
    cardClass: 'bg-[#FFFBEA] border-[#E4CA5A]',
  },
  missed: {
    label: 'Missed',
    icon: AlertCircle,
    iconClass: 'text-[#C0392B]',
    cardClass: 'bg-[#FFF0EE] border-[#E8A09A]',
  },
  scheduled: {
    label: 'Upcoming',
    icon: Clock3,
    iconClass: 'text-[#5C4A3A]',
    cardClass: 'bg-[#FAF8F5] border-[#E8D5B7]',
  },
  skipped: {
    label: 'Skipped',
    icon: AlertCircle,
    iconClass: 'text-[#9B6E2E]',
    cardClass: 'bg-[#FDF5E8] border-[#E8C57A]',
  },
};

/**
 * Compact, read-only dose card for the family view.
 * Shows status with both icon + text (never color alone).
 */
export function DoseStatusCard({ dose, className }: DoseStatusCardProps) {
  const cfg = STATUS_CONFIG[dose.status];
  const Icon = cfg.icon;

  return (
    <article
      aria-label={`${dose.medicineName}: ${cfg.label} at ${dose.scheduledTime}`}
      className={cn(
        'flex items-center gap-3 rounded-xl border px-4 py-3 shadow-2xs',
        cfg.cardClass,
        className,
      )}
    >
      <Icon aria-hidden="true" size={20} className={cn('shrink-0', cfg.iconClass)} />
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-sm text-[#2D2318] truncate">{dose.medicineName}</p>
        <p className="text-xs text-[#5C4A3A]">{dose.scheduledTime}</p>
      </div>
      <span
        className={cn(
          'text-[11px] font-bold uppercase tracking-wide whitespace-nowrap px-2 py-0.5 rounded bg-white/70 border border-current/20',
          cfg.iconClass,
        )}
      >
        {cfg.label}
      </span>
    </article>
  );
}
