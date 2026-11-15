'use client';

import React, { useState } from 'react';
import { ScheduleProposal } from '@/lib/api/types';
import { Sparkles, ArrowRight, CheckCircle2, XCircle, ShieldCheck } from 'lucide-react';
import { Button } from '../ui/Button';
import { Dialog } from '../ui/Dialog';

export function ProposalCard({
  proposal,
  onDecide,
}: {
  proposal: ScheduleProposal;
  onDecide?: (id: string, decision: 'approved' | 'rejected', elderConsent: boolean) => Promise<void>;
}) {
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  const [elderConsentChecked, setElderConsentChecked] = useState(false);
  const [doctorChecked, setDoctorChecked] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleApprove = async () => {
    if (!elderConsentChecked || !doctorChecked) return;
    setLoading(true);
    try {
      await onDecide?.(proposal.id, 'approved', true);
      setConfirmModalOpen(false);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    try {
      await onDecide?.(proposal.id, 'rejected', false);
    } finally {
      setLoading(false);
    }
  };

  const isPending = proposal.status === 'pending';

  return (
    <div className="bg-white border border-[#EBE4DB] rounded-xl p-5 shadow-2xs flex flex-col gap-3.5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#EBE4DB] pb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <Sparkles className="w-4 h-4 text-[#C97B4B]" aria-hidden />
          <h4 className="text-base font-bold text-[#2D2318]">{proposal.medicationName}</h4>
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#FAF8F5] border border-[#D6CCC0] text-[#5C4A38]">
            Proposed by: {proposal.proposedByName || 'System Guardian'}
          </span>
        </div>

        <span
          className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
            proposal.status === 'approved'
              ? 'bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784]'
              : proposal.status === 'rejected'
              ? 'bg-[#FAEAEA] text-[#B71C1C] border border-[#E57373]'
              : 'bg-[#FFF3E0] text-[#8C4E00] border border-[#FFB74D]'
          }`}
        >
          Status: {proposal.status}
        </span>
      </div>

      {/* Schedule Diff Preview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 bg-[#FAF8F5] rounded-lg border border-[#EBE4DB]">
        <div>
          <span className="text-[11px] font-bold text-[#8B7560] uppercase block mb-0.5">
            Current Schedule (To be archived):
          </span>
          <p className="text-xs sm:text-sm font-semibold text-[#5C4A38] line-through">
            {proposal.change.oldSchedule}
          </p>
        </div>
        <div>
          <span className="text-[11px] font-bold text-[#1B5E20] uppercase block mb-0.5 flex items-center gap-1">
            <ArrowRight className="w-3 h-3" aria-hidden />
            <span>Proposed Change:</span>
          </span>
          <p className="text-xs sm:text-sm font-bold text-[#1A150E]">
            {proposal.change.newSchedule}
          </p>
        </div>
      </div>

      {/* Rationale */}
      <p className="text-sm text-[#5C4A38] leading-relaxed">
        <strong>Rationale:</strong> {proposal.rationale}
      </p>

      {/* Elder Consent Notice */}
      <div className="p-3 bg-[#EEF5EE] border border-[#81C784] rounded-xl flex items-center gap-2 text-xs font-semibold text-[#1B5E20]">
        <ShieldCheck className="w-4 h-4 shrink-0" aria-hidden />
        <span>Elder Safeguard: Requires explicit consent from Savitri Devi before applying.</span>
      </div>

      {/* Actions */}
      {isPending && onDecide && (
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={handleReject}
            disabled={loading}
            className="text-xs font-bold text-[#B54040] hover:bg-[#FAEAEA]"
          >
            <XCircle className="w-4 h-4 mr-1.5" />
            <span>Reject Proposal</span>
          </Button>

          <Button
            size="sm"
            variant="primary"
            onClick={() => setConfirmModalOpen(true)}
            className="text-xs font-bold"
          >
            <CheckCircle2 className="w-4 h-4 mr-1.5" />
            <span>Review & Approve</span>
          </Button>
        </div>
      )}

      {/* Approval Confirmation Dialog */}
      <Dialog
        open={confirmModalOpen}
        onClose={() => setConfirmModalOpen(false)}
        title="Approve Schedule Proposal"
        description="Applying this proposal will archive the previous schedule version and update Savitri Devi's daily reminders."
      >
        <div className="flex flex-col gap-5 mt-4">
          <label className="flex items-start gap-3 p-3 bg-[#FAF8F5] rounded-xl border border-[#D6CCC0] cursor-pointer">
            <input
              type="checkbox"
              checked={elderConsentChecked}
              onChange={(e) => setElderConsentChecked(e.target.checked)}
              className="mt-1 w-5 h-5 accent-[#C97B4B] rounded"
            />
            <span className="text-sm text-[#2D2318] font-semibold leading-snug">
              I confirm that Savitri Devi (Elder) has reviewed and agreed to this schedule modification.
            </span>
          </label>

          <label className="flex items-start gap-3 p-3 bg-[#FAF8F5] rounded-xl border border-[#D6CCC0] cursor-pointer">
            <input
              type="checkbox"
              checked={doctorChecked}
              onChange={(e) => setDoctorChecked(e.target.checked)}
              className="mt-1 w-5 h-5 accent-[#C97B4B] rounded"
            />
            <span className="text-sm text-[#2D2318] font-semibold leading-snug">
              I confirm this timing change does not contradict treating doctor instructions.
            </span>
          </label>

          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setConfirmModalOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              disabled={!elderConsentChecked || !doctorChecked}
              loading={loading}
              onClick={handleApprove}
            >
              Activate New Schedule
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
}

