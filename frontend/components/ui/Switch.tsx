'use client';

import React from 'react';
import { cn } from '@/lib/utils';

export interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
}

export function Switch({ checked, onChange, label, description, disabled }: SwitchProps) {
  return (
    <label className="flex items-center justify-between gap-4 cursor-pointer select-none">
      {(label || description) && (
        <div className="flex flex-col">
          {label && <span className="text-base font-semibold text-[#2D2318]">{label}</span>}
          {description && <span className="text-sm text-[#5C4A38]">{description}</span>}
        </div>
      )}
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={cn(
          'relative inline-flex h-8 w-14 shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-4 focus:ring-[#C97B4B]/30',
          checked ? 'bg-[#5C8C5A]' : 'bg-[#D6CCC0]',
          disabled && 'opacity-50 cursor-not-allowed',
        )}
      >
        <span
          className={cn(
            'pointer-events-none inline-block h-7 w-7 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out',
            checked ? 'translate-x-6' : 'translate-x-0',
          )}
        />
      </button>
    </label>
  );
}

