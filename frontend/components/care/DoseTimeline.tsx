'use client';

import React from 'react';
import { DoseEvent } from '@/lib/api/types';
import { DoseStateBadge } from '../ui/Badge';
import { Clock, CheckCircle2, User, Mic, Smartphone } from 'lucide-react';
import { Button } from '../ui/Button';

export function DoseTimeline({
  doses,
  onMarkTaken,
}: {
  doses: DoseEvent[];
  onMarkTaken?: (id: string) => void;
}) {
  return (
    <div className="flex flex-col gap-3 min-w-0">
      {doses.map((dose, index) => {
        const isTaken = dose.state === 'taken' || dose.state === 'taken_late';
        const isMissed = dose.state === 'missed';
        const isDue = dose.state === 'reminded' || dose.state === 'scheduled' || dose.state === 'snoozed';

        return (
          <div
            key={dose.id}
            className={`flex items-start gap-3 p-4 rounded-xl border transition-all min-w-0 ${
              isMissed
                ? 'bg-[#FAEAEA]/60 border-[#E57373]'
                : isDue
                ? 'bg-white border-[#C97B4B] shadow-2xs'
                : 'bg-white border-[#EBE4DB]'
            }`}
          >
            {/* Timeline sequence marker */}
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 ${
                isTaken
                  ? 'bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784]'
                  : isMissed
                  ? 'bg-[#FAEAEA] text-[#B71C1C] border border-[#E57373]'
                  : 'bg-[#FFF3E0] text-[#8C4E00] border border-[#FFB74D]'
              }`}
            >
              {index + 1}
            </div>

            {/* Dose details & actions */}
            <div className="flex-1 flex flex-col md:flex-row md:items-center justify-between gap-3 min-w-0">
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="text-base font-bold text-[#2D2318] truncate">
                    {dose.medication?.name || 'Scheduled Medicine'}
                  </h3>
                  <span className="text-xs font-semibold text-[#5C4A38]">
                    {dose.medication?.strength}
                  </span>
                  <DoseStateBadge state={dose.state} />
                </div>

                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[#5C4A38] mt-1 font-medium">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-[#8B7560]" aria-hidden />
                    <span>Scheduled: {dose.scheduledAt}</span>
                  </span>

                  {dose.takenAt && (
                    <span className="flex items-center gap-1 text-[#1B5E20]">
                      <CheckCircle2 className="w-3.5 h-3.5" aria-hidden />
                      <span>Taken at {dose.takenAt}</span>
                    </span>
                  )}

                  {dose.recordedVia && (
                    <span className="inline-flex items-center text-[11px] text-[#8B7560] bg-[#F2EDE6] px-1.5 py-0.5 rounded">
                      {dose.recordedVia === 'voice' && <Mic className="w-3 h-3 mr-0.5" />}
                      {dose.recordedVia === 'app' && <Smartphone className="w-3 h-3 mr-0.5" />}
                      <span>via {dose.recordedVia}</span>
                    </span>
                  )}
                </div>

                {dose.medication?.instructions && (
                  <p className="text-xs text-[#8B7560] mt-1 italic break-words">
                    {dose.medication.instructions}
                  </p>
                )}
              </div>

              {/* Action on behalf */}
              {!isTaken && onMarkTaken && (
                <div className="shrink-0 pt-1 md:pt-0">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onMarkTaken(dose.id)}
                    aria-label={`Mark ${dose.medication?.name} taken on behalf`}
                    className="flex items-center gap-1 text-xs font-bold border-[#D6CCC0] text-[#5C4A38] hover:border-[#C97B4B] hover:text-[#C97B4B] py-1 px-2.5 min-h-[32px]"
                  >
                    <User className="w-3 h-3" aria-hidden />
                    <span>Mark Taken on Behalf</span>
                  </Button>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
