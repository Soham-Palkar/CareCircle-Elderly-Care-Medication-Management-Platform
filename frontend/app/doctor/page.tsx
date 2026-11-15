'use client';

import React from 'react';
import Link from 'next/link';
import { Stethoscope, FileText, ArrowLeft, ShieldAlert } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function DoctorRoadmapPage() {
  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 flex flex-col gap-6 pb-16">
      <div className="flex items-center gap-3 border-b border-[#EBE4DB] pb-4">
        <Link
          href="/care"
          className="p-2 bg-white border border-[#D6CCC0] rounded-lg text-[#2D2318] hover:bg-[#F2EDE6] transition-colors"
          aria-label="Back to Caretaker Dashboard"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-[#FFF3E0] text-[#8C4E00] border border-[#FFB74D]">
              Roadmap Preview · Read-Only
            </span>
          </div>
          <h1 className="text-2xl font-bold text-[#2D2318] mt-1">
            Doctor Consultation View (Phase 2 Preview)
          </h1>
          <p className="text-xs sm:text-sm text-[#5C4A38]">
            Planned read-only pre-appointment summary for routine checkups
          </p>
        </div>
      </div>

      <div className="bg-white border border-[#EBE4DB] rounded-xl p-6 shadow-2xs flex flex-col gap-5">
        <div className="p-4 bg-[#FAF8F5] border border-[#EBE4DB] rounded-lg flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-[#8B7560] shrink-0 mt-0.5" />
          <div className="text-xs text-[#5C4A38] leading-relaxed">
            <strong className="text-[#2D2318] block mb-0.5">Safety & Platform Scope Notice:</strong>
            CareCircle is a medication coordination and reminder platform, not a medical device or electronic health record (EHR) system. The Doctor view is designed exclusively as a <strong>read-only longitudinal adherence report</strong> that an elder or caretaker can bring or grant access to during regular consultations. All care adjustments require direct medical evaluation and explicit elder consent.
          </div>
        </div>

        <h2 className="text-base font-bold text-[#2D2318]">Planned Read-Only Capabilities</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 bg-[#FAF8F5] rounded-lg border border-[#EBE4DB] flex flex-col gap-2">
            <div className="flex items-center gap-2 text-[#A5622D] font-bold text-sm">
              <FileText className="w-4 h-4" />
              <span>30-Day Adherence Log Export</span>
            </div>
            <p className="text-xs text-[#5C4A38] leading-relaxed">
              Export recorded dose timings, missed dose frequencies, and routine anchor consistency for review during scheduled visits.
            </p>
          </div>

          <div className="p-4 bg-[#FAF8F5] rounded-lg border border-[#EBE4DB] flex flex-col gap-2">
            <div className="flex items-center gap-2 text-[#5C8C5A] font-bold text-sm">
              <Stethoscope className="w-4 h-4" />
              <span>Consultation Preparation Note</span>
            </div>
            <p className="text-xs text-[#5C4A38] leading-relaxed">
              Provide a concise list of current active medications, confirmed strengths, and elder-reported questions for upcoming appointments.
            </p>
          </div>
        </div>

        <div className="border-t border-[#EBE4DB] pt-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 text-xs text-[#8B7560]">
          <span>Status: Phase 2 Roadmap · Read-only consultation preview</span>
          <Link href="/care">
            <Button variant="secondary" size="sm" className="text-xs font-semibold">
              Return to Caretaker Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
