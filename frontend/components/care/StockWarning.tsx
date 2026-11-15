'use client';

import React from 'react';
import { Medication } from '@/lib/api/types';
import { AlertTriangle, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export function StockWarning({ medication }: { medication: Medication }) {
  const daysLeft = Math.floor(medication.stockCount / (medication.doseQuantity || 1));
  const isLow = daysLeft <= medication.refillThresholdDays;

  if (!isLow) return null;

  return (
    <div
      role="status"
      className="p-3.5 bg-[#FFF8EE] border border-[#FFD59E] rounded-xl flex items-center justify-between gap-3 text-xs sm:text-sm text-[#8C4E00]"
    >
      <div className="flex items-center gap-2.5 min-w-0">
        <AlertTriangle className="w-4 h-4 text-[#C97B4B] shrink-0" aria-hidden />
        <span className="font-medium truncate">
          <strong>Refill Needed:</strong> {medication.name} has {medication.stockCount} doses remaining (~{daysLeft} days).
        </span>
      </div>
      <Link
        href={`/care/medications/${medication.id}`}
        className="shrink-0 text-xs font-bold text-[#A5622D] hover:underline flex items-center gap-1"
      >
        <span>Details</span>
        <ArrowRight className="w-3 h-3" />
      </Link>
    </div>
  );
}
