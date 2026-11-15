'use client';

import { cn } from '@/lib/utils';
import { AlertTriangle } from 'lucide-react';

export interface MissedDoseAlert {
  id: string;
  medicineName?: string;
  medicationName?: string;
  scheduledTime: string;
  escalationLevel: number | 'low' | 'medium' | 'high';
  targetContacted?: string;
  resolvedAt?: string;
  resolvedBy?: string;
}

export interface AlertListProps {
  alerts: MissedDoseAlert[];
  className?: string;
}

const ESCALATION_STYLES: Record<string, { label: string; classes: string }> = {
  low: {
    label: 'Low',
    classes: 'bg-[#FFF9EC] border-[#F4C774] text-[#8B6914]',
  },
  medium: {
    label: 'Attention',
    classes: 'bg-[#FFF3E0] border-[#E8963A] text-[#7A4A10]',
  },
  high: {
    label: 'Urgent',
    classes: 'bg-[#FFF0EE] border-[#D94F3D] text-[#8B1A0D]',
  },
  2: {
    label: 'Level 2 Escalation',
    classes: 'bg-[#FFF3E0] border-[#E8963A] text-[#7A4A10]',
  },
  3: {
    label: 'Level 3 Family Escalation',
    classes: 'bg-[#FFF0EE] border-[#D94F3D] text-[#8B1A0D]',
  },
};

function AlertItem({ alert }: { alert: MissedDoseAlert }) {
  const levelKey = String(alert.escalationLevel);
  const style = ESCALATION_STYLES[levelKey] || ESCALATION_STYLES.medium;
  const isResolved = !!alert.resolvedAt;
  const name = alert.medicineName || alert.medicationName || 'Scheduled Medicine';

  return (
    <li
      className={cn(
        'rounded-2xl border-2 p-5 flex gap-4 items-start',
        isResolved ? 'bg-[#F5F9F5] border-[#A8D5B5] opacity-70' : style.classes,
      )}
      aria-label={`${isResolved ? 'Resolved alert' : 'Active alert'}: ${name} missed at ${alert.scheduledTime}`}
    >
      <AlertTriangle
        aria-hidden="true"
        size={22}
        className={cn('mt-0.5 shrink-0', isResolved ? 'text-[#5A8F6A]' : '')}
      />
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-[1.05rem] leading-snug">
          {name}
        </p>
        <p className="text-sm mt-0.5">
          Missed dose scheduled for <strong>{alert.scheduledTime}</strong>
        </p>
        {alert.targetContacted && (
          <p className="text-xs text-[#5C4A38] mt-1">
            Escalation dispatched to: <strong>{alert.targetContacted}</strong>
          </p>
        )}
        {!isResolved && (
          <span
            className={cn(
              'inline-block mt-2 text-xs font-bold uppercase tracking-wide px-2 py-0.5 rounded-full',
              'bg-white/70 border border-current',
            )}
          >
            {style.label}
          </span>
        )}
        {isResolved && (
          <p className="text-xs mt-1 text-[#5A8F6A] font-medium">
            ✓ Acknowledged{alert.resolvedBy ? ` by ${alert.resolvedBy}` : ''}
          </p>
        )}
      </div>
    </li>
  );
}

export function AlertList({ alerts, className }: AlertListProps) {
  if (alerts.length === 0) {
    return (
      <div
        role="status"
        aria-live="polite"
        className={cn(
          'rounded-2xl bg-[#F0F7F2] border-2 border-[#A8D5B5] p-8 text-center',
          className,
        )}
      >
        <p className="text-2xl mb-1">🌟</p>
        <p className="font-semibold text-[#2D2318] text-lg">No missed doses recently.</p>
        <p className="text-[#5A8F6A] mt-1">Everything is on track.</p>
      </div>
    );
  }

  return (
    <ul
      aria-label="Missed dose alerts"
      className={cn('flex flex-col gap-3', className)}
    >
      {alerts.map((alert) => (
        <AlertItem key={alert.id} alert={alert} />
      ))}
    </ul>
  );
}
