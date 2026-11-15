'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { setActiveRole } from '@/lib/auth/session';
import { HeartHandshake, UserCheck, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export default function JoinCirclePage() {
  const router = useRouter();
  const [inviteCode, setInviteCode] = useState('INV-FAMILY-4821');
  const [displayName, setDisplayName] = useState('Priya Sharma');
  const [passcode, setPasscode] = useState('654321');
  const [confirmPasscode, setConfirmPasscode] = useState('654321');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passcode.length < 6) {
      setError('Passcode must be at least 6 characters/digits.');
      return;
    }
    if (passcode !== confirmPasscode) {
      setError('Passcodes do not match.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.joinCircle(inviteCode, passcode, displayName);
      setActiveRole('family');
      router.push('/family');
    } catch {
      setError('Invalid or expired invite code. Please request a new code from your circle administrator.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAF8F5] flex flex-col justify-center py-8 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="mx-auto w-12 h-12 rounded-xl bg-[#C97B4B] flex items-center justify-center text-white shadow-2xs mb-3">
          <HeartHandshake className="w-6 h-6" aria-hidden />
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-[#2D2318] tracking-tight">
          Join a Care Circle
        </h1>
        <p className="mt-1 text-xs sm:text-sm text-[#5C4A38]">
          Redeem your single-use invite code to connect with your family circle
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-6 px-6 sm:px-8 shadow-2xs rounded-xl border border-[#EBE4DB] flex flex-col gap-5">
          <form onSubmit={handleJoin} className="flex flex-col gap-5">
            <Input
              label="Invite Code *"
              placeholder="e.g. INV-FAMILY-4821"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value)}
              required
              helperText="The code shared by your circle administrator."
            />

            <Input
              label="Your Display Name *"
              placeholder="e.g. Priya Sharma"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              required
            />

            <Input
              label="Set Your Passcode (6+ digits) *"
              type="password"
              placeholder="Create your personal passcode"
              value={passcode}
              onChange={(e) => setPasscode(e.target.value)}
              required
            />

            <Input
              label="Confirm Passcode *"
              type="password"
              placeholder="Re-enter passcode"
              value={confirmPasscode}
              onChange={(e) => setConfirmPasscode(e.target.value)}
              required
            />

            {error && (
              <div role="alert" className="p-3 bg-[#FAEAEA] border border-[#E57373] rounded-xl text-sm font-semibold text-[#B71C1C]">
                {error}
              </div>
            )}

            <Button type="submit" variant="primary" size="lg" loading={loading} className="w-full text-lg font-bold">
              Join Circle
            </Button>
          </form>

          <div className="border-t border-[#EBE4DB] pt-4 text-center text-sm font-medium text-[#5C4A38]">
            Already signed up?{' '}
            <Link href="/login" className="text-[#C97B4B] font-bold hover:underline">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

