'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export default function NewAppointmentPage() {
  const router = useRouter();
  const [doctorName, setDoctorName] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [location, setLocation] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.createAppointment({
        doctorName,
        specialty,
        location,
        scheduledAt,
        notes,
      });
      router.push('/care/appointments');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto flex flex-col gap-6 pb-16">
      <div className="flex items-center gap-3 border-b border-[#EBE4DB] pb-4">
        <Link
          href="/care/appointments"
          aria-label="Back to appointments list"
          className="p-2 bg-white border border-[#D6CCC0] rounded-lg text-[#2D2318] hover:bg-[#F2EDE6]"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-[#2D2318]">Schedule Doctor Appointment</h1>
          <p className="text-xs sm:text-sm text-[#5C4A38]">
            Set upcoming medical consultations with reminders for Savitri Devi
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-[#EBE4DB] rounded-xl p-5 sm:p-6 shadow-2xs flex flex-col gap-4">
        <Input
          label="Doctor / Clinic Name *"
          placeholder="e.g. Dr. Anand Mehta"
          value={doctorName}
          onChange={(e) => setDoctorName(e.target.value)}
          required
        />
        <Input
          label="Specialty / Purpose *"
          placeholder="e.g. Cardiology Check-up, Eye Screening"
          value={specialty}
          onChange={(e) => setSpecialty(e.target.value)}
          required
        />
        <Input
          label="Location / Hospital *"
          placeholder="e.g. City Care Hospital, Room 304"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          required
        />
        <Input
          label="Date & Time Description *"
          placeholder="e.g. Tomorrow at 10:30 AM or 2026-11-20 at 04:00 PM"
          value={scheduledAt}
          onChange={(e) => setScheduledAt(e.target.value)}
          required
        />
        <div className="flex flex-col gap-1.5">
          <label className="text-base font-semibold text-[#2D2318]">Preparation Notes</label>
          <textarea
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="e.g. Fasting required, bring previous blood pressure reports"
            className="w-full px-4 py-3 rounded-xl border border-[#D6CCC0] text-base text-[#2D2318] bg-white focus:border-[#C97B4B] focus:outline-none"
          />
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Link href="/care/appointments">
            <Button variant="secondary" type="button">
              Cancel
            </Button>
          </Link>
          <Button type="submit" variant="primary" loading={loading} disabled={!doctorName || !scheduledAt}>
            Save Appointment
          </Button>
        </div>
      </form>
    </div>
  );
}

