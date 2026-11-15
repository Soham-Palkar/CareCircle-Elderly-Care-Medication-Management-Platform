'use client';

import React from 'react';
import { DoseEvent, Streak } from '@/lib/api/types';
import { CheckCircle2, AlertCircle } from 'lucide-react';

export function StatusSummary({
  doses,
  streak,
}: {
  doses: DoseEvent[];
  streak?: Streak;
}) {
  const total = doses.length;
  const taken = doses.filter((d) => d.state === 'taken' || d.state === 'taken_late').length;
  const missed = doses.filter((d) => d.state === 'missed').length;
  const due = doses.filter((d) => d.state === 'reminded' || d.state === 'scheduled').length;
  const allClear = missed === 0;

  return (
    <div className="bg-white border border-[#EBE4DB] rounded-xl p-5 sm:p-6 shadow-2xs flex flex-col gap-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EBE4DB] pb-3.5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-[#8B7560]">
              Daily Status Summary
            </span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-[#FAF8F5] text-[#8B7560] border border-[#D6CCC0]">
              Demo Data
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-[#2D2318] mt-0.5">
            Savitri Devi — Medication Schedule
          </h2>
        </div>

        {allClear ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784] w-fit">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>On Track Today</span>
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-[#FAEAEA] text-[#B71C1C] border border-[#E57373] w-fit">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>{missed} Missed Dose Recorded</span>
          </span>
        )}
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 bg-[#FAF8F5] rounded-lg border border-[#EBE4DB]">
          <span className="text-xs font-bold text-[#8B7560] uppercase block">Doses Taken</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-black text-[#1B5E20]">{taken}</span>
            <span className="text-xs font-semibold text-[#5C4A38]">/ {total}</span>
          </div>
          <span className="text-[11px] text-[#5C4A38] mt-0.5 block">Recorded today</span>
        </div>

        <div className="p-3.5 bg-[#FAF8F5] rounded-lg border border-[#EBE4DB]">
          <span className="text-xs font-bold text-[#8B7560] uppercase block">Remaining</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-black text-[#C97B4B]">{due}</span>
            <span className="text-xs font-semibold text-[#5C4A38]">upcoming</span>
          </div>
          <span className="text-[11px] text-[#5C4A38] mt-0.5 block">Scheduled later</span>
        </div>

        <div className="p-3.5 bg-[#FAF8F5] rounded-lg border border-[#EBE4DB]">
          <span className="text-xs font-bold text-[#8B7560] uppercase block">Missed</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-black text-[#B71C1C]">{missed}</span>
            <span className="text-xs font-semibold text-[#5C4A38]">alerts</span>
          </div>
          <span className="text-[11px] text-[#5C4A38] mt-0.5 block">Recorded</span>
        </div>

        <div className="p-3.5 bg-[#FAF8F5] rounded-lg border border-[#EBE4DB]">
          <span className="text-xs font-bold text-[#8B7560] uppercase block">Current Streak</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-black text-[#8C4E00]">{streak?.currentStreak || 4}</span>
            <span className="text-xs font-semibold text-[#8C4E00]">days</span>
          </div>
          <span className="text-[11px] text-[#5C4A38] mt-0.5 block">Consistent routine</span>
        </div>
      </div>

      <p className="text-xs sm:text-sm text-[#5C4A38] leading-relaxed bg-[#FAF8F5] p-3 rounded-lg border border-[#EBE4DB]">
        {allClear
          ? 'All scheduled doses for today have been recorded as taken or remain on schedule.'
          : 'A scheduled dose was reported as missed today. An alert was dispatched to the primary caretaker per circle escalation settings.'}
      </p>
    </div>
  );
}
