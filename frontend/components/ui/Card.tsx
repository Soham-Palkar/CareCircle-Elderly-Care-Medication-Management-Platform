'use client';

import React from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'elder';
}

export function Card({ className, variant = 'default', children, ...props }: CardProps) {
  const variants = {
    default: 'bg-white border border-[#EBE4DB] shadow-2xs rounded-xl p-5',
    elevated: 'bg-white border border-[#D6CCC0] shadow-xs rounded-xl p-6',
    elder: 'bg-white border-2 border-[#D6CCC0] shadow-sm rounded-2xl p-6 sm:p-8',
  };

  return (
    <div className={cn(variants[variant], className)} {...props}>
      {children}
    </div>
  );
}
