'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api/client';
import { Medication } from '@/lib/api/types';
import { MedicineCard } from '@/components/elder/MedicineCard';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { ArrowLeft } from 'lucide-react';

export default function ElderMedicineDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const [medication, setMedication] = useState<Medication | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMed = async () => {
      try {
        setLoading(true);
        const meds = await api.getMedications();
        const found = meds.find((m) => m.id === id) || meds[0];
        setMedication(found);
      } catch {
        setError('Could not load medicine details.');
      } finally {
        setLoading(false);
      }
    };
    fetchMed();
  }, [id]);

  if (loading) return <LoadingState message="Loading medicine card..." />;
  if (error || !medication) return <ErrorState message={error || 'Medicine not found'} />;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <Link
          href="/elder"
          aria-label="Back to main screen"
          className="p-3 bg-white border-2 border-[#D6CCC0] rounded-2xl text-[#1A150E] focus:outline-none focus:ring-4 focus:ring-[#C97B4B]"
        >
          <ArrowLeft className="w-8 h-8" aria-hidden />
        </Link>
        <div>
          <span className="text-xl font-bold text-[#A5622D] uppercase tracking-wider">
            Plain Language Card
          </span>
          <h1 className="text-4xl font-black text-[#1A150E]">{medication.name}</h1>
        </div>
      </div>

      <MedicineCard medication={medication} />
    </div>
  );
}

