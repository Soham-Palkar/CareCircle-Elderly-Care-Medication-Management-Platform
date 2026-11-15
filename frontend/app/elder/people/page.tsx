'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api/client';
import { Member, AuditLogItem } from '@/lib/api/types';
import { PermissionCard } from '@/components/elder/PermissionCard';
import { LoadingState, ErrorState } from '@/components/common/FeedbackStates';
import { ArrowLeft, Shield, History, CheckCircle2 } from 'lucide-react';
import { Tabs } from '@/components/ui/Tabs';

export default function ElderPeoplePage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [activeTab, setActiveTab] = useState<'members' | 'audit'>('members');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [m, a] = await Promise.all([api.getMembers(), api.getAuditLog()]);
      setMembers(m.filter((mem) => mem.isActive));
      setAuditLogs(a);
    } catch {
      setError('Could not load member permissions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpdatePermissions = async (memberId: string, perms: any) => {
    await api.updateMemberPermissions(memberId, perms);
    await loadData();
  };

  const handleDeactivate = async (memberId: string) => {
    await api.deactivateMember(memberId);
    await loadData();
  };

  if (loading) return <LoadingState message="Loading care circle members..." />;
  if (error) return <ErrorState message={error} onRetry={loadData} />;

  return (
    <div className="flex flex-col gap-8 pb-12">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/elder"
          aria-label="Back to main screen"
          className="p-3 bg-white border-2 border-[#D6CCC0] rounded-2xl text-[#1A150E] focus:outline-none focus:ring-4 focus:ring-[#C97B4B]"
        >
          <ArrowLeft className="w-8 h-8" aria-hidden />
        </Link>
        <div>
          <h1 className="text-4xl font-black text-[#1A150E]">Who Has Access</h1>
          <p className="text-2xl text-[#5C4A38] font-medium">You control who sees your health details</p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs
        activeTab={activeTab}
        onChange={(t) => setActiveTab(t as any)}
        tabs={[
          { id: 'members', label: 'Circle Members', icon: <Shield className="w-5 h-5" /> },
          { id: 'audit', label: 'Audit History', icon: <History className="w-5 h-5" /> },
        ]}
      />

      {activeTab === 'members' ? (
        <section className="flex flex-col gap-8" aria-label="Members List">
          <div className="p-6 bg-[#EEF5EE] border-2 border-[#81C784] rounded-3xl flex items-start gap-4">
            <CheckCircle2 className="w-8 h-8 text-[#1B5E20] shrink-0 mt-1" aria-hidden />
            <div>
              <h2 className="text-2xl font-bold text-[#1B5E20]">You have the final say</h2>
              <p className="text-xl text-[#2D2318] font-medium mt-1">
                Your family and caretaker can assist you, but you can turn on or off any person&apos;s permission at any time.
              </p>
            </div>
          </div>

          <div className="flex flex-col gap-6">
            {members.map((member) => (
              <PermissionCard
                key={member.id}
                member={member}
                onUpdatePermissions={handleUpdatePermissions}
                onDeactivate={handleDeactivate}
              />
            ))}
          </div>
        </section>
      ) : (
        <section className="bg-white border-2 border-[#C4B29F] rounded-3xl p-8 shadow-sm flex flex-col gap-6">
          <div>
            <h2 className="text-3xl font-extrabold text-[#1A150E]">Care Activity & Changes Log</h2>
            <p className="text-xl text-[#5C4A38] font-medium mt-1">
              A clear, read-only record of every dose taken or setting adjusted.
            </p>
          </div>

          <div className="divide-y divide-[#EBE4DB]">
            {auditLogs.map((log) => (
              <div key={log.id} className="py-4 flex flex-col gap-1">
                <div className="flex items-center justify-between text-xl font-bold text-[#1A150E]">
                  <span>{log.actorName}</span>
                  <span className="text-base text-[#8B7560] font-normal">{log.createdAt.slice(0, 10)}</span>
                </div>
                <p className="text-lg text-[#5C4A38] font-medium">
                  Action: <strong className="text-[#A5622D]">{log.action.replace('_', ' ')}</strong> on {log.entityType}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

