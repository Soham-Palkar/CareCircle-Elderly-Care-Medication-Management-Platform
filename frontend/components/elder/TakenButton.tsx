'use client';

import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface TakenButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  justTaken?: boolean;
}

export const TakenButton = forwardRef<HTMLButtonElement, TakenButtonProps>(
  ({ loading, justTaken, className, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        aria-label={justTaken ? 'Marked as taken' : 'Mark as taken'}
        aria-busy={loading}
        className={cn(
          // Base sizing — elder-sized, minimum 48px height per requirements
          'flex items-center justify-center gap-3',
          'min-h-[72px] w-full rounded-2xl px-8 py-5',
          'text-[26px] font-bold leading-tight',
          // Warm sage-green for success action — AAA contrast
          'bg-[#2D6A4F] text-[#FAF8F5]',
          // States
          'transition-all duration-150',
          'focus:outline-none focus:ring-4 focus:ring-[#2D6A4F] focus:ring-offset-2',
          'active:scale-[0.98]',
          'disabled:opacity-60 disabled:cursor-not-allowed disabled:active:scale-100',
          justTaken && 'bg-[#1B4332]',
          className,
        )}
        {...props}
      >
        {loading ? (
          <>
            <Loader2 aria-hidden="true" size={30} className="animate-spin" />
            <span>Saving…</span>
          </>
        ) : (
          children
        )}
      </button>
    );
  },
);

TakenButton.displayName = 'TakenButton';
