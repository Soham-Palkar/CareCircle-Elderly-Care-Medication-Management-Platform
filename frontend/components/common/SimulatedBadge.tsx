'use client';

import React from 'react';
import { Sparkles, Info } from 'lucide-react';

export function SimulatedBadge({ advisory = false }: { advisory?: boolean }) {
  if (advisory) {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold tracking-wider bg-[#FFF3E0] text-[#8C4E00] border border-[#FFB74D]">
        <Info className="w-3.5 h-3.5" aria-hidden />
        <span>ADVISORY PREDICTION</span>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold tracking-wider bg-[#FDF3EB] text-[#8C4E00] border-2 border-dashed border-[#C97B4B]">
      <Sparkles className="w-3.5 h-3.5" aria-hidden />
      <span>SIMULATED DATA</span>
    </span>
  );
}

