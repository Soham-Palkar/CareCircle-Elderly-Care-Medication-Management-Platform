'use client';

import React from 'react';
import { EscalationSettings } from '@/components/care/EscalationSettings';
import { TelegramLink } from '@/components/care/TelegramLink';
import { Settings, Bell, Moon, Mail } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function CareSettingsPage() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-8 pb-16">
      <div className="border-b border-[#EBE4DB] pb-4">
        <div className="flex items-center gap-1.5 text-[#C97B4B] mb-0.5">
          <Settings className="w-4 h-4" />
          <span className="text-xs font-bold uppercase tracking-wider">Preferences</span>
        </div>
        <h1 className="text-2xl font-bold text-[#2D2318]">Notifications & Escalation</h1>
        <p className="text-xs sm:text-sm text-[#5C4A38] mt-0.5">
          Configure proactive email alerts, quiet hours, and interactive Telegram responses.
        </p>
      </div>

      {/* Escalation Policy Ladder */}
      <EscalationSettings />

      {/* Telegram Link */}
      <TelegramLink />

      {/* Notification Preferences & Quiet Hours */}
      <div className="bg-white border border-[#EBE4DB] rounded-xl p-5 sm:p-6 shadow-2xs flex flex-col gap-4">
        <div className="border-b border-[#EBE4DB] pb-3">
          <h3 className="text-lg font-bold text-[#2D2318] flex items-center gap-2">
            <Bell className="w-5 h-5 text-[#C97B4B]" aria-hidden />
            <span>Channel Delivery & Quiet Hours</span>
          </h3>
          <p className="text-xs text-[#5C4A38] mt-0.5">
            CareCircle guarantees at-least-once delivery with exponential retry backoff.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="p-3.5 bg-[#FAF8F5] border border-[#EBE4DB] rounded-lg flex items-start gap-2.5">
            <Mail className="w-4 h-4 text-[#5C4A38] shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-xs text-[#2D2318] block">Email Outbox</span>
              <span className="text-xs text-[#5C4A38]">
                Mandatory notifications for missed doses and refills sent to <strong>rajesh.sharma@example.com</strong>
              </span>
            </div>
          </div>

          <div className="p-3.5 bg-[#FAF8F5] border border-[#EBE4DB] rounded-lg flex items-start gap-2.5">
            <Moon className="w-4 h-4 text-[#5C4A38] shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-xs text-[#2D2318] block">Quiet Hours (Night Routine)</span>
              <span className="text-xs text-[#5C4A38]">
                Non-critical alerts muted between <strong>10:00 PM and 06:30 AM</strong> to protect sleep. Critical alerts always bypass.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

