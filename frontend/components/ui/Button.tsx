'use client';

import React, { forwardRef } from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'destructive' | 'ghost' | 'elderPrimary' | 'elderSecondary';
  size?: 'sm' | 'md' | 'lg' | 'elder';
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, disabled, children, ...props }, ref) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium rounded-xl transition-all duration-150 focus:outline-none focus:ring-4 focus:ring-[#C97B4B] focus:ring-offset-2 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none select-none';

    const variants = {
      primary: 'bg-[#C97B4B] text-white hover:bg-[#A5622D] shadow-sm',
      secondary: 'bg-[#F2EDE6] text-[#2D2318] hover:bg-[#EBE4DB] border border-[#D6CCC0]',
      outline: 'bg-transparent text-[#2D2318] border-2 border-[#D6CCC0] hover:bg-[#F2EDE6]',
      destructive: 'bg-[#B54040] text-white hover:bg-[#8C2D2D]',
      ghost: 'bg-transparent text-[#5C4A38] hover:bg-[#F2EDE6]',
      // Elderly mode variants (7:1 contrast guaranteed)
      elderPrimary:
        'bg-[#1B5E20] text-white hover:bg-[#144717] border-2 border-[#81C784] font-bold shadow-md min-h-[64px]',
      elderSecondary:
        'bg-[#F5EDE0] text-[#2D2318] hover:bg-[#EBE4DB] border-2 border-[#C4B29F] font-semibold min-h-[56px]',
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-sm min-h-[36px]',
      md: 'px-5 py-2.5 text-base min-h-[48px]', // WCAG AA minimum 48px
      lg: 'px-6 py-3.5 text-lg min-h-[52px]',
      elder: 'px-8 py-4 text-2xl min-h-[64px] rounded-2xl', // WCAG AAA Elderly Mode
    };

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {loading && <Loader2 className="mr-2 h-5 w-5 animate-spin" />}
        {children}
      </button>
    );
  },
);

Button.displayName = 'Button';

