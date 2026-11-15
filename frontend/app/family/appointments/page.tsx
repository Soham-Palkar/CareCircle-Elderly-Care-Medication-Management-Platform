'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api/client';
import { Appointment } from '@/lib/api/types';
import { LoadingState } from '@/components/common/FeedbackStates';
import { Calendar, Clock, MapPin, Stethoscope } from 'lucide-react';

export default function FamilyAppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAppointments().then((data) => {
      setAppointments(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingState message="Loading upcoming visits..." />;

  return (
    <div className="flex flex-col gap-6 pb-16">
      <div className="border-b border-[#EBE4DB] pb-4">
        <h1 className="text-2xl font-bold text-[#2D2318]">Doctor Appointments</h1>
        <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
          Upcoming consultations and health check-ups for Savitri Devi
        </p>
      </div>

      <div className="flex flex-col gap-3">
        {appointments.map((appt) => (
          <div key={appt.id} className="bg-white border border-[#EBE4DB] rounded-xl p-5 shadow-2xs flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Stethoscope className="w-5 h-5 text-[#C97B4B]" aria-hidden />
                <h3 className="text-lg font-bold text-[#2D2318]">{appt.doctorName}</h3>
                <span className="text-xs text-[#8B7560]">({appt.specialty})</span>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784]">
                {appt.status}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-sm text-[#5C4A38]">
              <span className="flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-[#8B7560]" />
                <span>{appt.scheduledAt}</span>
              </span>
              <span className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-[#8B7560]" />
                <span>{appt.location}</span>
              </span>
            </div>

            {appt.notes && (
              <p className="text-xs text-[#8B7560] bg-[#FAF8F5] p-3 rounded-xl border border-[#EBE4DB]">
                <strong>Notes:</strong> {appt.notes}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

