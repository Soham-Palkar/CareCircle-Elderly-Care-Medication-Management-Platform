'use client';

import { useEffect, useRef, useState } from 'react';
import { CheckCircle2, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface UndoToastProps {
  visible?: boolean;
  medicineName?: string;
  message?: string;
  onUndo: () => void;
  onDismiss?: () => void;
  /** Countdown duration in ms or seconds */
  duration?: number;
  durationSeconds?: number;
}

export function UndoToast({
  visible = true,
  medicineName,
  message,
  onUndo,
  onDismiss,
  duration,
  durationSeconds,
}: UndoToastProps) {
  const actualDuration = duration || (durationSeconds ? durationSeconds * 1000 : 5000);
  const [remaining, setRemaining] = useState(actualDuration);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const undoBtnRef = useRef<HTMLButtonElement>(null);

  // Focus undo button when toast appears
  useEffect(() => {
    if (visible) {
      setRemaining(actualDuration);
      undoBtnRef.current?.focus();
    }
  }, [visible, actualDuration]);

  // Countdown timer
  useEffect(() => {
    if (!visible) return;
    intervalRef.current = setInterval(() => {
      setRemaining((r) => {
        if (r <= 100) {
          onDismiss?.();
          return 0;
        }
        return r - 100;
      });
    }, 100);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [visible, onDismiss]);

  if (!visible || remaining <= 0) return null;

  const pct = Math.round((remaining / actualDuration) * 100);

  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={`Marked as taken. You have ${Math.ceil(remaining / 1000)} seconds to undo.`}
      className={cn(
        'fixed bottom-28 left-4 right-4 z-50 max-w-xl mx-auto',
        'bg-[#2D6A4F] text-[#FAF8F5] rounded-2xl shadow-xl',
        'flex items-center gap-4 px-6 py-4',
        'animate-in slide-in-from-bottom-4 duration-200',
      )}
    >
      <CheckCircle2 aria-hidden size={32} className="shrink-0" />

      <div className="flex-1 min-w-0">
        <p className="text-[22px] font-bold leading-snug">
          {message || (medicineName ? `${medicineName} marked as taken!` : 'Marked as taken!')}
        </p>
        {/* Progress bar */}
        <div
          className="mt-2 h-2 bg-[#1B4332] rounded-full overflow-hidden"
          aria-hidden
        >
          <div
            className="h-full bg-[#95D5B2] rounded-full transition-all duration-100 ease-linear"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      <button
        ref={undoBtnRef}
        onClick={onUndo}
        aria-label="Undo — mark as not taken"
        className={cn(
          'shrink-0 px-5 py-3 rounded-xl text-[20px] font-bold',
          'bg-[#FAF8F5] text-[#2D6A4F]',
          'min-h-[48px] min-w-[80px]',
          'focus:outline-none focus:ring-4 focus:ring-[#FAF8F5] focus:ring-offset-2 focus:ring-offset-[#2D6A4F]',
          'active:scale-95 transition-transform cursor-pointer',
        )}
      >
        Undo
      </button>

      {onDismiss && (
        <button
          onClick={onDismiss}
          aria-label="Close this notification"
          className={cn(
            'shrink-0 p-2 rounded-xl min-h-[48px] min-w-[48px] flex items-center justify-center',
            'text-[#D8F3DC] hover:text-[#FAF8F5]',
            'focus:outline-none focus:ring-4 focus:ring-[#FAF8F5] focus:ring-offset-2 focus:ring-offset-[#2D6A4F]',
          )}
        >
          <X aria-hidden size={24} />
        </button>
      )}
    </div>
  );
}
