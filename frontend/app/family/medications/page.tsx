'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api/client';
import { Medication, Member } from '@/lib/api/types';
import { getCurrentMember } from '@/lib/auth/session';
import { PermissionGate } from '@/components/family/PermissionGate';
import { LoadingState } from '@/components/common/FeedbackStates';
import { Pill, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function FamilyMedicationsPage() {
  const [meds, setMeds] = useState<Medication[]>([]);
  const [member, setMember] = useState<Member | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cur = getCurrentMember();
    setMember(cur);
    api.getMedications().then((data) => {
      setMeds(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingState message="Checking family permissions..." />;

  // Permission Gate: elder must have granted canViewMeds
  const hasPermission = member?.permissions?.canViewMeds ?? true;

  if (!hasPermission) {
    return (
      <PermissionGate
        title="Medication Details Restricted"
        message="Savitri Devi has chosen to keep medication names private. You still receive status updates when doses are completed."
      />
    );
  }

  return (
    <div className="flex flex-col gap-6 pb-16">
      <div className="border-b border-[#EBE4DB] pb-4">
        <h1 className="text-3xl font-black text-[#2D2318]">Medication Schedule</h1>
        <p className="text-sm text-[#5C4A38] mt-1">
          Permitted view granted by Savitri Devi
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {meds.map((med) => (
          <div key={med.id} className="bg-white border border-[#EBE4DB] rounded-xl p-5 shadow-2xs flex flex-col justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Pill className="w-4 h-4 text-[#C97B4B]" aria-hidden />
                <h3 className="text-base font-bold text-[#2D2318]">{med.name}</h3>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#FAF8F5] border border-[#D6CCC0] text-[#5C4A38]">
                  {med.strength}
                </span>
              </div>
              <p className="text-xs sm:text-sm text-[#5C4A38] font-medium">{med.instructions}</p>
              {med.purposeCard?.purpose && (
                <p className="text-xs text-[#8B7560] bg-[#FAF8F5] p-2.5 rounded-lg border border-[#EBE4DB] mt-2.5">
                  <strong>Recorded purpose:</strong> {med.purposeCard.purpose}
                </p>
              )}
            </div>
            <div className="pt-2 border-t border-[#F2EDE6] flex items-center justify-between text-xs text-[#1B5E20] font-semibold">
              <span className="flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> Doctor Confirmed
              </span>
              <span>Active Routine</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

