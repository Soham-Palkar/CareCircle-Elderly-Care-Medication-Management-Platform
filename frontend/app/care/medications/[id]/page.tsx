'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { Medication } from '@/lib/api/types';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { ArrowLeft, Clock, History, AlertTriangle, ShieldCheck, Archive } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Dialog } from '@/components/ui/Dialog';

export default function CareMedicationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;
  const [med, setMed] = useState<Medication | null>(null);
  const [loading, setLoading] = useState(true);
  const [archiveModalOpen, setArchiveModalOpen] = useState(false);

  useEffect(() => {
    api.getMedicationById(id).then((res) => {
      setMed(res);
      setLoading(false);
    });
  }, [id]);

  const handleArchive = async () => {
    if (!med) return;
    await api.archiveMedication(med.id);
    router.push('/care/medications');
  };

  if (loading) return <LoadingState message="Loading medication schedule..." />;
  if (!med) return <ErrorState message="Medication not found." />;

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 pb-16">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/care/medications"
            className="p-2.5 bg-white border border-[#D6CCC0] rounded-xl text-[#2D2318] hover:bg-[#F2EDE6]"
          >
            <ArrowLeft className="w-6 h-6" />
          </Link>
          <div>
            <h1 className="text-3xl font-black text-[#2D2318]">{med.name}</h1>
            <span className="text-sm font-semibold text-[#8B7560]">
              {med.form} · {med.strength} · Criticality: {med.criticality}
            </span>
          </div>
        </div>

        <Button
          variant="destructive"
          size="sm"
          onClick={() => setArchiveModalOpen(true)}
          className="flex items-center gap-1.5 text-xs font-bold"
        >
          <Archive className="w-4 h-4" />
          <span>Archive Schedule</span>
        </Button>
      </div>

      {/* Active Version Card */}
      <div className="bg-white border-2 border-[#EBE4DB] rounded-3xl p-6 sm:p-8 shadow-sm flex flex-col gap-6">
        <div className="flex items-center justify-between border-b border-[#EBE4DB] pb-4">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#1B5E20]" />
            <h3 className="text-lg font-bold text-[#2D2318]">Current Active Schedule (v2.0)</h3>
          </div>
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784]">
            Active
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 bg-[#FAF8F5] rounded-2xl border border-[#D6CCC0]">
            <span className="text-xs font-bold text-[#8B7560] uppercase block mb-1">
              Instructions
            </span>
            <p className="text-base font-semibold text-[#2D2318]">{med.instructions}</p>
          </div>

          <div className="p-4 bg-[#FAF8F5] rounded-2xl border border-[#D6CCC0]">
            <span className="text-xs font-bold text-[#8B7560] uppercase block mb-1">
              Stock & Refills
            </span>
            <p className="text-base font-semibold text-[#2D2318]">
              {med.stockCount} units remaining (Refill threshold: {med.refillThresholdDays} days)
            </p>
          </div>
        </div>

        {/* Purpose Card */}
        {med.purposeCard && (
          <div className="bg-[#FAF8F5] p-5 rounded-2xl border border-[#D6CCC0] flex flex-col gap-2">
            <h4 className="text-sm font-bold uppercase text-[#A5622D]">
              Plain Language Explanation (Displayed to Elder)
            </h4>
            <p className="text-base text-[#2D2318] font-medium leading-relaxed">
              {med.purposeCard.purpose}
            </p>
            {med.purposeCard.cautions && (
              <p className="text-xs text-[#8C4E00] mt-1">
                <strong>Caution:</strong> {med.purposeCard.cautions}
              </p>
            )}
          </div>
        )}

        {/* Previous Schedule Version History */}
        <div className="border-t border-[#EBE4DB] pt-4">
          <h4 className="text-sm font-bold text-[#5C4A38] uppercase tracking-wider flex items-center gap-2 mb-3">
            <History className="w-4 h-4" />
            <span>Schedule Version History (Archived Versions)</span>
          </h4>
          <div className="p-4 bg-[#F2EDE6] rounded-xl border border-[#D6CCC0] text-sm text-[#5C4A38] flex justify-between items-center">
            <div>
              <span className="font-bold block text-[#2D2318]">v1.0 (Fixed 09:00 AM)</span>
              <span className="text-xs">Archived on Oct 10 when switched to routine breakfast anchor</span>
            </div>
            <span className="text-xs font-bold px-2 py-0.5 rounded bg-white text-[#8B7560]">
              Archived
            </span>
          </div>
        </div>
      </div>

      {/* Archive Modal */}
      <Dialog
        open={archiveModalOpen}
        onClose={() => setArchiveModalOpen(false)}
        title={`Archive ${med.name}?`}
        description="Archiving will remove this medicine from today's active dose generation. All historical dose logs and adherence records remain securely preserved in the audit history."
      >
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={() => setArchiveModalOpen(false)}>
            Keep Active
          </Button>
          <Button variant="destructive" onClick={handleArchive}>
            Confirm Archive
          </Button>
        </div>
      </Dialog>
    </div>
  );
}

