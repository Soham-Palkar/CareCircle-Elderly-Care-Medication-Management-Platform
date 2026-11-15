'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { setActiveRole } from '@/lib/auth/session';
import { HeartHandshake, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export default function LoginPage() {
  const router = useRouter();
  const [circleCode, setCircleCode] = useState('');
  const [passcode, setPasscode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attempts, setAttempts] = useState(0);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const cleanCode = circleCode.trim().toUpperCase();
    const cleanPass = passcode.trim();

    if (!cleanCode || !cleanPass) {
      setError('Please provide both circle code and passcode.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await api.login(cleanCode, cleanPass);
      setActiveRole(res.member.role);
      const targetPath =
        res.member.role === 'elder'
          ? '/elder'
          : res.member.role === 'caretaker'
          ? '/care'
          : res.member.role === 'doctor'
          ? '/doctor'
          : '/family';
      router.push(targetPath);
    } catch (err: unknown) {
      const newAttempts = attempts + 1;
      setAttempts(newAttempts);

      const apiErr = err as { code?: string; message?: string };
      if (newAttempts >= 5 || apiErr?.code === 'ACCOUNT_LOCKED') {
        setError(
          'This circle account is temporarily locked for security. Please try again after 15 minutes.',
        );
      } else {
        setError(
          apiErr?.message ||
            'Incorrect circle code or passcode. Please check your credentials.',
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#FAF8F5] flex flex-col justify-center py-8 px-4 sm:px-6 lg:px-8">
      {/* Brand header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="mx-auto w-12 h-12 rounded-xl bg-[#C97B4B] flex items-center justify-center text-white shadow-2xs mb-3">
          <HeartHandshake className="w-6 h-6" aria-hidden />
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-[#2D2318] tracking-tight">
          Welcome to CareCircle
        </h1>
        <p className="mt-1 text-sm text-[#5C4A38]">
          Sign in to your Care Circle with your circle code and passcode
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md flex flex-col gap-5">
        {/* Standard production login form */}
        <div className="bg-white py-6 px-6 sm:px-8 shadow-2xs rounded-xl border border-[#EBE4DB] flex flex-col gap-5">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              label="Circle Code *"
              placeholder="e.g. ABCD-1234"
              value={circleCode}
              onChange={(e) => setCircleCode(e.target.value.toUpperCase())}
              required
              helperText="The unique code for your shared Care Circle."
              autoComplete="organization"
            />

            <Input
              label="Passcode / PIN *"
              type="password"
              placeholder="Enter your private passcode"
              value={passcode}
              onChange={(e) => setPasscode(e.target.value)}
              required
              helperText="Your private passcode — never shared with others."
              autoComplete="current-password"
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
              <Link
                href="/create-circle"
                className="text-[#C97B4B] font-bold hover:underline"
              >
                Create Care Circle
              </Link>
            </p>
            <p>
              Have an invite code?{' '}
              <Link
                href="/join"
                className="text-[#C97B4B] font-bold hover:underline"
              >
                Join with Invite
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
