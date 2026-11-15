'use client';

import React from 'react';
import { ConnectionStatus as StatusType } from '@/lib/realtime/useSSE';
import { Wifi, RefreshCw, AlertCircle } from 'lucide-react';

export function ConnectionStatus({
  status,
  onReconnect,
}: {
  status: StatusType;
  onReconnect?: () => void;
}) {
  if (status === 'connected') {
    return (
      <div
        role="status"
        aria-label="Real-time live updates connected"
        className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784]"
      >
        <span className="w-2 h-2 rounded-full bg-[#1B5E20] animate-pulse" aria-hidden />
        <Wifi className="w-3.5 h-3.5" aria-hidden />
        <span>Live SSE Feed Connected</span>
      </div>
    );
  }

  if (status === 'reconnecting') {
    return (
      <div
        role="status"
        aria-label="Reconnecting live updates"
        className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-[#FFF3E0] text-[#8C4E00] border border-[#FFB74D]"
      >
        <RefreshCw className="w-3.5 h-3.5 animate-spin" aria-hidden />
        <span>Reconnecting live updates...</span>
      </div>
    );
  }

  return (
    <button
      onClick={onReconnect}
      role="status"
      aria-label="Live updates stalled. Click to reconnect."
      className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-[#FAEAEA] text-[#B71C1C] border border-[#E57373] hover:bg-[#FFCDD2]"
    >
      <AlertCircle className="w-3.5 h-3.5" aria-hidden />
      <span>Stalled. Tap to reconnect</span>
    </button>
  );
}

