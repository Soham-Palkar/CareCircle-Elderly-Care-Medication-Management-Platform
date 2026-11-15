'use client';

import Link from 'next/link';
import { CheckCircle2, Clock3, ChevronRight } from 'lucide-react';
import { DoseStateLabel, type DoseState } from './DoseStateLabel';
import { cn } from '@/lib/utils';

export interface TodayDoseItem {
  id: string;
  medicationId: string;
  medicineName: string;
  strength?: string;
  scheduledTime: string;
  instructions?: string;
  state: DoseState;
  stateDetail?: string;
}

export interface TodayDoseListProps {
  doses: TodayDoseItem[];
  onTaken?: (id: string) => Promise<void>;
  onSnooze?: (id: string) => Promise<void>;
  className?: string;
}

export function TodayDoseList({ doses, className }: TodayDoseListProps) {
  if (doses.length === 0) {
    return (
      <div className="flex flex-col items-center gap-6 py-16 text-center">
        <CheckCircle2 aria-hidden size={80} className="text-[#2D6A4F]" />
        <p className="text-[28px] font-bold text-[#2D2318]">All done for today!</p>
        <p className="text-[22px] text-[#5C4A3A]">Great job taking care of yourself.</p>
      </div>
    );
  }

  return (
    <ul
      className={cn('flex flex-col gap-4', className)}
      aria-label="Today's doses"
      role="list"
    >
      {doses.map((dose) => (
        <li key={dose.id}>
          <Link
            href={`/elder/medicine/${dose.medicationId}`}
            className={cn(
              'flex items-center gap-4 p-5 rounded-2xl',
              'bg-[#FAF8F5] border-2 border-[#E8D5B7]',
              'min-h-[80px]',
              'focus:outline-none focus:ring-4 focus:ring-[#C97B4B] focus:ring-offset-2',
              'active:scale-[0.99] transition-transform',
              'hover:border-[#C97B4B]',
            )}
            aria-label={`${dose.medicineName}, scheduled ${dose.scheduledTime}, status: ${dose.state}`}
          >
            {/* Time */}
            <div className="flex flex-col items-center min-w-[72px]">
              <Clock3 aria-hidden size={24} className="text-[#7A5A3A]" />
              <span className="text-[20px] font-bold text-[#2D2318] mt-1">
                {dose.scheduledTime}
              </span>
            </div>

            {/* Name + state */}
            <div className="flex-1 min-w-0">
              <p className="text-[26px] font-bold text-[#2D2318] leading-tight truncate">
                {dose.medicineName} {dose.strength && <span className="text-xl text-[#7A5A3A]">({dose.strength})</span>}
              </p>
              <div className="mt-1">
                <DoseStateLabel
                  state={dose.state}
                  detail={dose.stateDetail}
                  className="text-[18px] py-1 px-3"
                />
              </div>
            </div>

            {/* Chevron */}
            <ChevronRight aria-hidden size={28} className="text-[#A08060] shrink-0" />
          </Link>
        </li>
      ))}
    </ul>
  );
}
