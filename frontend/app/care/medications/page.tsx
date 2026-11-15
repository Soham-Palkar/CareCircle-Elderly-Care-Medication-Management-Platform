'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api/client';
import { Medication } from '@/lib/api/types';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { Plus, Pill, AlertTriangle, ArrowRight, ShieldCheck, Archive } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function CareMedicationsListPage() {
  const [meds, setMeds] = useState<Medication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadMeds = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getMedications();
      setMeds(data);
    } catch {
      setError('Could not load medications list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMeds();
  }, []);

  if (loading) return <LoadingState message="Loading medications..." />;
  if (error) return <ErrorState message={error} onRetry={loadMeds} />;

  return (
    <div className="flex flex-col gap-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EBE4DB] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-[#2D2318]">Medication Management</h1>
          <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
            Active and archived schedules for Savitri Devi
          </p>
        </div>
        <Link href="/care/medications/new">
          <Button variant="primary" size="sm" className="flex items-center gap-1.5 font-bold">
            <Plus className="w-4 h-4" />
            <span>Add New Medication</span>
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {meds.map((med) => {
          const daysLeft = Math.floor(med.stockCount / (med.doseQuantity || 1));
          const isLow = daysLeft <= med.refillThresholdDays;

          return (
            <div
              key={med.id}
              className="bg-white border border-[#EBE4DB] rounded-xl p-5 shadow-2xs flex flex-col justify-between gap-3.5"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <Pill className="w-5 h-5 text-[#C97B4B]" aria-hidden />
                    <h3 className="text-lg font-bold text-[#2D2318]">{med.name}</h3>
                  </div>
                  <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#FAF8F5] border border-[#D6CCC0] text-[#5C4A38]">
                    {med.form} · {med.strength}
                  </span>
                </div>

                <p className="text-xs sm:text-sm text-[#5C4A38] font-medium mb-2.5">
                  {med.instructions}
                </p>

                {med.purposeCard?.purpose && (
                  <p className="text-xs text-[#8B7560] bg-[#FAF8F5] p-2.5 rounded-lg border border-[#EBE4DB]">
                    <strong>Purpose:</strong> {med.purposeCard.purpose}
                  </p>
                )}

                <div className="flex items-center gap-4 mt-4 text-xs font-semibold text-[#5C4A38]">
                  <span>Stock: {med.stockCount} units</span>
                  <span>Daily: {med.doseQuantity} dose/day</span>
                  {isLow && (
                    <span className="inline-flex items-center gap-1 text-[#8C4E00] font-bold">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      Refill soon ({daysLeft}d)
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between border-t border-[#F2EDE6] pt-4">
                <span className="text-xs font-semibold text-[#1B5E20] flex items-center gap-1">
                  <ShieldCheck className="w-4 h-4" />
                  Doctor verified
                </span>
                <Link
                  href={`/care/medications/${med.id}`}
                  className="inline-flex items-center gap-1.5 text-sm font-bold text-[#A5622D] hover:underline"
                >
                  <span>Schedule details</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

