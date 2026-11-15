'use client';

import React from 'react';
import { RiskFlag } from '@/lib/api/types';
import { AlertTriangle, AlertCircle, Info, ChevronDown, Check } from 'lucide-react';
import { Button } from '../ui/Button';

export function FlagCard({
  flag,
  onAcknowledge,
}: {
  flag: RiskFlag;
  onAcknowledge?: (id: string) => void;
}) {
  const [expanded, setExpanded] = React.useState(false);

  const severityConfig = {
    info: {
      icon: <Info className="w-4 h-4 text-[#1E3A8A] shrink-0" aria-hidden />,
      badge: 'bg-[#F0F4F8] text-[#1E3A8A] border-[#BFDBFE]',
      card: 'border-[#BFDBFE] bg-[#F7F9FC]',
      label: 'Info',
    },
    warning: {
      icon: <AlertTriangle className="w-4 h-4 text-[#8C4E00] shrink-0" aria-hidden />,
      badge: 'bg-[#FFF3E0] text-[#8C4E00] border-[#FFB74D]',
      card: 'border-[#FFD59E] bg-[#FFFBF5]',
      label: 'Warning',
    },
    high: {
      icon: <AlertCircle className="w-4 h-4 text-[#B71C1C] shrink-0" aria-hidden />,
      badge: 'bg-[#FAEAEA] text-[#B71C1C] border-[#E57373]',
      card: 'border-[#E57373] bg-[#FCF5F5]',
      label: 'High Priority',
    },
  };

  const current = severityConfig[flag.severity] || severityConfig.info;

  return (
    <div
      role="article"
      aria-label={`Risk flag: ${flag.ruleCode} - ${flag.message}`}
      className={`p-4 rounded-xl border transition-all shadow-2xs flex flex-col gap-2.5 min-w-0 ${current.card}`}
    >
      {/* Header with rule and status */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-1.5 min-w-0">
          {current.icon}
          <span className="text-xs font-bold text-[#2D2318] truncate">
            {flag.ruleCode} · {flag.ruleName}
          </span>
          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border uppercase tracking-wider ${current.badge}`}>
            {current.label}
          </span>
        </div>
        <span className="text-[11px] font-semibold text-[#8B7560] shrink-0">
          Advisory
        </span>
      </div>

      {/* Flag Message */}
      <p className="text-sm font-semibold text-[#2D2318] leading-snug break-words">
        {flag.message}
      </p>

      {/* Expandable Evidence Details */}
      <div className="flex flex-col gap-1.5">
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          aria-expanded={expanded}
          className="flex items-center gap-1 text-xs font-bold text-[#8B7560] hover:text-[#2D2318] focus:outline-none focus:underline w-fit"
        >
          <span>{expanded ? 'Hide evidence' : 'View evidence details'}</span>
          <ChevronDown
            className={`w-3.5 h-3.5 transition-transform duration-150 ${expanded ? 'rotate-180' : ''}`}
            aria-hidden
          />
        </button>

        {expanded && (
          <div className="bg-white/90 p-2.5 rounded-lg border border-[#D6CCC0] text-xs font-mono text-[#423223] overflow-x-auto max-w-full">
            <pre className="whitespace-pre-wrap text-[11px]">{JSON.stringify(flag.evidence, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* Footer: Advisory Disclaimer & Action */}
      <div className="flex items-center justify-between gap-2 pt-2 border-t border-[#EBE4DB] mt-0.5">
        <span className="text-[11px] text-[#8B7560] italic">
          Pattern advisory. Discuss with physician.
        </span>

        {flag.status === 'open' && onAcknowledge && (
          <Button
            size="sm"
            variant="secondary"
            onClick={() => onAcknowledge(flag.id)}
            className="flex items-center gap-1 text-xs font-bold px-2.5 py-1 min-h-[30px]"
          >
            <Check className="w-3 h-3" aria-hidden />
            <span>Acknowledge</span>
          </Button>
        )}
      </div>
    </div>
  );
}
