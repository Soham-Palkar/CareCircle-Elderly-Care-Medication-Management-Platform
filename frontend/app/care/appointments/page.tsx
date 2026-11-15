'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api/client';
import { Appointment } from '@/lib/api/types';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { Plus, Calendar, MapPin, Clock, Stethoscope, XCircle, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function CareAppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAppointments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getAppointments();
      setAppointments(data);
    } catch {
      setError('Could not load appointments.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAppointments();
  }, []);

  const handleCancel = async (id: string) => {
    await api.cancelAppointment(id);
    await loadAppointments();
  };

  if (loading) return <LoadingState message="Loading appointments..." />;
  if (error) return <ErrorState message={error} onRetry={loadAppointments} />;

  return (
    <div className="flex flex-col gap-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EBE4DB] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-[#2D2318]">Appointments Management</h1>
          <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
            Doctor visits and check-ups scheduled for Savitri Devi
          </p>
        </div>
        <Link href="/care/appointments/new">
          <Button variant="primary" size="sm" className="flex items-center gap-1.5 font-bold">
            <Plus className="w-4 h-4" />
            <span>Schedule Appointment</span>
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {appointments.map((appt) => {
          const isCancelled = appt.status === 'cancelled';
          return (
            <div
              key={appt.id}
              className={`bg-white border rounded-xl p-5 shadow-2xs flex flex-col justify-between gap-3.5 ${
                isCancelled ? 'border-[#EBE4DB] opacity-60' : 'border-[#EBE4DB]'
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <Stethoscope className="w-6 h-6 text-[#C97B4B]" aria-hidden />
                    <h3 className="text-xl font-bold text-[#2D2318]">{appt.doctorName}</h3>
                  </div>
                  <span
                    className={`text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded-full ${
                      isCancelled
                        ? 'bg-[#FAEAEA] text-[#B71C1C]'
                        : 'bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784]'
                    }`}
                  >
                    {appt.status}
                  </span>
                </div>

                <div className="flex flex-col gap-2 text-sm text-[#5C4A38]">
                  <p className="font-semibold text-[#2D2318]">{appt.specialty}</p>
                  <p className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-[#8B7560]" aria-hidden />
                    <span>{appt.scheduledAt}</span>
                  </p>
                  <p className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-[#8B7560]" aria-hidden />
                    <span>{appt.location}</span>
                  </p>
                  {appt.notes && (
                    <p className="text-xs text-[#8B7560] bg-[#FAF8F5] p-2.5 rounded-xl border border-[#EBE4DB] mt-2">
                      <strong>Notes:</strong> {appt.notes}
                    </p>
                  )}
                </div>
              </div>

              {!isCancelled && (
                <div className="flex items-center justify-between border-t border-[#F2EDE6] pt-3">
                  <span className="text-xs text-[#8B7560]">
                    Email reminders active (24h & 2h before)
                  </span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleCancel(appt.id)}
                    className="text-xs text-[#B54040] hover:bg-[#FAEAEA]"
                  >
                    <XCircle className="w-3.5 h-3.5 mr-1" />
                    <span>Cancel Visit</span>
                  </Button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

