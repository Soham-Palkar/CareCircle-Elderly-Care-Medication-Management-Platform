'use client';

import React, { useState } from 'react';
import { ScanDraft } from '@/lib/api/types';
import { Camera, Upload, AlertTriangle, CheckCircle2, ShieldCheck, Edit3 } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

export function ScanReview({
  draft,
  onConfirmSchedule,
}: {
  draft: ScanDraft;
  onConfirmSchedule?: (medData: any) => Promise<void>;
}) {
  const [step, setStep] = useState<'upload' | 'processing' | 'review' | 'confirmed'>('upload');
  const [name, setName] = useState(draft.extracted.name || 'Metformin Hydrochloride');
  const [strength, setStrength] = useState(draft.extracted.strength || '500 mg');
  const [form, setForm] = useState(draft.extracted.form || 'Film-coated Tablet');
  const [frequency, setFrequency] = useState(draft.extracted.frequency || 'Once daily after lunch');
  const [instructions, setInstructions] = useState(
    draft.extracted.instructions || 'Take 1 tablet with or after lunch',
  );
  const [doctorConfirmed, setDoctorConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSimulateScan = () => {
    setStep('processing');
    setTimeout(() => {
      setStep('review');
    }, 1200);
  };

  const handleFinalConfirm = async () => {
    if (!doctorConfirmed) return;
    setLoading(true);
    try {
      await onConfirmSchedule?.({
        name,
        strength,
        form,
        instructions,
        confirmedWithDoctor: true,
        source: 'scan',
      });
      setStep('confirmed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-[#EBE4DB] rounded-xl p-5 sm:p-6 shadow-2xs flex flex-col gap-5">
      {/* Privacy & Safe Scope Banner */}
      <div className="bg-[#FAF8F5] border border-[#EBE4DB] p-3.5 rounded-lg flex items-start gap-2.5">
        <ShieldCheck className="w-6 h-6 text-[#1B5E20] shrink-0 mt-0.5" aria-hidden />
        <div className="text-xs text-[#5C4A38] leading-relaxed">
          <p className="font-bold text-[#2D2318] mb-0.5">
            Privacy & Safety Notice:
          </p>
          <p>
            Supports printed prescription slips, medicine blister strips, and outer boxes.
            <strong> Loose pills are NOT identified.</strong> Images are stripped of EXIF data, processed as temporary drafts, and never activated without human doctor-check confirmation.
          </p>
        </div>
      </div>

      {step === 'upload' && (
        <div className="flex flex-col gap-6 items-center text-center py-6">
          <div className="flex items-center gap-4">
            <div className="p-4 bg-[#FFF3E0] rounded-2xl text-[#C97B4B]">
              <Camera className="w-10 h-10" aria-hidden />
            </div>
            <div className="p-4 bg-[#F2EDE6] rounded-2xl text-[#5C4A38]">
              <Upload className="w-10 h-10" aria-hidden />
            </div>
          </div>

          <div>
            <h3 className="text-2xl font-bold text-[#2D2318]">Upload Prescription or Packaging</h3>
            <p className="text-base text-[#5C4A38] mt-1 max-w-md">
              Take a photo or choose an image of the doctor&apos;s prescription slip or medicine box.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 w-full max-w-sm">
            <Button
              variant="primary"
              size="lg"
              onClick={handleSimulateScan}
              className="w-full flex items-center justify-center gap-2"
            >
              <Camera className="w-5 h-5" />
              <span>Use Camera</span>
            </Button>
            <Button
              variant="secondary"
              size="lg"
              onClick={handleSimulateScan}
              className="w-full flex items-center justify-center gap-2"
            >
              <Upload className="w-5 h-5" />
              <span>Choose Photo</span>
            </Button>
          </div>
        </div>
      )}

      {step === 'processing' && (
        <div className="flex flex-col items-center justify-center py-12 gap-4 text-center">
          <div className="w-14 h-14 border-4 border-[#C97B4B] border-t-transparent rounded-full animate-spin" />
          <h3 className="text-xl font-bold text-[#2D2318]">Reading Label & Extracting Details...</h3>
          <p className="text-sm text-[#8B7560]">
            Analyzing text confidence and matching known pharmaceutical formulations.
          </p>
        </div>
      )}

      {step === 'review' && (
        <div className="flex flex-col gap-6">
          <div className="flex items-center justify-between border-b border-[#EBE4DB] pb-3">
            <div>
              <span className="text-xs font-bold text-[#C97B4B] uppercase tracking-wider">
                Extracted Draft (Review Required)
              </span>
              <h3 className="text-xl font-bold text-[#2D2318]">Review Extracted Schedule</h3>
            </div>
            <span className="text-xs font-bold px-3 py-1 bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784] rounded-full">
              Confidence: {Math.round(draft.overallConfidence * 100)}%
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Medicine Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              helperText={`OCR confidence: ${Math.round(draft.extracted.confidence.name * 100)}%`}
            />
            <Input
              label="Strength"
              value={strength}
              onChange={(e) => setStrength(e.target.value)}
              helperText={`OCR confidence: ${Math.round(draft.extracted.confidence.strength * 100)}%`}
            />
            <Input
              label="Form"
              value={form}
              onChange={(e) => setForm(e.target.value)}
              helperText={`OCR confidence: ${Math.round(draft.extracted.confidence.form * 100)}%`}
            />
            <Input
              label="Frequency"
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              helperText={`OCR confidence: ${Math.round(draft.extracted.confidence.frequency * 100)}%`}
            />
            <div className="sm:col-span-2">
              <Input
                label="Instructions"
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                helperText="Editable instructions for daily routine reminders."
              />
            </div>
          </div>

          {/* Doctor Check Safeguard */}
          <label className="flex items-start gap-3 p-4 bg-[#FFF3E0] rounded-2xl border border-[#FFB74D] cursor-pointer">
            <input
              type="checkbox"
              checked={doctorConfirmed}
              onChange={(e) => setDoctorConfirmed(e.target.checked)}
              className="mt-1 w-5 h-5 accent-[#C97B4B] rounded"
            />
            <div className="text-sm text-[#8C4E00]">
              <span className="font-bold block">Human Doctor Confirmation (Mandatory):</span>
              <span>
                I confirm that I have reviewed the prescription label and verified this dose with the treating doctor.
              </span>
            </div>
          </label>

          <div className="flex justify-between items-center pt-2">
            <Button variant="ghost" onClick={() => setStep('upload')}>
              Scan Another
            </Button>
            <Button
              variant="primary"
              size="lg"
              disabled={!doctorConfirmed}
              loading={loading}
              onClick={handleFinalConfirm}
            >
              Confirm & Save to Active Schedule
            </Button>
          </div>
        </div>
      )}

      {step === 'confirmed' && (
        <div className="flex flex-col items-center text-center py-8 gap-4">
          <div className="p-4 bg-[#EEF5EE] rounded-full text-[#1B5E20]">
            <CheckCircle2 className="w-12 h-12" aria-hidden />
          </div>
          <h3 className="text-2xl font-bold text-[#1B5E20]">Schedule Confirmed and Saved!</h3>
          <p className="text-base text-[#5C4A38] max-w-md">
            {name} ({strength}) has been added to Savitri Devi&apos;s daily routine and will appear in her upcoming reminders.
          </p>
          <Button variant="secondary" onClick={() => setStep('upload')}>
            Scan Another Medication
          </Button>
        </div>
      )}
    </div>
  );
}

