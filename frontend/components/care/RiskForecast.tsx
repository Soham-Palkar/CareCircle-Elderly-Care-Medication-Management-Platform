'use client';

import React from 'react';
import { RiskForecastSlot } from '@/lib/api/types';
import { Clock, ShieldCheck, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { SimulatedBadge } from '../common/SimulatedBadge';

export function RiskForecast({ slots }: { slots: RiskForecastSlot[] }) {
  const riskBadges = {
    low: {
      label: 'Low Risk',
      icon: <ShieldCheck className="w-4 h-4 text-[#1B5E20]" aria-hidden />,
      style: 'bg-[#EEF5EE] text-[#1B5E20] border-[#81C784]',
    },
    medium: {
      label: 'Moderate Miss Risk',
      icon: <AlertTriangle className="w-4 h-4 text-[#8C4E00]" aria-hidden />,
      style: 'bg-[#FFF3E0] text-[#8C4E00] border-[#FFB74D]',
    },
    high: {
      label: 'High Miss Risk',
      icon: <AlertCircle className="w-4 h-4 text-[#B71C1C]" aria-hidden />,
      style: 'bg-[#FAEAEA] text-[#B71C1C] border-[#E57373]',
    },
  };

  return (
    <div className="bg-white border border-[#EBE4DB] rounded-xl p-5 shadow-2xs flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EBE4DB] pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-[#2D2318]">24–48h Slot Miss-Risk Forecast</h3>
            <SimulatedBadge advisory />
          </div>
          <p className="text-xs text-[#5C4A38] mt-0.5">
            Statistical Laplace-smoothed adherence forecast to help caretakers schedule timely reminders.
          </p>
        </div>
      </div>

      <div className="p-3 bg-[#FAF8F5] border border-[#EBE4DB] rounded-lg flex items-start gap-2.5 text-xs text-[#5C4A38]">
        <Info className="w-4 h-4 text-[#8B7560] shrink-0 mt-0.5" aria-hidden />
        <span>
          <strong>Advisory Forecast:</strong> This forecast reflects historical routine timing and does not predict medical events.
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {slots.map((slot, index) => {
          const config = riskBadges[slot.risk];
          return (
            <div
              key={index}
              className="p-3.5 bg-white border border-[#EBE4DB] rounded-lg shadow-2xs flex flex-col gap-2.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-[#8B7560]" aria-hidden />
                  <span className="font-bold text-[#2D2318] text-sm">{slot.slot}</span>
                  <span className="text-xs font-semibold text-[#8B7560]">({slot.time})</span>
                </div>
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold border ${config.style}`}
                >
                  {config.icon}
                  <span>{config.label}</span>
                </span>
              </div>

              <p className="text-xs text-[#5C4A38] font-medium leading-relaxed">
                Evidence: {slot.evidence}
              </p>

              <div className="text-[11px] text-[#8B7560] flex items-center justify-between pt-1 border-t border-[#F2EDE6]">
                <span>Date: {slot.date}</span>
                <span>Probability: {Math.round(slot.missProbability * 100)}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

