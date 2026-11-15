'use client';

import React from 'react';
import { AdherenceDaily, Streak } from '@/lib/api/types';
import { Flame, Award, CheckCircle2, AlertCircle } from 'lucide-react';

export function AdherenceChart({
  adherence,
  streak,
}: {
  adherence: AdherenceDaily[];
  streak?: Streak;
}) {
  const avg = Math.round(
    adherence.reduce((acc, curr) => acc + curr.adherencePct, 0) / (adherence.length || 1),
  );

  return (
    <div className="bg-white border border-[#EBE4DB] rounded-xl p-5 shadow-2xs flex flex-col gap-5">
      {/* Header with Adherence % & Streak */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EBE4DB] pb-3.5">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-[#8B7560]">
            7-Day Performance
          </span>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span className="text-3xl font-black text-[#2D2318]">{avg}%</span>
            <span className="text-xs font-semibold text-[#1B5E20]">Overall Adherence</span>
          </div>
        </div>

        {streak && (
          <div className="flex items-center gap-2.5 bg-[#FFF8EE] border border-[#FFD59E] px-3.5 py-1.5 rounded-lg">
            <Flame className="w-5 h-5 text-[#C97B4B]" aria-hidden />
            <div>
              <span className="text-[11px] font-bold uppercase text-[#8C4E00] block">
                Consistency Streak
              </span>
              <span className="text-base font-bold text-[#8C4E00]">
                {streak.currentStreak} Days Consecutive
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Bar Chart Representation with Accessible Patterns and Text */}
      <div className="flex flex-col gap-2">
        <h3 className="text-sm font-bold text-[#5C4A38]">Daily Breakdown (Last 7 Days)</h3>
        <div
          role="region"
          aria-label="Adherence chart for last 7 days"
          className="grid grid-cols-7 gap-2 sm:gap-4 pt-4 pb-2 items-end min-h-[160px]"
        >
          {adherence.map((item) => {
            const heightPct = Math.max(item.adherencePct, 15);
            const isFull = item.adherencePct === 100;
            const isLow = item.adherencePct < 70;

            return (
              <div key={item.date} className="flex flex-col items-center gap-2">
                <span className="text-xs font-bold text-[#2D2318]">{item.adherencePct}%</span>
                <div className="w-full max-w-[36px] bg-[#F2EDE6] rounded-t-lg overflow-hidden flex flex-col justify-end h-32">
                  <div
                    style={{ height: `${heightPct}%` }}
                    className={`w-full transition-all duration-500 rounded-t-lg ${
                      isFull
                        ? 'bg-[#5C8C5A]'
                        : isLow
                        ? 'bg-[#B54040]'
                        : 'bg-[#C97B4B]'
                    }`}
                  />
                </div>
                <span className="text-xs font-semibold text-[#5C4A38] truncate w-full text-center">
                  {item.date}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Accessible Text Summary Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-[#5C4A38]">
          <caption className="sr-only">Detailed daily dose adherence numbers</caption>
          <thead>
            <tr className="border-b border-[#EBE4DB] font-bold text-[#2D2318]">
              <th scope="col" className="pb-2">Date</th>
              <th scope="col" className="pb-2">Scheduled</th>
              <th scope="col" className="pb-2">Taken</th>
              <th scope="col" className="pb-2">Missed</th>
              <th scope="col" className="pb-2 text-right">Result</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F2EDE6]">
            {adherence.map((row) => (
              <tr key={row.date} className="py-1.5">
                <td className="py-2 font-medium text-[#2D2318]">{row.date}</td>
                <td className="py-2">{row.scheduledCount}</td>
                <td className="py-2 text-[#1B5E20] font-semibold">{row.takenCount}</td>
                <td className="py-2 text-[#B54040]">{row.missedCount}</td>
                <td className="py-2 text-right font-bold">
                  {row.adherencePct === 100 ? (
                    <span className="inline-flex items-center gap-1 text-[#1B5E20]">
                      <CheckCircle2 className="w-3.5 h-3.5" aria-hidden /> Complete
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[#8C4E00]">
                      <AlertCircle className="w-3.5 h-3.5" aria-hidden /> {row.adherencePct}%
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

