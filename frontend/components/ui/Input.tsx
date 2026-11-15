'use client';

import React, { forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-base font-semibold text-[#2D2318]">
            {label}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-help` : undefined}
          className={cn(
            'w-full px-4 py-3 rounded-xl border text-base text-[#2D2318] bg-white transition-colors',
            'border-[#D6CCC0] focus:border-[#C97B4B] focus:outline-none focus:ring-4 focus:ring-[#C97B4B]/20',
            'disabled:bg-[#F2EDE6] disabled:text-[#8B7560]',
            error && 'border-[#B54040] focus:border-[#B54040] focus:ring-[#B54040]/20',
            className,
          )}
          {...props}
        />
        {error && (
          <p id={`${inputId}-error`} role="alert" className="text-sm font-medium text-[#B54040]">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p id={`${inputId}-help`} className="text-sm text-[#5C4A38]">
            {helperText}
          </p>
        )}
      </div>
    );
  },
);

Input.displayName = 'Input';

