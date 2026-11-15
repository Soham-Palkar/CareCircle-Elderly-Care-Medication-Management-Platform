'use client';

import React, { useState } from 'react';
import { Member } from '@/lib/api/types';
import { ShieldCheck, UserX, AlertTriangle } from 'lucide-react';
import { Switch } from '../ui/Switch';
import { Dialog } from '../ui/Dialog';
import { Button } from '../ui/Button';

export function PermissionCard({
  member,
  onUpdatePermissions,
  onDeactivate,
}: {
  member: Member;
  onUpdatePermissions: (memberId: string, perms: any) => Promise<void>;
  onDeactivate: (memberId: string) => Promise<void>;
}) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const perms = member.permissions || {
    canViewMeds: true,
    canEditMeds: false,
    canMarkDoses: false,
    canViewAppointments: true,
    canEditAppointments: false,
    canViewHealth: true,
    receivesAlerts: true,
    alertLevelMin: 1,
  };

  const handleToggle = async (key: string, value: boolean) => {
    await onUpdatePermissions(member.id, { [key]: value });
  };

  const handleDeactivateConfirm = async () => {
    setLoading(true);
    try {
      await onDeactivate(member.id);
      setConfirmOpen(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border-2 border-[#C4B29F] rounded-3xl p-8 shadow-md flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#EBE4DB] pb-4">
        <div>
          <h3 className="text-3xl font-extrabold text-[#1A150E]">{member.displayName}</h3>
          <span className="text-xl font-bold text-[#A5622D] uppercase tracking-wider block mt-1">
            Role: {member.role}
          </span>
        </div>
        <div className="flex items-center gap-2 text-xl font-semibold text-[#1B5E20] bg-[#EEF5EE] px-4 py-2 rounded-2xl border border-[#81C784]">
          <ShieldCheck className="w-6 h-6" aria-hidden />
          <span>Active Access</span>
        </div>
      </div>

      <div className="flex flex-col gap-6">
        <h4 className="text-2xl font-bold text-[#1A150E]">Permissions you have granted:</h4>

        <div className="bg-[#FAF8F5] p-6 rounded-2xl border border-[#EBE4DB] flex flex-col gap-6">
          <Switch
            label="Can view my medicines"
            description="Allows them to see current medication names and doses"
            checked={perms.canViewMeds}
            onChange={(val) => handleToggle('canViewMeds', val)}
          />
          <Switch
            label="Can add or change medicine schedule"
            description="Allows editing medication schedule with doctor check confirmation"
            checked={perms.canEditMeds}
            onChange={(val) => handleToggle('canEditMeds', val)}
          />
          <Switch
            label="Can mark medicine taken on my behalf"
            description="Logs an entry when they help you take your dose"
            checked={perms.canMarkDoses}
            onChange={(val) => handleToggle('canMarkDoses', val)}
          />
          <Switch
            label="Can see doctor appointments"
            description="Allows viewing and helping organize medical visits"
            checked={perms.canViewAppointments}
            onChange={(val) => handleToggle('canViewAppointments', val)}
          />
        </div>
      </div>

      {member.role !== 'elder' && (
        <div className="border-t border-[#EBE4DB] pt-6 flex justify-end">
          <Button
            variant="destructive"
            size="lg"
            onClick={() => setConfirmOpen(true)}
            className="flex items-center gap-2 text-xl font-bold min-h-[56px] px-6"
          >
            <UserX className="w-6 h-6" aria-hidden />
            <span>Remove From Circle</span>
          </Button>
        </div>
      )}

      {/* Confirmation Dialog with ample spacing */}
      <Dialog
        open={confirmOpen}
        onClose={() => setConfirmOpen(false)}
        title="Remove Member Access?"
        description={`Are you sure you want to remove ${member.displayName} from your Care Circle? They will no longer be able to view your medicines or appointments.`}
      >
        <div className="flex flex-col gap-6 mt-4">
          <div className="p-4 bg-[#FFF3E0] rounded-2xl border border-[#FFB74D] flex items-center gap-3">
            <AlertTriangle className="w-8 h-8 text-[#8C4E00] shrink-0" aria-hidden />
            <p className="text-lg text-[#8C4E00] font-medium">
              You can invite them again in the future if you choose.
            </p>
          </div>
          <div className="flex flex-col-reverse sm:flex-row items-center justify-end gap-4">
            <Button variant="secondary" size="lg" onClick={() => setConfirmOpen(false)} className="w-full sm:w-auto">
              Keep Access
            </Button>
            <Button
              variant="destructive"
              size="lg"
              loading={loading}
              onClick={handleDeactivateConfirm}
              className="w-full sm:w-auto"
            >
              Confirm Removal
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
}

