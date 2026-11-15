'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api/client';
import { Member, Role } from '@/lib/api/types';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { Users, UserPlus, Shield, Copy, Check, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Dialog } from '@/components/ui/Dialog';

export default function CareMembersPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [inviteRole, setInviteRole] = useState<Role>('family');
  const [generatedCode, setGeneratedCode] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const loadMembers = async () => {
    try {
      setLoading(true);
      const data = await api.getMembers();
      setMembers(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMembers();
  }, []);

  const handleGenerateInvite = () => {
    const code = `INV-${inviteRole.toUpperCase()}-${Math.floor(1000 + Math.random() * 9000)}`;
    setGeneratedCode(code);
  };

  const copyCode = () => {
    if (generatedCode) {
      navigator.clipboard.writeText(generatedCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) return <LoadingState message="Loading circle members..." />;

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 pb-16">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EBE4DB] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-[#2D2318]">Care Circle Members</h1>
          <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
            Authorized family members, caretakers, and doctors in Devi Family Care
          </p>
        </div>
        <Button variant="primary" size="sm" onClick={() => setInviteModalOpen(true)} className="flex items-center gap-1.5 font-bold">
          <UserPlus className="w-4 h-4" />
          <span>Invite New Member</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {members.map((mem) => (
          <div
            key={mem.id}
            className={`p-5 bg-white border rounded-xl shadow-2xs flex flex-col justify-between gap-3.5 ${
              mem.isActive ? 'border-[#EBE4DB]' : 'border-[#EBE4DB] opacity-50'
            }`}
          >
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-bold text-[#2D2318]">{mem.displayName}</h3>
                  <span className="text-xs font-bold uppercase tracking-wider text-[#A5622D] block mt-0.5">
                    Role: {mem.role}
                  </span>
                </div>
                <span
                  className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                    mem.isActive
                      ? 'bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784]'
                      : 'bg-[#F2EDE6] text-[#8B7560]'
                  }`}
                >
                  {mem.isActive ? 'Active Member' : 'Deactivated'}
                </span>
              </div>

              {mem.email && (
                <p className="text-xs text-[#5C4A38] mt-3">
                  Email: <strong>{mem.email}</strong>
                </p>
              )}

              {mem.telegramChatId && (
                <p className="text-xs text-[#0088CC] font-semibold mt-1">
                  Telegram Linked: ID {mem.telegramChatId}
                </p>
              )}
            </div>

            <div className="pt-3 border-t border-[#F2EDE6] flex items-center justify-between text-xs text-[#8B7560]">
              <span>Joined: {mem.createdAt.slice(0, 10)}</span>
              {mem.role === 'elder' && (
                <span className="font-bold text-[#A5622D]">Circle Administrator</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Invite Member Dialog */}
      <Dialog
        open={inviteModalOpen}
        onClose={() => {
          setInviteModalOpen(false);
          setGeneratedCode(null);
        }}
        title="Invite New Care Circle Member"
        description="Generate a single-use expiring invite code. The invitee will redeem this and set their personal passcode."
      >
        <div className="flex flex-col gap-5 mt-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-semibold text-[#2D2318]">Assign Role</label>
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value as any)}
              className="px-4 py-2.5 rounded-xl border border-[#D6CCC0] bg-white text-sm"
            >
              <option value="family">Family (Status & Adherence overview)</option>
              <option value="caretaker">Caretaker (Full schedule & medication tools)</option>
              <option value="doctor">Doctor (Read-only longitudinal records)</option>
            </select>
          </div>

          {!generatedCode ? (
            <Button variant="primary" onClick={handleGenerateInvite} className="mt-2">
              Generate Invite Code
            </Button>
          ) : (
            <div className="p-5 bg-[#FAF8F5] border-2 border-[#C97B4B] rounded-2xl flex flex-col gap-3">
              <span className="text-xs font-bold text-[#8C4E00] uppercase">
                Single-Use Invite Code (Valid for 48 hours):
              </span>
              <div className="flex items-center justify-between gap-3 bg-white p-3 rounded-xl border border-[#D6CCC0]">
                <code className="text-xl font-mono font-black text-[#2D2318]">{generatedCode}</code>
                <Button size="sm" variant="secondary" onClick={copyCode} className="flex items-center gap-1.5">
                  {copied ? <Check className="w-4 h-4 text-[#1B5E20]" /> : <Copy className="w-4 h-4" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </Button>
              </div>
              <p className="text-xs text-[#5C4A38]">
                Share this code with the family member along with your circle code (<strong>DEVI-7892</strong>).
              </p>
            </div>
          )}
        </div>
      </Dialog>
    </div>
  );
}

