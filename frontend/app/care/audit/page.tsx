'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api/client';
import { AuditLogItem } from '@/lib/api/types';
import { LoadingState } from '@/components/common/FeedbackStates';
import { ShieldCheck, History, Filter } from 'lucide-react';

export default function CareAuditPage() {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterAction, setFilterAction] = useState<string>('all');

  useEffect(() => {
    api.getAuditLog().then((data) => {
      setLogs(data);
      setLoading(false);
    });
  }, []);

  const filteredLogs = filterAction === 'all' ? logs : logs.filter((l) => l.action === filterAction);

  if (loading) return <LoadingState message="Loading security audit log..." />;

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 pb-16">
      <div className="border-b border-[#EBE4DB] pb-6">
        <div className="flex items-center gap-2 text-[#C97B4B] mb-1">
          <ShieldCheck className="w-6 h-6" />
          <span className="text-xs font-bold uppercase tracking-wider">Tamper-Proof Audit</span>
        </div>
        <h1 className="text-3xl font-black text-[#2D2318]">CareCircle Audit History</h1>
        <p className="text-base text-[#5C4A38] mt-1">
          Append-only, immutable record of every medication change, dose event, and permission modification.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center justify-between gap-4 bg-white p-3.5 rounded-lg border border-[#EBE4DB]">
        <div className="flex items-center gap-2 text-xs font-semibold text-[#5C4A38]">
          <Filter className="w-3.5 h-3.5" />
          <span>Filter Action:</span>
        </div>
        <select
          value={filterAction}
          onChange={(e) => setFilterAction(e.target.value)}
          className="px-2.5 py-1 rounded-md border border-[#D6CCC0] bg-[#FAF8F5] text-xs text-[#2D2318] focus:outline-none"
        >
          <option value="all">All Audit Actions</option>
          <option value="DOSE_TAKEN">DOSE_TAKEN</option>
          <option value="MEDICATION_CONFIRMED">MEDICATION_CONFIRMED</option>
          <option value="PERMISSION_UPDATED">PERMISSION_UPDATED</option>
          <option value="MEMBER_DEACTIVATED">MEMBER_DEACTIVATED</option>
        </select>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white border border-[#EBE4DB] rounded-xl p-5 shadow-2xs overflow-x-auto">
        <table className="w-full text-left text-sm text-[#5C4A38]">
          <caption className="sr-only">Audit log of system actions</caption>
          <thead>
            <tr className="border-b border-[#EBE4DB] text-[#2D2318] font-bold">
              <th scope="col" className="pb-3">Timestamp (UTC)</th>
              <th scope="col" className="pb-3">Actor & Role</th>
              <th scope="col" className="pb-3">Action</th>
              <th scope="col" className="pb-3">Entity Type</th>
              <th scope="col" className="pb-3">Details / Outcome</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F2EDE6]">
            {filteredLogs.map((log) => (
              <tr key={log.id} className="py-3">
                <td className="py-3 text-xs font-mono text-[#8B7560]">
                  {log.createdAt.replace('T', ' ').slice(0, 19)}
                </td>
                <td className="py-3 font-semibold text-[#2D2318]">
                  {log.actorName}
                  <span className="block text-xs font-normal text-[#8B7560]">({log.actorRole})</span>
                </td>
                <td className="py-3 font-bold text-[#A5622D]">
                  {log.action}
                </td>
                <td className="py-3 text-xs font-medium">
                  {log.entityType}
                </td>
                <td className="py-3 text-xs text-[#5C4A38]">
                  {log.after ? JSON.stringify(log.after) : 'Recorded successfully'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

