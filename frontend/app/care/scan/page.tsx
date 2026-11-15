'use client';

import React from 'react';
import { ScanReview } from '@/components/care/ScanReview';
import { mockScanDraft } from '@/lib/api/mockData';
import { api } from '@/lib/api/client';
import { Camera } from 'lucide-react';

export default function CareScanPage() {
  const handleConfirmSchedule = async (medData: any) => {
    await api.createMedication(medData);
  };

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6 pb-16">
      <div className="border-b border-[#EBE4DB] pb-4">
        <div className="flex items-center gap-1.5 text-[#C97B4B] mb-0.5">
          <Camera className="w-4 h-4" />
          <span className="text-xs font-bold uppercase tracking-wider">Vision Tool</span>
        </div>
        <h1 className="text-2xl font-bold text-[#2D2318]">Prescription & Packaging Scan</h1>
        <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
          Extract medicine name, strength, and schedule from packaging photos into human-verified drafts.
        </p>
      </div>

      <ScanReview draft={mockScanDraft} onConfirmSchedule={handleConfirmSchedule} />
    </div>
  );
}

