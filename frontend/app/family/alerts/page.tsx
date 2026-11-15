'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api/client';
import { DoseEvent } from '@/lib/api/types';
import { AlertList } from '@/components/family/AlertList';
import { LoadingState } from '@/components/common/FeedbackStates';
import { Bell, CheckCircle2 } from 'lucide-react';

export default function FamilyAlertsPage() {
  const [doses, setDoses] = useState<DoseEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTodayDoses().then((d) => {
      setDoses(d);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingState message="Loading alert history..." />;

  const missedDoses = doses.filter((d) => d.state === 'missed');

  return (
    <div className="flex flex-col gap-6 pb-16">
      <div className="border-b border-[#EBE4DB] pb-4">
        <h1 className="text-2xl font-bold text-[#2D2318]">Alerts & Escalation Log</h1>
        <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
          Historical record of missed doses and caregiver outreach
        </p>
      </div>

      {missedDoses.length === 0 ? (
        <div className="bg-[#EEF5EE] border border-[#81C784] rounded-xl p-6 text-center flex flex-col items-center gap-2.5 shadow-2xs">
          <CheckCircle2 className="w-8 h-8 text-[#1B5E20]" aria-hidden />
          <h2 className="text-lg font-bold text-[#1B5E20]">No Active Missed Dose Alerts</h2>
          <p className="text-xs sm:text-sm text-[#2D2318] max-w-md">
            Savitri Devi has taken her scheduled doses without any unresolved escalation.
          </p>
        </div>
      ) : (
        <AlertList
          alerts={missedDoses.map((d) => ({
            id: d.id,
            medicationName: d.medication?.name || 'Scheduled Medicine',
            scheduledTime: d.scheduledAt,
            escalationLevel: d.escalationLevel || 2,
            targetContacted: 'Rajesh Sharma (Caretaker)',
          }))}
        />
      )}
    </div>
  );
}

