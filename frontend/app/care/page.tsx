'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api/client';
import { DoseEvent, Appointment, RiskFlag, AdherenceDaily, Streak, Medication } from '@/lib/api/types';
import { useSSE } from '@/lib/realtime/useSSE';
import { DoseTimeline } from '@/components/care/DoseTimeline';
import { FlagCard } from '@/components/care/FlagCard';
import { ConnectionStatus } from '@/components/care/ConnectionStatus';
import { StockWarning } from '@/components/care/StockWarning';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { Plus, Calendar, ArrowRight, Flame, ShieldAlert, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function CareDashboardPage() {
  const { status: sseStatus, reconnect } = useSSE();
  const [doses, setDoses] = useState<DoseEvent[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [flags, setFlags] = useState<RiskFlag[]>([]);
  const [adherence, setAdherence] = useState<AdherenceDaily[]>([]);
  const [streak, setStreak] = useState<Streak | null>(null);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const [d, a, f, twin, m] = await Promise.all([
        api.getTodayDoses(),
        api.getAppointments(),
        api.getRiskFlags(),
        api.getTwinProfile(),
        api.getMedications(),
      ]);
      setDoses(d);
      setAppointments(a);
      setFlags(f);
      setAdherence(twin.adherence);
      setStreak(twin.streak);
      setMedications(m);
    } catch {
      setError('Could not load caretaker dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleMarkTaken = async (doseId: string) => {
    await api.markDoseTaken(doseId);
    await loadDashboard();
  };

  const handleAcknowledgeFlag = async (flagId: string) => {
    await api.acknowledgeFlag(flagId);
    await loadDashboard();
  };

  if (loading) return <LoadingState message="Loading caretaker live feed..." />;
  if (error) return <ErrorState message={error} onRetry={loadDashboard} />;

  // Filter for low stock medicines
  const lowStockMeds = medications.filter(
    (m) => Math.floor(m.stockCount / (m.doseQuantity || 1)) <= m.refillThresholdDays,
  );

  return (
    <div className="flex flex-col gap-6 pb-12 min-w-0">
      {/* Top Banner & Status */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EBE4DB] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-[#2D2318]">Caretaker Dashboard</h1>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-[#FAF8F5] text-[#8B7560] border border-[#D6CCC0]">
              Demo Data
            </span>
          </div>
          <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5 font-medium">
            Active Care Recipient: <strong>Savitri Devi</strong> (74 yrs · Asia/Kolkata)
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <ConnectionStatus status={sseStatus} onReconnect={reconnect} />
          <Link href="/care/medications/new">
            <Button variant="primary" size="sm" className="flex items-center gap-1 text-xs font-bold py-1.5 px-3 min-h-[36px]">
              <Plus className="w-3.5 h-3.5" />
              <span>Add Medication</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Stock Refill Warnings Banner */}
      {lowStockMeds.length > 0 && (
        <section aria-label="Refill Warnings" className="flex flex-col gap-2">
          {lowStockMeds.map((med) => (
            <StockWarning key={med.id} medication={med} />
          ))}
        </section>
      )}

      {/* Main Grid: Left Timeline (7 cols), Right Summary & Flags (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Live Dose Timeline */}
        <section className="lg:col-span-7 flex flex-col gap-3 min-w-0" aria-label="Today's Dose Timeline">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-[#2D2318]">Today&apos;s Live Dose Timeline</h2>
            <span className="text-[11px] font-semibold text-[#8B7560]">
              SSE Sync: Active
            </span>
          </div>

          <DoseTimeline doses={doses} onMarkTaken={handleMarkTaken} />
        </section>

        {/* Right Column: Adherence Snapshot, Risk Flags, Upcoming Appointments */}
        <div className="lg:col-span-5 flex flex-col gap-4 min-w-0">
          {/* Adherence & Streak Snapshot */}
          <div className="p-4 bg-white border border-[#EBE4DB] rounded-xl shadow-2xs flex flex-col gap-2 min-w-0">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-[#8B7560] uppercase tracking-wider">Adherence Streak</h3>
              <Flame className="w-4 h-4 text-[#C97B4B]" aria-hidden />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-[#2D2318]">{streak?.currentStreak || 4}</span>
              <span className="text-xs font-semibold text-[#1B5E20]">Days Consecutive</span>
            </div>
            <p className="text-xs text-[#5C4A38]">
              Best record: {streak?.bestStreak || 18} days. Consistent morning routine.
            </p>
            <div className="pt-2 border-t border-[#F2EDE6] mt-1">
              <Link
                href="/care/adherence"
                className="text-xs font-bold text-[#A5622D] hover:underline flex items-center justify-between"
              >
                <span>View full adherence logs</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Risk Flags R1-R6 */}
          <section aria-label="Digital Twin Risk Flags" className="flex flex-col gap-2.5 min-w-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4 text-[#C97B4B]" aria-hidden />
                <h3 className="text-sm font-bold text-[#2D2318]">Twin Risk Flags</h3>
              </div>
              <Link href="/care/twin" className="text-xs font-bold text-[#A5622D] hover:underline flex items-center gap-0.5">
                <span>Twin Guardian</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {flags.map((flag) => (
              <FlagCard key={flag.id} flag={flag} onAcknowledge={handleAcknowledgeFlag} />
            ))}
          </section>

          {/* Upcoming Appointments */}
          <section aria-label="Upcoming Doctor Appointments" className="p-4 bg-white border border-[#EBE4DB] rounded-xl shadow-2xs flex flex-col gap-3 min-w-0">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-[#2D2318] flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-[#C97B4B]" aria-hidden />
                <span>Upcoming Appointments</span>
              </h3>
              <Link href="/care/appointments" className="text-xs font-bold text-[#A5622D] hover:underline flex items-center gap-0.5">
                <span>View All</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="divide-y divide-[#F2EDE6]">
              {appointments.slice(0, 2).map((appt) => (
                <div key={appt.id} className="py-2 first:pt-0 last:pb-0 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold text-xs sm:text-sm text-[#2D2318] truncate">{appt.doctorName}</span>
                    <span className="text-[11px] font-semibold text-[#8B7560] shrink-0">{appt.scheduledAt}</span>
                  </div>
                  <p className="text-xs text-[#5C4A38] mt-0.5 truncate">{appt.specialty} · {appt.location}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
