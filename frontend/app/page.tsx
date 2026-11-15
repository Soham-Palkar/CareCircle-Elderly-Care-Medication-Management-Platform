'use client';

import React from 'react';
import Link from 'next/link';
import { User, Shield, Users, ArrowRight, CheckCircle2, ShieldAlert } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function HomePage() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 sm:py-12 flex flex-col gap-10">
      {/* Hero Section */}
      <section className="text-center flex flex-col items-center gap-4">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FFF3E0] border border-[#FFB74D] text-[#8C4E00] text-xs font-bold uppercase tracking-wider">
          Elderly Care & Medication Coordination
        </span>

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#2D2318] tracking-tight max-w-2xl leading-tight">
          Medication reminders with dignity at the center.
        </h1>

        <p className="text-base sm:text-lg text-[#5C4A38] max-w-2xl font-medium leading-relaxed">
          CareCircle helps older adults manage daily medications, appointments, and routines while keeping authorized caretakers and family informed — with the older adult retaining control.
        </p>

        {/* Primary Entry Actions */}
        <div className="flex flex-wrap items-center justify-center gap-3 mt-2">
          <Link href="/login">
            <Button variant="primary" size="md" className="font-bold px-6">
              Sign In with Circle Code
            </Button>
          </Link>
          <Link href="/create-circle">
            <Button variant="secondary" size="md" className="font-bold px-6">
              Create a Circle
            </Button>
          </Link>
          <Link href="/join">
            <Button variant="outline" size="md" className="font-bold px-5">
              Redeem Invite
            </Button>
          </Link>
        </div>
      </section>

      {/* Role-Specific Capabilities Overview */}
      <section aria-label="Role Experiences" className="flex flex-col gap-4">
        <div className="text-center max-w-xl mx-auto">
          <h2 className="text-xl sm:text-2xl font-bold text-[#2D2318]">
            Tailored Experiences for Every Role
          </h2>
          <p className="text-sm text-[#5C4A38] mt-1">
            CareCircle provides distinct, role-appropriate interfaces governed by backend access controls:
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Elder Experience Card */}
          <div className="bg-white border border-[#EBE4DB] rounded-xl p-6 shadow-2xs flex flex-col justify-between gap-4">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#EEF5EE] border border-[#81C784] text-[#1B5E20] flex items-center justify-center mb-3">
                <User className="w-5 h-5" aria-hidden />
              </div>
              <h3 className="text-lg font-bold text-[#2D2318]">Elderly Experience</h3>
              <p className="text-xs font-semibold text-[#1B5E20] mt-0.5">
                Large 24px+ Type · AAA 7:1 Contrast
              </p>
              <p className="text-sm text-[#5C4A38] mt-2.5 leading-relaxed">
                A calm, uncluttered view centered on the single next dose due. Big touch targets, plain-language audio assistance, and direct emergency caretaker alerts.
              </p>
            </div>
            <ul className="text-xs text-[#5C4A38] space-y-1.5 pt-3 border-t border-[#F2EDE6]">
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#1B5E20] shrink-0" />
                <span>One primary action at a time</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#1B5E20] shrink-0" />
                <span>Voice input with button fallback</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#1B5E20] shrink-0" />
                <span>Final consent on all schedule changes</span>
              </li>
            </ul>
          </div>

          {/* Caretaker Experience Card */}
          <div className="bg-white border border-[#EBE4DB] rounded-xl p-6 shadow-2xs flex flex-col justify-between gap-4">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#FFF3E0] border border-[#FFB74D] text-[#8C4E00] flex items-center justify-center mb-3">
                <Shield className="w-5 h-5" aria-hidden />
              </div>
              <h3 className="text-lg font-bold text-[#2D2318]">Caretaker Dashboard</h3>
              <p className="text-xs font-semibold text-[#8C4E00] mt-0.5">
                Live Timeline · Coordination Tools
              </p>
              <p className="text-sm text-[#5C4A38] mt-2.5 leading-relaxed">
                Real-time dose timeline with SSE synchronization, prescription box scanning with draft review, advisory risk flags (R1–R6), and escalation management.
              </p>
            </div>
            <ul className="text-xs text-[#5C4A38] space-y-1.5 pt-3 border-t border-[#F2EDE6]">
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#8C4E00] shrink-0" />
                <span>Low-stock refill notifications</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#8C4E00] shrink-0" />
                <span>Routine-anchored schedule editor</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#8C4E00] shrink-0" />
                <span>Escalation rules & quiet hours</span>
              </li>
            </ul>
          </div>

          {/* Family Experience Card */}
          <div className="bg-white border border-[#EBE4DB] rounded-xl p-6 shadow-2xs flex flex-col justify-between gap-4">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#F0F4F8] border border-[#BFDBFE] text-[#1E3A8A] flex items-center justify-center mb-3">
                <Users className="w-5 h-5" aria-hidden />
              </div>
              <h3 className="text-lg font-bold text-[#2D2318]">Family Peace-of-Mind</h3>
              <p className="text-xs font-semibold text-[#1E3A8A] mt-0.5">
                Status-First · Permission Bound
              </p>
              <p className="text-sm text-[#5C4A38] mt-2.5 leading-relaxed">
                Clear daily status summary, dose completion indicators, and appointment schedules without overwhelming clinical complexity or unauthorized edit access.
              </p>
            </div>
            <ul className="text-xs text-[#5C4A38] space-y-1.5 pt-3 border-t border-[#F2EDE6]">
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#1E3A8A] shrink-0" />
                <span>Today&apos;s dose completion progress</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#1E3A8A] shrink-0" />
                <span>Missed dose alert summaries</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#1E3A8A] shrink-0" />
                <span>Respects elder-configured permissions</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Safety & Compliance Notice */}
      <section className="bg-white border border-[#EBE4DB] rounded-xl p-5 shadow-2xs flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-[#8B7560] shrink-0 mt-0.5" aria-hidden />
        <div className="text-xs text-[#5C4A38] leading-relaxed">
          <strong className="text-[#2D2318]">Reminder and coordination notice:</strong> CareCircle is a reminder and care coordination platform, not a medical device. It does not provide medical diagnoses, treatment decisions, or clinical monitoring. Schedule proposals and predictive risk patterns are strictly advisory and require human confirmation.
        </div>
      </section>
    </div>
  );
}
