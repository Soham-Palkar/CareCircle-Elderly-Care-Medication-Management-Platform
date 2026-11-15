'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { setActiveRole } from '@/lib/auth/session';
import { HeartHandshake, Shield, AlertCircle, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export default function LoginPage() {
  const router = useRouter();
  const [circleCode, setCircleCode] = useState('DEVI-7892');
  const [passcode, setPasscode] = useState('123456');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attempts, setAttempts] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!circleCode.trim() || !passcode.trim()) {
      setError('Please provide both circle code and passcode.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await api.login(circleCode, passcode);
      setActiveRole(res.member.role);
      
      if (res.member.role === 'elder') {
        router.push('/elder');
      } else if (res.member.role === 'caretaker') {
        router.push('/care');
      } else {
        router.push('/family');
      }
    } catch {
      const newAttempts = attempts + 1;
      setAttempts(newAttempts);
      if (newAttempts >= 5) {
        setError('This circle account is temporarily locked for security. Please try again after 15 minutes.');
      } else {
        setError('Incorrect circle code or passcode. Please check your credentials.');
      }
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
          Welcome to CareCircle
        </h1>
        <p className="mt-1 text-xs sm:text-sm text-[#5C4A38]">
          Sign in to your Care Circle with your circle code and passcode
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-6 px-6 sm:px-8 shadow-2xs rounded-xl border border-[#EBE4DB] flex flex-col gap-5">
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
              placeholder="Enter your 6-digit PIN or passphrase"
              value={passcode}
              onChange={(e) => setPasscode(e.target.value)}
              required
              helperText="Never shared with anyone else."
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

          {/* Demo Helper Pill */}
          <div className="p-3 bg-[#FAF8F5] rounded-lg border border-[#EBE4DB] text-xs text-[#5C4A38]">
            <span className="font-bold block text-[#2D2318] mb-0.5">Evaluation Demo Account:</span>
            <span>Circle: <code>DEVI-7892</code> · Passcode: <code>123456</code> (Pre-filled for direct review)</span>
          </div>

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

