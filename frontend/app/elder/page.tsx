'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api/client';
import { DoseEvent } from '@/lib/api/types';
import { BigDoseCard } from '@/components/elder/BigDoseCard';
import { UndoToast } from '@/components/elder/UndoToast';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { CheckCircle2, Calendar, ArrowRight, HelpCircle } from 'lucide-react';
import { announce } from '@/lib/a11y/announcements';

export default function ElderHomePage() {
  const [dose, setDose] = useState<DoseEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [undoDoseId, setUndoDoseId] = useState<string | null>(null);
  const [undoToken, setUndoToken] = useState<string | null>(null);
  const [remainingCount, setRemainingCount] = useState(0);

  const loadDose = async () => {
    try {
      setLoading(true);
      setError(null);
      const next = await api.getNextDose();
      setDose(next);
      const allToday = await api.getTodayDoses();
      const remaining = allToday.filter((d) => d.state !== 'taken' && d.state !== 'taken_late').length;
      setRemainingCount(remaining);
      if (next) {
        announce(`Next due dose: ${next.medication?.name || 'Scheduled medicine'}`);
      }
    } catch {
      setError('Could not load your medicine information. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDose();
  }, []);

  const handleTaken = async (id: string) => {
    try {
      const updated = await api.markDoseTaken(id);
      setDose(updated);
      setUndoDoseId(id);
      setUndoToken(updated.undoToken || 'token');
      announce('Dose recorded as taken. Undo available for 10 seconds.');
    } catch (e) {
      console.error(e);
    }
  };

  const handleSnooze = async (id: string) => {
    try {
      const updated = await api.snoozeDose(id, 15);
      setDose(updated);
      announce('Dose postponed for 15 minutes.');
    } catch (e) {
      console.error(e);
    }
  };

  const handleUndo = async () => {
    if (!undoDoseId || !undoToken) return;
    try {
      const reverted = await api.undoDoseAction(undoDoseId, undoToken);
      setDose(reverted);
      setUndoDoseId(null);
      setUndoToken(null);
      announce('Action undone. Dose is marked due again.');
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <LoadingState message="Loading your next medicine..." />;
  if (error) return <ErrorState message={error} onRetry={loadDose} />;

  return (
    <div className="flex flex-col gap-8 pb-10">
      {/* Greeting Header */}
      <header className="border-b-2 border-[#EBE4DB] pb-6">
        <h1 className="text-4xl sm:text-5xl font-black text-[#1A150E] tracking-tight">
          Namaste, Savitri ji
        </h1>
        <p className="text-2xl text-[#5C4A38] font-semibold mt-2 flex items-center gap-3">
          <Calendar className="w-7 h-7 text-[#A5622D]" aria-hidden />
          <span>Today is Sunday, November 15</span>
        </p>
      </header>

      {/* Main Focus: Big Dose Card */}
      {dose ? (
        <section aria-label="Next Due Medicine">
          <BigDoseCard
            dose={{
              id: dose.id,
              medicationId: dose.medicationId,
              medicineName: dose.medication?.name || 'Amlodipine',
              strength: dose.medication?.strength || '5 mg',
              form: dose.medication?.form || 'Tablet',
              purposeCard: dose.medication?.purposeCard?.purpose || 'Helps keep your blood pressure steady and heart relaxed.',
              scheduledTime: dose.scheduledAt,
              instructions: dose.medication?.instructions || 'Take 1 tablet after breakfast with water',
              state: dose.state,
            }}
            onTaken={handleTaken}
            onSnooze={handleSnooze}
          />
        </section>
      ) : (
        <div className="bg-[#EEF5EE] border-3 border-[#81C784] rounded-3xl p-10 text-center flex flex-col items-center gap-4">
          <CheckCircle2 className="w-20 h-20 text-[#1B5E20]" aria-hidden />
          <h2 className="text-4xl font-black text-[#1B5E20]">All Done for Today!</h2>
          <p className="text-2xl text-[#2D2318] font-semibold max-w-lg">
            You have completed all your scheduled medicines. Enjoy your afternoon with peace of mind.
          </p>
        </div>
      )}

      {/* Today's Schedule Overview Link */}
      <section className="bg-white border-2 border-[#D6CCC0] rounded-3xl p-6 shadow-xs flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[#1A150E]">Today&apos;s Medicine Schedule</h2>
          <p className="text-xl text-[#5C4A38] mt-1 font-medium">
            {remainingCount > 0 ? `${remainingCount} more medicine slot(s) today` : 'All scheduled doses taken'}
          </p>
        </div>
        <Link
          href="/elder/today"
          className="flex items-center gap-2 text-2xl font-bold text-[#A5622D] hover:underline p-3 focus:outline-none focus:ring-4 focus:ring-[#C97B4B] rounded-2xl"
          aria-label="View full today's dose schedule"
        >
          <span>View list</span>
          <ArrowRight className="w-7 h-7" aria-hidden />
        </Link>
      </section>

      {/* Urgent Help Section */}
      <section className="border-t-2 border-[#EBE4DB] pt-6 flex justify-center">
        <Link
          href="/elder/help"
          className="w-full min-h-[64px] bg-[#FFEBEE] border-2 border-[#E57373] text-[#B71C1C] hover:bg-[#FFCDD2] rounded-3xl flex items-center justify-center gap-3 text-2xl font-extrabold focus:outline-none focus:ring-4 focus:ring-[#B71C1C]"
        >
          <HelpCircle className="w-8 h-8" aria-hidden />
          <span>I need help or feel unwell</span>
        </Link>
      </section>

      {/* Accidental Tap Undo Toast */}
      {undoDoseId && (
        <UndoToast
          message="Marked as taken. Did you tap by mistake?"
          onUndo={handleUndo}
          durationSeconds={10}
        />
      )}
    </div>
  );
}

