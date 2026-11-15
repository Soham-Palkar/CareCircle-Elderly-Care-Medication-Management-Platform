'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api/client';
import { AdherenceDaily, Streak, Medication } from '@/lib/api/types';
import { AdherenceChart } from '@/components/care/AdherenceChart';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { Award, Flame, Heart, CheckCircle2 } from 'lucide-react';

export default function CareAdherencePage() {
  const [adherence, setAdherence] = useState<AdherenceDaily[]>([]);
  const [streak, setStreak] = useState<Streak | null>(null);
  const [meds, setMeds] = useState<Medication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.getTwinProfile(), api.getMedications()])
      .then(([twin, m]) => {
        setAdherence(twin.adherence);
        setStreak(twin.streak);
        setMeds(m);
        setLoading(false);
      })
      .catch(() => {
        setError('Could not load adherence statistics.');
        setLoading(false);
      });
  }, []);

  if (loading) return <LoadingState message="Loading adherence reports..." />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="flex flex-col gap-6 pb-16">
      <div className="border-b border-[#EBE4DB] pb-4">
        <h1 className="text-2xl font-bold text-[#2D2318]">Adherence & Streaks</h1>
        <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
          Longitudinal adherence tracking and family routine consistency for Savitri Devi
        </p>
      </div>

      {/* 7-day Adherence Chart Component */}
      <AdherenceChart adherence={adherence} streak={streak || undefined} />

      {/* Relationship-based Reward Highlight */}
      <div className="p-5 bg-[#FAF8F5] border border-[#EBE4DB] rounded-xl flex items-start gap-3.5 shadow-2xs">
        <div className="p-2.5 bg-[#FFF3E0] rounded-lg text-[#C97B4B] shrink-0 mt-0.5">
          <Heart className="w-5 h-5" aria-hidden />
        </div>
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-[#8C4E00]">
            Routine Motivation
          </span>
          <h3 className="text-base font-bold text-[#2D2318] mt-0.5">
            Upcoming Reward: Grandchildren Video Call at 7-Day Streak!
          </h3>
          <p className="text-sm text-[#5C4A38] mt-1 font-medium">
            Instead of empty gamified badges or points, CareCircle celebrates consistent care routines with shared family moments. Only 3 more days to unlock a surprise photo album update from Priya!
          </p>
        </div>
      </div>

      {/* Per-Medication Summary Breakdown */}
      <div className="bg-white border border-[#EBE4DB] rounded-3xl p-6 shadow-sm flex flex-col gap-4">
        <h3 className="text-xl font-bold text-[#2D2318]">Per-Medication Breakdown</h3>
        <div className="divide-y divide-[#F2EDE6]">
          {meds.map((med) => (
            <div key={med.id} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <span className="font-bold text-base text-[#2D2318] block">{med.name}</span>
                <span className="text-xs text-[#5C4A38]">{med.strength} · {med.form}</span>
              </div>
              <div className="flex items-center gap-6">
                <span className="text-xs text-[#8B7560]">Criticality: <strong>{med.criticality}</strong></span>
                <span className="text-sm font-bold text-[#1B5E20] flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> 95% Consistent
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

