'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { ArrowLeft, AlertTriangle, ShieldCheck, Check } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export default function NewMedicationPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [strength, setStrength] = useState('');
  const [form, setForm] = useState('Tablet');
  const [scheduleKind, setScheduleKind] = useState<'routine_anchor' | 'fixed_time'>('routine_anchor');
  const [timeOfDay, setTimeOfDay] = useState('08:30');
  const [anchor, setAnchor] = useState<'breakfast' | 'lunch' | 'dinner' | 'bedtime'>('breakfast');
  const [anchorOffset, setAnchorOffset] = useState(15);
  const [instructions, setInstructions] = useState('');
  const [purpose, setPurpose] = useState('');
  const [stockCount, setStockCount] = useState(30);
  const [refillThreshold, setRefillThreshold] = useState(5);
  const [criticality, setCriticality] = useState<'normal' | 'critical'>('normal');
  const [doctorConfirmed, setDoctorConfirmed] = useState(false);
  const [interactionWarning, setInteractionWarning] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Check name change for simulated drug duplicate or interaction advisory
  const handleNameChange = (val: string) => {
    setName(val);
    const clean = val.toLowerCase();
    if (clean.includes('amlodipine') || clean.includes('norvasc')) {
      setInteractionWarning(
        'Advisory: Amlodipine is already active in Savitri Devi’s schedule. Please ensure this is not an unintended duplicate order.',
      );
    } else if (clean.includes('ibuprofen') || clean.includes('aspirin')) {
      setInteractionWarning(
        'Advisory Note: NSAIDs like Ibuprofen may reduce the efficacy of blood pressure medications. Please verify safety with the treating physician.',
      );
    } else {
      setInteractionWarning(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!doctorConfirmed) return;
    setLoading(true);
    try {
      await api.createMedication({
        name,
        strength,
        form,
        instructions:
          instructions ||
          (scheduleKind === 'routine_anchor'
            ? `Take ${anchorOffset} mins after ${anchor}`
            : `Take at ${timeOfDay}`),
        purposeCard: {
          purpose: purpose || 'Prescribed health regimen',
          cautions: 'Report any side effects to caretaker or doctor.',
          advisoryDisclaimer: 'Advisory summary for daily routine.',
        },
        criticality,
        stockCount,
        refillThresholdDays: refillThreshold,
        confirmedWithDoctor: true,
      });
      router.push('/care/medications');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6 pb-16">
      <div className="flex items-center gap-3 border-b border-[#EBE4DB] pb-4">
        <Link
          href="/care/medications"
          aria-label="Back to medications list"
          className="p-2 bg-white border border-[#D6CCC0] rounded-lg text-[#2D2318] hover:bg-[#F2EDE6]"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-[#2D2318]">Add Medication Schedule</h1>
          <p className="text-xs sm:text-sm text-[#5C4A38]">
            Configure fixed or routine-anchored medicine times for Savitri Devi
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-[#EBE4DB] rounded-xl p-5 sm:p-6 shadow-2xs flex flex-col gap-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Medicine Name *"
            placeholder="e.g. Amlodipine, Metformin"
            value={name}
            onChange={(e) => handleNameChange(e.target.value)}
            required
          />
          <Input
            label="Strength & Unit *"
            placeholder="e.g. 5 mg, 500 mg"
            value={strength}
            onChange={(e) => setStrength(e.target.value)}
            required
          />
          <div className="flex flex-col gap-1.5">
            <label className="text-base font-semibold text-[#2D2318]">Dosage Form</label>
            <select
              value={form}
              onChange={(e) => setForm(e.target.value)}
              className="px-4 py-3 rounded-xl border border-[#D6CCC0] text-base text-[#2D2318] bg-white focus:border-[#C97B4B] focus:outline-none"
            >
              <option value="Tablet">Tablet</option>
              <option value="Capsule">Capsule</option>
              <option value="Syrup">Syrup</option>
              <option value="Drops">Eye/Ear Drops</option>
              <option value="Inhaler">Inhaler</option>
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-base font-semibold text-[#2D2318]">Criticality</label>
            <select
              value={criticality}
              onChange={(e) => setCriticality(e.target.value as any)}
              className="px-4 py-3 rounded-xl border border-[#D6CCC0] text-base text-[#2D2318] bg-white focus:border-[#C97B4B] focus:outline-none"
            >
              <option value="normal">Normal (Standard escalation)</option>
              <option value="critical">Critical (Accelerated escalation if missed)</option>
            </select>
          </div>
        </div>

        {/* Schedule Anchoring Sub-form */}
        <div className="bg-[#FAF8F5] p-6 rounded-2xl border border-[#D6CCC0] flex flex-col gap-4">
          <h3 className="text-lg font-bold text-[#2D2318]">Schedule & Reminder Anchor</h3>
          
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer text-sm font-semibold text-[#2D2318]">
              <input
                type="radio"
                name="scheduleKind"
                checked={scheduleKind === 'routine_anchor'}
                onChange={() => setScheduleKind('routine_anchor')}
                className="w-4 h-4 accent-[#C97B4B]"
              />
              <span>Routine Anchor (e.g. After breakfast)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-sm font-semibold text-[#2D2318]">
              <input
                type="radio"
                name="scheduleKind"
                checked={scheduleKind === 'fixed_time'}
                onChange={() => setScheduleKind('fixed_time')}
                className="w-4 h-4 accent-[#C97B4B]"
              />
              <span>Fixed Wall-Clock Time</span>
            </label>
          </div>

          {scheduleKind === 'routine_anchor' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-semibold text-[#5C4A38]">Anchor Routine</label>
                <select
                  value={anchor}
                  onChange={(e) => setAnchor(e.target.value as any)}
                  className="px-4 py-2.5 rounded-xl border border-[#D6CCC0] bg-white text-sm"
                >
                  <option value="breakfast">Breakfast (~08:30 AM)</option>
                  <option value="lunch">Lunch (~01:00 PM)</option>
                  <option value="dinner">Dinner (~08:00 PM)</option>
                  <option value="bedtime">Bedtime (~09:30 PM)</option>
                </select>
              </div>
              <Input
                label="Offset Minutes"
                type="number"
                value={anchorOffset}
                onChange={(e) => setAnchorOffset(Number(e.target.value))}
                helperText="Minutes after routine anchor (e.g. +15)"
              />
            </div>
          ) : (
            <Input
              label="Scheduled Time"
              type="time"
              value={timeOfDay}
              onChange={(e) => setTimeOfDay(e.target.value)}
            />
          )}
        </div>

        {/* Stock & Purpose */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Initial Stock Quantity"
            type="number"
            value={stockCount}
            onChange={(e) => setStockCount(Number(e.target.value))}
            helperText="Number of tablets/doses in packaging"
          />
          <Input
            label="Refill Alert Threshold (Days)"
            type="number"
            value={refillThreshold}
            onChange={(e) => setRefillThreshold(Number(e.target.value))}
            helperText="Alert when stock falls below this many days"
          />
        </div>

        <Input
          label="Plain-language Purpose (Shown to Elder)"
          placeholder="e.g. Helps keep your blood pressure steady and heart relaxed"
          value={purpose}
          onChange={(e) => setPurpose(e.target.value)}
        />

        {/* Advisory Warning if duplicate / interacting */}
        {interactionWarning && (
          <div role="alert" className="p-4 bg-[#FFF3E0] border border-[#FFB74D] rounded-2xl flex items-start gap-3 text-sm text-[#8C4E00]">
            <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5 text-[#C97B4B]" />
            <div>
              <span className="font-bold block">Advisory Interaction / Duplicate Warning:</span>
              <span>{interactionWarning}</span>
            </div>
          </div>
        )}

        {/* Doctor Check Confirmation (Required) */}
        <label className="flex items-start gap-3 p-4 bg-[#EEF5EE] border border-[#81C784] rounded-2xl cursor-pointer">
          <input
            type="checkbox"
            checked={doctorConfirmed}
            onChange={(e) => setDoctorConfirmed(e.target.checked)}
            className="mt-1 w-5 h-5 accent-[#1B5E20] rounded"
          />
          <div className="text-sm text-[#1B5E20]">
            <span className="font-bold block flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4" />
              Doctor Confirmation Safeguard (Mandatory):
            </span>
            <span>
              I confirm that this medication and dosage schedule have been checked and verified with the treating physician.
            </span>
          </div>
        </label>

        <div className="flex items-center justify-end gap-4 pt-2">
          <Link href="/care/medications">
            <Button variant="secondary" type="button">
              Cancel
            </Button>
          </Link>
          <Button
            type="submit"
            variant="primary"
            disabled={!doctorConfirmed || !name}
            loading={loading}
          >
            Save Active Schedule
          </Button>
        </div>
      </form>
    </div>
  );
}

