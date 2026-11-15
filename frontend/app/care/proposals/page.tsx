'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api/client';
import { ScheduleProposal } from '@/lib/api/types';
import { ProposalCard } from '@/components/care/ProposalCard';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { Sparkles, ShieldCheck } from 'lucide-react';

export default function CareProposalsPage() {
  const [proposals, setProposals] = useState<ScheduleProposal[]>([]);
  const [loading, setLoading] = useState(true);

  const loadProposals = async () => {
    try {
      setLoading(true);
      const data = await api.getProposals();
      setProposals(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProposals();
  }, []);

  const handleDecide = async (id: string, decision: 'approved' | 'rejected', elderConsent: boolean) => {
    await api.decideProposal(id, decision, elderConsent);
    await loadProposals();
  };

  if (loading) return <LoadingState message="Loading schedule proposals..." />;

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 pb-16">
      <div className="border-b border-[#EBE4DB] pb-4">
        <div className="flex items-center gap-1.5 text-[#C97B4B] mb-0.5">
          <Sparkles className="w-4 h-4" />
          <span className="text-xs font-bold uppercase tracking-wider">Guardian Planning</span>
        </div>
        <h1 className="text-2xl font-bold text-[#2D2318]">What-If Schedule Proposals</h1>
        <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
          Review potential timing changes suggested by adherence pattern analysis.
        </p>
      </div>

      <div className="p-3.5 bg-[#EEF5EE] border border-[#81C784] rounded-lg flex items-start gap-2.5 text-xs text-[#1B5E20]">
        <ShieldCheck className="w-4 h-4 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold block text-sm">Safety Rule: Elder Authority</span>
          <span>
            No schedule change is ever auto-applied. Both caretaker review and Savitri Devi&apos;s explicit consent are required.
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-6">
        {proposals.map((prop) => (
          <ProposalCard key={prop.id} proposal={prop} onDecide={handleDecide} />
        ))}
      </div>
    </div>
  );
}

