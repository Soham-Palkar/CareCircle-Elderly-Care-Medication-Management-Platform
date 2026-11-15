'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api/client';
import { DoseEvent, Streak, Appointment } from '@/lib/api/types';
import { StatusSummary } from '@/components/family/StatusSummary';
import { DoseStatusCard } from '@/components/family/DoseStatusCard';
import { LoadingState } from '@/components/common/FeedbackStates';
import { Calendar, ArrowRight, HeartHandshake } from 'lucide-react';
import Link from 'next/link';

export default function FamilyHomePage() {
  const [doses, setDoses] = useState<DoseEvent[]>([]);
  const [streak, setStreak] = useState<Streak | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getTodayDoses(), api.getTwinProfile(), api.getAppointments()])
      .then(([d, twin, a]) => {
        setDoses(d);
        setStreak(twin.streak);
        setAppointments(a);
        setLoading(false);
      });
  }, []);

  if (loading) return <LoadingState message="Checking in on Savitri Devi..." />;

  return (
    <div className="flex flex-col gap-6 pb-16">
      {/* Header */}
      <div className="border-b border-[#EBE4DB] pb-4">
        <h1 className="text-2xl font-bold text-[#2D2318]">Family Circle</h1>
        <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
          Connected with Savitri Devi · Staying informed with peace of mind
        </p>
      </div>

      {/* Prominent Status-First Summary */}
      <StatusSummary doses={doses} streak={streak || undefined} />

      {/* Today's Dose Status List */}
      <section className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-[#2D2318]">Today&apos;s Doses</h2>
          <Link href="/family/medications" className="text-xs font-bold text-[#A5622D] hover:underline">
            View All Medications
          </Link>
        </div>

        <div className="flex flex-col gap-3">
          {doses.map((dose) => {
            const mappedStatus =
              dose.state === 'taken'
                ? 'taken'
                : dose.state === 'taken_late'
                ? 'taken_late'
                : dose.state === 'missed'
                ? 'missed'
                : dose.state === 'skipped'
                ? 'skipped'
                : 'scheduled';

            return (
              <DoseStatusCard
                key={dose.id}
                dose={{
                  id: dose.id,
                  medicineName: dose.medication?.name || 'Scheduled Medicine',
                  scheduledTime: dose.scheduledAt,
                  status: mappedStatus,
                }}
              />
            );
          })}
        </div>
      </section>

      {/* Next Appointment Card */}
      {appointments.length > 0 && (
        <section className="bg-white border border-[#EBE4DB] rounded-xl p-5 shadow-2xs flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-[#2D2318] flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-[#C97B4B]" aria-hidden />
              <span>Next Doctor Appointment</span>
            </h3>
            <Link href="/family/appointments" className="text-xs font-bold text-[#A5622D] hover:underline">
              All Visits
            </Link>
          </div>
          <div className="p-3.5 bg-[#FAF8F5] rounded-lg border border-[#EBE4DB]">
            <span className="font-bold text-sm text-[#2D2318] block">
              {appointments[0].doctorName} ({appointments[0].specialty})
            </span>
            <span className="text-xs text-[#5C4A38] block mt-0.5">
              Time: {appointments[0].scheduledAt} · Location: {appointments[0].location}
            </span>
          </div>
        </section>
      )}
    </div>
  );
}
