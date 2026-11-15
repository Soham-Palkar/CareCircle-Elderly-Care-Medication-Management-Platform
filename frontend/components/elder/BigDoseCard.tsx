'use client';

import { useEffect, useRef, useState } from 'react';
import { CheckCircle2, Clock3, Utensils } from 'lucide-react';
import { TakenButton } from './TakenButton';
import { DoseStateLabel, type DoseState } from './DoseStateLabel';
import { cn } from '@/lib/utils';

export interface DoseInfo {
  id: string;
  medicationId: string;
  medicineName: string;
  strength?: string;
  form?: string;
  purposeCard?: string;        // plain-language "what it's for"
  scheduledTime: string;       // ISO or display string
  instructions?: string;       // "Take with food" etc.
  state: DoseState;
  stateDetail?: string;
}

interface BigDoseCardProps {
  dose: DoseInfo;
  onTaken: (id: string) => Promise<void>;
  onSnooze: (id: string) => Promise<void>;
  className?: string;
}

export function BigDoseCard({ dose, onTaken, onSnooze, className }: BigDoseCardProps) {
  const [takenLoading, setTakenLoading] = useState(false);
  const [snoozeLoading, setSnoozeLoading] = useState(false);
  const headingRef = useRef<HTMLHeadingElement>(null);

  // Focus medicine name when card mounts (a11y — announce new dose)
  useEffect(() => {
    headingRef.current?.focus();
  }, [dose.id]);

  const handleTaken = async () => {
    setTakenLoading(true);
    try {
      await onTaken(dose.id);
    } finally {
      setTakenLoading(false);
    }
  };

  const handleSnooze = async () => {
    setSnoozeLoading(true);
    try {
      await onSnooze(dose.id);
    } finally {
      setSnoozeLoading(false);
    }
  };

  const isFinal =
    dose.state === 'taken' ||
    dose.state === 'taken_late' ||
    dose.state === 'skipped' ||
    dose.state === 'missed';

  return (
    <article
      aria-label={`Next dose: ${dose.medicineName}`}
      className={cn(
        'bg-[#FAF8F5] border-2 border-[#E8D5B7] rounded-3xl p-8 shadow-lg',
        'flex flex-col gap-6',
        className,
      )}
    >
      {/* State badge */}
      <div>
        <DoseStateLabel state={dose.state} detail={dose.stateDetail} />
      </div>

      {/* Medicine name — biggest text on screen */}
      <h2
        ref={headingRef}
        tabIndex={-1}
        className="text-[42px] font-extrabold text-[#2D2318] leading-tight focus:outline-none"
      >
        {dose.medicineName}
        {dose.strength && (
          <span className="block text-[26px] font-semibold text-[#7A5A3A] mt-1">
            {dose.strength}
            {dose.form ? ` · ${dose.form}` : ''}
          </span>
        )}
      </h2>

      {/* What it's for */}
      {dose.purposeCard && (
        <p className="text-[24px] text-[#5C4A3A] leading-relaxed bg-[#FDF3E7] rounded-2xl px-6 py-4">
          {dose.purposeCard}
        </p>
      )}

      {/* Time + instructions row */}
      <div className="flex flex-wrap gap-4">
        <span className="inline-flex items-center gap-2 text-[22px] text-[#5C4A3A] font-medium">
          <Clock3 aria-hidden size={26} />
          <span>Scheduled: {dose.scheduledTime}</span>
        </span>
        {dose.instructions && (
          <span className="inline-flex items-center gap-2 text-[22px] text-[#5C4A3A] font-medium">
            <Utensils aria-hidden size={26} />
            <span>{dose.instructions}</span>
          </span>
        )}
      </div>

      {/* Actions — only when dose isn't already finalized */}
      {!isFinal && (
        <div className="flex flex-col gap-4 mt-2">
          {/* Primary: Taken */}
          <TakenButton
            onClick={handleTaken}
            loading={takenLoading}
            disabled={snoozeLoading}
          >
            <CheckCircle2 aria-hidden size={32} />
            <span>I took it</span>
          </TakenButton>

          {/* Secondary: Remind me later */}
          <button
            onClick={handleSnooze}
            disabled={takenLoading || snoozeLoading}
            aria-label="Remind me later — snooze this dose"
            aria-busy={snoozeLoading}
            className={cn(
              'flex items-center justify-center gap-3',
              'min-h-[64px] w-full rounded-2xl px-8 py-4',
              'text-[22px] font-semibold',
              'bg-[#F5EDE0] text-[#5C4A3A] border-2 border-[#E8D5B7]',
              'transition-all duration-150',
              'focus:outline-none focus:ring-4 focus:ring-[#C97B4B] focus:ring-offset-2',
              'active:scale-[0.98]',
              'disabled:opacity-60 disabled:cursor-not-allowed',
            )}
          >
            <Clock3 aria-hidden size={28} />
            <span>Remind me later</span>
          </button>
        </div>
      )}

      {/* Already taken / final state reassurance */}
      {(dose.state === 'taken' || dose.state === 'taken_late') && (
        <p className="text-[24px] text-[#2D6A4F] font-semibold text-center mt-2">
          ✓ You&apos;re all set for this one!
        </p>
      )}
    </article>
  );
}
