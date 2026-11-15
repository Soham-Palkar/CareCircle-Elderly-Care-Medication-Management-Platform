'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api/client';
import { HealthReading, RiskFlag, RiskForecastSlot, ScheduleProposal } from '@/lib/api/types';
import { FlagCard } from '@/components/care/FlagCard';
import { RiskForecast } from '@/components/care/RiskForecast';
import { ProposalCard } from '@/components/care/ProposalCard';
import { SimulatedBadge } from '@/components/common/SimulatedBadge';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { Cpu, HeartPulse, Activity, Plus, ShieldCheck, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Dialog } from '@/components/ui/Dialog';

export default function CareTwinPage() {
  const [readings, setReadings] = useState<HealthReading[]>([]);
  const [flags, setFlags] = useState<RiskFlag[]>([]);
  const [forecast, setForecast] = useState<RiskForecastSlot[]>([]);
  const [proposals, setProposals] = useState<ScheduleProposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [readingKind, setReadingKind] = useState<'heart_rate' | 'bp_sys' | 'sleep_hours' | 'glucose'>('heart_rate');
  const [readingVal, setReadingVal] = useState(72);
  const [readingSource, setReadingSource] = useState<'manual' | 'simulated'>('manual');

  const loadTwin = async () => {
    try {
      setLoading(true);
      const [r, f, fc, p] = await Promise.all([
        api.getHealthReadings(),
        api.getRiskFlags(),
        api.getForecast(),
        api.getProposals(),
      ]);
      setReadings(r);
      setFlags(f);
      setForecast(fc);
      setProposals(p);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTwin();
  }, []);

  const handleAddReading = async (e: React.FormEvent) => {
    e.preventDefault();
    const units = {
      heart_rate: 'bpm',
      bp_sys: 'mmHg',
      sleep_hours: 'hrs',
      glucose: 'mg/dL',
    };
    await api.addHealthReading({
      kind: readingKind,
      value: readingVal,
      unit: units[readingKind],
      source: readingSource,
    });
    setAddModalOpen(false);
    await loadTwin();
  };

  const handleDecideProposal = async (id: string, decision: 'approved' | 'rejected', elderConsent: boolean) => {
    await api.decideProposal(id, decision, elderConsent);
    await loadTwin();
  };

  if (loading) return <LoadingState message="Loading Digital Twin Guardian profile..." />;

  return (
    <div className="flex flex-col gap-6 pb-16">
      {/* Header with Advisory Notice */}
      <div className="border-b border-[#EBE4DB] pb-4">
        <div className="flex items-center gap-2 mb-0.5">
          <Cpu className="w-5 h-5 text-[#C97B4B]" aria-hidden />
          <h1 className="text-2xl font-bold text-[#2D2318]">Digital Twin Guardian</h1>
          <SimulatedBadge advisory />
        </div>
        <p className="text-xs sm:text-sm text-[#5C4A38]">
          Unified behavioural health profile combining dose history, routine biometrics, and explainable risk rules for Savitri Devi.
        </p>
      </div>

      {/* Advisory Disclaimer Notice */}
      <div className="p-3.5 bg-[#FFF8EE] border border-[#FFD59E] rounded-lg flex items-start gap-2.5 text-xs text-[#8C4E00]">
        <ShieldCheck className="w-4 h-4 shrink-0 mt-0.5 text-[#C97B4B]" />
        <div>
          <span className="font-bold block text-sm">Advisory Clinical Disclaimer:</span>
          <span>
            CareCircle Digital Twin is a reminder coordination and routine planning tool, not an authorized diagnostic medical device. All predictions, risk slots, and readings are labeled as advisory or simulated. Medication schedules require human confirmation and elder consent.
          </span>
        </div>
      </div>

      {/* 24-48h Miss-Risk Forecast */}
      <RiskForecast slots={forecast} />

      {/* Explainable Risk Flags */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-[#2D2318]">Explainable Risk Flags (R1–R6 Rules)</h2>
          <span className="text-xs font-semibold text-[#8B7560]">Rule Engine Active</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {flags.map((flag) => (
            <FlagCard key={flag.id} flag={flag} />
          ))}
        </div>
      </section>

      {/* Health Readings Section (Manual & Simulated) */}
      <section className="bg-white border border-[#EBE4DB] rounded-3xl p-6 shadow-sm flex flex-col gap-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EBE4DB] pb-4">
          <div>
            <h2 className="text-xl font-bold text-[#2D2318]">Health & Routine Readings</h2>
            <p className="text-xs text-[#5C4A38] mt-0.5">
              Readings labeled explicitly by source: Manual or Simulated.
            </p>
          </div>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setAddModalOpen(true)}
            className="flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Add Reading</span>
          </Button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {readings.map((reading) => (
            <div key={reading.id} className="p-4 bg-[#FAF8F5] rounded-2xl border border-[#D6CCC0] flex flex-col gap-1">
              <span className="text-xs font-bold text-[#8B7560] uppercase truncate">
                {reading.kind.replace('_', ' ')}
              </span>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-2xl font-black text-[#2D2318]">{reading.value}</span>
                <span className="text-xs font-semibold text-[#5C4A38]">{reading.unit}</span>
              </div>
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-[#EBE4DB] text-xs">
                <span className="text-[#8B7560]">{reading.recordedAt}</span>
                <span
                  className={`font-bold uppercase tracking-wider text-[10px] px-2 py-0.5 rounded ${
                    reading.source === 'simulated'
                      ? 'bg-[#FFF3E0] text-[#8C4E00] border border-[#FFB74D]'
                      : 'bg-[#EEF5EE] text-[#1B5E20]'
                  }`}
                >
                  {reading.source}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* What-If Schedule Proposals */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-[#2D2318]">What-If Schedule Proposals</h2>
            <p className="text-xs text-[#5C4A38] mt-0.5">
              Proposals are never auto-applied. Caretaker review and elder approval are mandatory.
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-4">
          {proposals.map((prop) => (
            <ProposalCard key={prop.id} proposal={prop} onDecide={handleDecideProposal} />
          ))}
        </div>
      </section>

      {/* Add Reading Dialog */}
      <Dialog
        open={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        title="Record Health Reading"
        description="Enter a biometric observation. Will be labeled accurately by source."
      >
        <form onSubmit={handleAddReading} className="flex flex-col gap-4 mt-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-semibold text-[#2D2318]">Biometric Type</label>
            <select
              value={readingKind}
              onChange={(e) => setReadingKind(e.target.value as any)}
              className="px-4 py-2.5 rounded-xl border border-[#D6CCC0] bg-white text-sm"
            >
              <option value="heart_rate">Heart Rate (bpm)</option>
              <option value="bp_sys">Systolic BP (mmHg)</option>
              <option value="sleep_hours">Sleep Hours (hrs)</option>
              <option value="glucose">Blood Glucose (mg/dL)</option>
            </select>
          </div>

          <Input
            label="Reading Value"
            type="number"
            value={readingVal}
            onChange={(e) => setReadingVal(Number(e.target.value))}
            required
          />

          <div className="flex flex-col gap-1">
            <label className="text-sm font-semibold text-[#2D2318]">Data Source Label</label>
            <select
              value={readingSource}
              onChange={(e) => setReadingSource(e.target.value as any)}
              className="px-4 py-2.5 rounded-xl border border-[#D6CCC0] bg-white text-sm"
            >
              <option value="manual">Manual Entry (Observed)</option>
              <option value="simulated">Simulated Data</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" type="button" onClick={() => setAddModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Save Reading
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
}

