'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { setActiveRole } from '@/lib/auth/session';
import {
  HeartHandshake,
  AlertCircle,
  Heart,
  Stethoscope,
  Users,
  User,
  ChevronRight,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

// ---------------------------------------------------------------------------
// Role definitions — describes each member type for the quick-login tiles.
// Demo credentials are displayed openly; role authorization comes from the
// backend in production. The elder retains control of all permissions.
// ---------------------------------------------------------------------------
type DemoRole = {
  role: 'elder' | 'caretaker' | 'family' | 'doctor';
  label: string;
  description: string;
  demoPasscode: string;
  redirectPath: string;
  icon: React.ReactNode;
  accentClass: string;
  badgeClass: string;
};

const DEMO_ROLES: DemoRole[] = [
  {
    role: 'elder',
    label: 'Elder',
    description: 'Savitri Devi — simplified view, full control',
    demoPasscode: '111111',
    redirectPath: '/elder',
    icon: <Heart className="w-5 h-5" aria-hidden />,
    accentClass: 'border-[#C97B4B] bg-[#FDF3E7] text-[#8B4513]',
    badgeClass: 'bg-[#C97B4B] text-white',
  },
  {
    role: 'caretaker',
    label: 'Caretaker',
    description: 'Rajesh Sharma — schedule management, alerts',
    demoPasscode: '222222',
    redirectPath: '/care',
    icon: <Stethoscope className="w-5 h-5" aria-hidden />,
    accentClass: 'border-[#3B6B8A] bg-[#EBF3F9] text-[#1E4A6B]',
    badgeClass: 'bg-[#3B6B8A] text-white',
  },
  {
    role: 'family',
    label: 'Family',
    description: 'Priya Sharma — status view, permitted access',
    demoPasscode: '333333',
    redirectPath: '/family',
    icon: <Users className="w-5 h-5" aria-hidden />,
    accentClass: 'border-[#5B7C5A] bg-[#EEF4EE] text-[#2D5A2C]',
    badgeClass: 'bg-[#5B7C5A] text-white',
  },
  {
    role: 'doctor',
    label: 'Doctor',
    description: 'Dr. Anand Mehta — read-only view (roadmap preview)',
    demoPasscode: '444444',
    redirectPath: '/doctor',
    icon: <User className="w-5 h-5" aria-hidden />,
    accentClass: 'border-[#7B5EA7] bg-[#F4F0FA] text-[#4A2D80]',
    badgeClass: 'bg-[#7B5EA7] text-white',
  },
];

const DEMO_CIRCLE_CODE = 'DEVI-7892';

// ---------------------------------------------------------------------------

export default function LoginPage() {
  const router = useRouter();
  const [circleCode, setCircleCode] = useState(DEMO_CIRCLE_CODE);
  const [passcode, setPasscode] = useState('');
  const [loading, setLoading] = useState(false);
  const [quickLoading, setQuickLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempts, setAttempts] = useState(0);

  // Shared sign-in logic used by both the form and the quick-login tiles
  async function signIn(code: string, pin: string, redirect?: string) {
    setError(null);
    try {
      const res = await api.login(code, pin);
      setActiveRole(res.member.role);
      const path =
        redirect ??
        (res.member.role === 'elder'
          ? '/elder'
          : res.member.role === 'caretaker'
          ? '/care'
          : res.member.role === 'doctor'
          ? '/doctor'
          : '/family');
      router.push(path);
    } catch {
      const newAttempts = attempts + 1;
      setAttempts(newAttempts);
      if (newAttempts >= 5) {
        setError(
          'This circle account is temporarily locked for security. Please try again after 15 minutes.',
        );
      } else {
        setError('Incorrect circle code or passcode. Please check your credentials.');
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!circleCode.trim() || !passcode.trim()) {
      setError('Please provide both circle code and passcode.');
      return;
    }
    setLoading(true);
    await signIn(circleCode, passcode);
    setLoading(false);
  };

  const handleQuickLogin = async (demoRole: DemoRole) => {
    setQuickLoading(demoRole.role);
    setError(null);
    await signIn(DEMO_CIRCLE_CODE, demoRole.demoPasscode, demoRole.redirectPath);
    setQuickLoading(null);
  };

  return (
    <div className="min-h-screen bg-[#FAF8F5] flex flex-col justify-center py-8 px-4 sm:px-6 lg:px-8">
      {/* Brand header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="mx-auto w-12 h-12 rounded-xl bg-[#C97B4B] flex items-center justify-center text-white shadow-sm mb-3">
          <HeartHandshake className="w-6 h-6" aria-hidden />
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-[#2D2318] tracking-tight">
          Welcome to CareCircle
        </h1>
        <p className="mt-1 text-sm text-[#5C4A38]">
          Sign in to your Care Circle with your circle code and passcode
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-lg flex flex-col gap-5">

        {/* ── Demo quick-login tiles ─────────────────────────────────── */}
        <section
          aria-labelledby="demo-heading"
          className="bg-white rounded-xl border border-[#EBE4DB] shadow-sm overflow-hidden"
        >
          <div className="px-5 py-3 bg-[#FAF8F5] border-b border-[#EBE4DB] flex items-center gap-2">
            <span
              id="demo-heading"
              className="text-xs font-bold tracking-widest uppercase text-[#8B6C55]"
            >
              Demo — sign in as
            </span>
            <span className="ml-auto text-[10px] font-medium text-[#8B6C55] bg-[#EBE4DB] rounded px-2 py-0.5">
              Circle: {DEMO_CIRCLE_CODE}
            </span>
          </div>

          <ul className="divide-y divide-[#EBE4DB]" role="list">
            {DEMO_ROLES.map((demoRole) => (
              <li key={demoRole.role}>
                <button
                  type="button"
                  onClick={() => handleQuickLogin(demoRole)}
                  disabled={quickLoading !== null || loading}
                  aria-busy={quickLoading === demoRole.role}
                  className={[
                    'w-full flex items-center gap-4 px-5 py-3.5 text-left',
                    'hover:bg-[#FAF8F5] focus:outline-none focus:ring-2 focus:ring-inset focus:ring-[#C97B4B]',
                    'transition-colors disabled:opacity-60 disabled:cursor-not-allowed',
                  ].join(' ')}
                >
                  {/* Role icon badge */}
                  <span
                    className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${demoRole.badgeClass}`}
                    aria-hidden
                  >
                    {demoRole.icon}
                  </span>

                  {/* Label + description */}
                  <span className="flex-1 min-w-0">
                    <span className="block text-sm font-bold text-[#2D2318]">
                      {demoRole.label}
                    </span>
                    <span className="block text-xs text-[#5C4A38] truncate">
                      {demoRole.description}
                    </span>
                  </span>

                  {/* Passcode hint */}
                  <span className="shrink-0 flex items-center gap-1.5">
                    <span className="text-xs text-[#8B6C55] font-mono bg-[#F5EDE0] rounded px-1.5 py-0.5">
                      {demoRole.demoPasscode}
                    </span>
                    {quickLoading === demoRole.role ? (
                      <svg
                        className="w-4 h-4 animate-spin text-[#C97B4B]"
                        fill="none"
                        viewBox="0 0 24 24"
                        aria-hidden
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                        />
                      </svg>
                    ) : (
                      <ChevronRight className="w-4 h-4 text-[#C97B4B]" aria-hidden />
                    )}
                  </span>
                </button>
              </li>
            ))}
          </ul>

          <p className="px-5 py-2.5 text-[10px] text-[#8B6C55] bg-[#FAF8F5] border-t border-[#EBE4DB]">
            Demo only. Role access is determined by the backend in production — selecting a tile
            here uses that member's demo passcode, not a UI-side override.
          </p>
        </section>

        {/* ── Divider ──────────────────────────────────────────────────── */}
        <div className="flex items-center gap-3" aria-hidden>
          <div className="flex-1 border-t border-[#EBE4DB]" />
          <span className="text-xs text-[#8B6C55] font-medium">or sign in with passcode</span>
          <div className="flex-1 border-t border-[#EBE4DB]" />
        </div>

        {/* ── Standard login form ──────────────────────────────────────── */}
        <div className="bg-white py-6 px-6 sm:px-8 shadow-sm rounded-xl border border-[#EBE4DB] flex flex-col gap-5">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              label="Circle Code *"
              placeholder="e.g. DEVI-7892"
              value={circleCode}
              onChange={(e) => setCircleCode(e.target.value)}
              required
              helperText="The public code for your shared Care Circle."
            />

            <Input
              label="Passcode / PIN *"
              type="password"
              placeholder="Enter your passcode"
              value={passcode}
              onChange={(e) => setPasscode(e.target.value)}
              required
              helperText="Your private passcode — never shared with others."
            />

            {error && (
              <div
                role="alert"
                className="p-3 bg-[#FAEAEA] border border-[#E57373] rounded-lg flex items-start gap-2 text-xs font-semibold text-[#B71C1C]"
              >
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="md"
              loading={loading}
              className="w-full font-bold"
            >
              Sign In
            </Button>
          </form>

          <div className="border-t border-[#EBE4DB] pt-4 flex flex-col gap-2 text-center text-sm font-medium text-[#5C4A38]">
            <p>
              Starting a new circle?{' '}
              <Link href="/create-circle" className="text-[#C97B4B] font-bold hover:underline">
                Create Care Circle
              </Link>
            </p>
            <p>
              Have an invite code?{' '}
              <Link href="/join" className="text-[#C97B4B] font-bold hover:underline">
                Join with Invite
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
