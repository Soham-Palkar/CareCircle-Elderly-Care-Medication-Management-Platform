'use client';

import React, { useState } from 'react';
import { Send, CheckCircle2, MessageSquare, ExternalLink } from 'lucide-react';
import { Button } from '../ui/Button';

export function TelegramLink() {
  const [linked, setLinked] = useState(true);

  return (
    <div className="bg-white border border-[#EBE4DB] rounded-xl p-5 sm:p-6 shadow-2xs flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EBE4DB] pb-3">
        <div>
          <div className="flex items-center gap-2">
            <Send className="w-5 h-5 text-[#0088CC]" aria-hidden />
            <h3 className="text-lg font-bold text-[#2D2318]">Telegram Messaging Bridge</h3>
          </div>
          <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
            Receive proactive reminders and record doses directly from Telegram without opening the app.
          </p>
        </div>

        {linked ? (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-bold bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784] w-fit">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Connected (@RajeshCareBot)</span>
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-bold bg-[#F2EDE6] text-[#5C4A38] w-fit">
            Not Linked
          </span>
        )}
      </div>

      {/* How replies work: 1, 2, 3 */}
      <div className="bg-[#FAF8F5] border border-[#EBE4DB] rounded-lg p-4 flex flex-col gap-2.5">
        <h4 className="text-xs font-bold uppercase tracking-wider text-[#8C4E00] flex items-center gap-1.5">
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Interactive Reply Shortcuts</span>
        </h4>
        <p className="text-xs text-[#5C4A38]">
          When CareCircle sends a reminder to your Telegram, you or family members can simply reply with single digits:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
          <div className="p-3 bg-white rounded-lg border border-[#EBE4DB]">
            <span className="text-base font-bold text-[#1B5E20] block">Reply &ldquo;1&rdquo;</span>
            <span className="text-xs text-[#5C4A38]">Marks dose as <strong>Taken</strong> in shared log</span>
          </div>
          <div className="p-3 bg-white rounded-lg border border-[#EBE4DB]">
            <span className="text-base font-bold text-[#8C4E00] block">Reply &ldquo;2&rdquo;</span>
            <span className="text-xs text-[#5C4A38]"><strong>Snoozes</strong> reminder for 15 minutes</span>
          </div>
          <div className="p-3 bg-white rounded-lg border border-[#EBE4DB]">
            <span className="text-base font-bold text-[#B71C1C] block">Reply &ldquo;3&rdquo;</span>
            <span className="text-xs text-[#5C4A38]">Logs dose as <strong>Skipped</strong> with reason</span>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center pt-2">
        <a
          href="https://t.me/CareCircleBot?start=token-rajesh-7892"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sm font-bold text-[#0088CC] hover:underline"
        >
          <span>Open Telegram Bot Direct Link</span>
          <ExternalLink className="w-4 h-4" />
        </a>
        <Button
          variant={linked ? 'outline' : 'primary'}
          size="sm"
          onClick={() => setLinked(!linked)}
        >
          {linked ? 'Unlink Telegram' : 'Connect Telegram'}
        </Button>
      </div>
    </div>
  );
}

