'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api/client';
import { DoseEvent } from '@/lib/api/types';
import { TodayDoseList } from '@/components/elder/TodayDoseList';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { ArrowLeft } from 'lucide-react';

export default function ElderTodayPage() {
  const [doses, setDoses] = useState<DoseEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getTodayDoses();
      setDoses(data);
    } catch {
      setError('Could not load today’s schedule.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTaken = async (id: string) => {
    await api.markDoseTaken(id);
    await loadData();
  };

  const handleSnooze = async (id: string) => {
    await api.snoozeDose(id);
    await loadData();
  };

  if (loading) return <LoadingState message="Loading today's medicines..." />;
  if (error) return <ErrorState message={error} onRetry={loadData} />;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <Link
          href="/elder"
          aria-label="Back to main screen"
          className="p-3 bg-white border-2 border-[#D6CCC0] rounded-2xl text-[#1A150E] focus:outline-none focus:ring-4 focus:ring-[#C97B4B]"
        >
          <ArrowLeft className="w-8 h-8" aria-hidden />
        </Link>
        <div>
          <h1 className="text-4xl font-black text-[#1A150E]">Today&apos;s Medicines</h1>
          <p className="text-2xl text-[#5C4A38] font-medium">All doses scheduled for today</p>
        </div>
      </div>

      <TodayDoseList
        doses={doses.map((d) => ({
          id: d.id,
          medicationId: d.medicationId,
          medicineName: d.medication?.name || 'Medicine',
          strength: d.medication?.strength,
          scheduledTime: d.scheduledAt,
          instructions: d.medication?.instructions,
          state: d.state,
        }))}
        onTaken={handleTaken}
        onSnooze={handleSnooze}
      />
    </div>
  );
}

