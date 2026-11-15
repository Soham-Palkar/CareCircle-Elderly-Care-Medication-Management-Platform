'use client';

import React, { useState } from 'react';
import { ArrowDown, Bell, Check, Clock, Mail, MessageSquare, Shield } from 'lucide-react';
import { Button } from '../ui/Button';

export function EscalationSettings() {
  const [saved, setSaved] = useState(false);
  const [l1Delay, setL1Delay] = useState(10);
  const [l2Delay, setL2Delay] = useState(30);
  const [l3Delay, setL3Delay] = useState(60);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="bg-white border border-[#EBE4DB] rounded-xl p-5 sm:p-6 shadow-2xs flex flex-col gap-5">
      <div>
        <h3 className="text-lg font-bold text-[#2D2318]">Escalation Ladder & Policy</h3>
        <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
          When a dose is not taken, CareCircle escalates progressively so family is informed without causing unnecessary alarm.
        </p>
      </div>

      {/* Visual Escalation Steps */}
      <div className="flex flex-col gap-2.5">
        {/* Level 0 */}
        <div className="p-3.5 bg-[#FAF8F5] border border-[#EBE4DB] rounded-lg flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-[#C97B4B] text-white flex items-center justify-center font-bold text-xs shrink-0">
            L0
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#2D2318] text-sm">Level 0: Due Time (0 min)</span>
              <span className="text-[11px] font-semibold text-[#8B7560]">Target: Elder</span>
            </div>
            <p className="text-xs text-[#5C4A38] mt-0.5">
              Gentle reminder in app and voice assistant for Savitri Devi.
            </p>
          </div>
        </div>

        <div className="flex justify-center text-[#8B7560]">
          <ArrowDown className="w-4 h-4" aria-hidden />
        </div>

        {/* Level 1 */}
        <div className="p-3.5 bg-[#FAF8F5] border border-[#EBE4DB] rounded-lg flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-[#A5622D] text-white flex items-center justify-center font-bold text-xs shrink-0">
            L1
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#2D2318] text-sm">Level 1: Repeat (+{l1Delay} mins)</span>
              <span className="text-[11px] font-semibold text-[#8B7560]">Target: Elder repeat</span>
            </div>
            <p className="text-xs text-[#5C4A38] mt-0.5">
              Second gentle prompt. Does not alarm caretakers yet.
            </p>
          </div>
        </div>

        <div className="flex justify-center text-[#8B7560]">
          <ArrowDown className="w-5 h-5" aria-hidden />
        </div>

        {/* Level 2 */}
        <div className="p-4 bg-[#FFF3E0] border border-[#FFB74D] rounded-2xl flex items-start gap-4">
          <div className="w-10 h-10 rounded-full bg-[#8C4E00] text-white flex items-center justify-center font-bold text-sm shrink-0">
            L2
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#8C4E00] text-base">
                Level 2: Missed Dose Escalation (+{l2Delay} mins)
              </span>
              <span className="text-xs font-semibold text-[#8C4E00] bg-white px-2 py-0.5 rounded-md border border-[#FFB74D]">
                Target: Caretaker (Rajesh)
              </span>
            </div>
            <p className="text-sm text-[#5C4A38] mt-1">
              Dose marked as missed. Caretaker alerted via Email and optional Telegram message.
            </p>
          </div>
        </div>

        <div className="flex justify-center text-[#8B7560]">
          <ArrowDown className="w-5 h-5" aria-hidden />
        </div>

        {/* Level 3 */}
        <div className="p-4 bg-[#FAEAEA] border border-[#E57373] rounded-2xl flex items-start gap-4">
          <div className="w-10 h-10 rounded-full bg-[#B71C1C] text-white flex items-center justify-center font-bold text-sm shrink-0">
            L3
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#B71C1C] text-base">
                Level 3: Family Safety Circle (+{l3Delay} mins)
              </span>
              <span className="text-xs font-semibold text-[#B71C1C] bg-white px-2 py-0.5 rounded-md border border-[#E57373]">
                Target: Family (Priya)
              </span>
            </div>
            <p className="text-sm text-[#5C4A38] mt-1">
              If unresolved after 1 hour, secondary family members receive notification to check in.
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-2">
        <Button variant="primary" onClick={handleSave} className="flex items-center gap-2">
          {saved ? <Check className="w-4 h-4" /> : <Shield className="w-4 h-4" />}
          <span>{saved ? 'Policy Saved!' : 'Save Escalation Policy'}</span>
        </Button>
      </div>
    </div>
  );
}

