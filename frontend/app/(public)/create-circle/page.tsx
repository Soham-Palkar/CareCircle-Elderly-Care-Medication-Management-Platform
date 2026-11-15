'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { setActiveRole } from '@/lib/auth/session';
import { HeartHandshake, ShieldCheck, Copy, Check, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export default function CreateCirclePage() {
  const router = useRouter();
  const [step, setStep] = useState<'form' | 'created'>('form');
  const [circleName, setCircleName] = useState('');
  const [elderName, setElderName] = useState('');
  const [passcode, setPasscode] = useState('');
  const [confirmPasscode, setConfirmPasscode] = useState('');
  const [createdCircleCode, setCreatedCircleCode] = useState('');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passcode.length < 6) {
      setError('Passcode must be at least 6 digits long.');
      return;
    }
    if (passcode !== confirmPasscode) {
      setError('Passcodes do not match.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.createCircle({
        circleName,
        elderName,
        passcode,
      });
      setCreatedCircleCode(res.circle.circleCode);
      setActiveRole('elder');
      setStep('created');
    } finally {
      setLoading(false);
    }
  };

  const copyCode = () => {
    navigator.clipboard.writeText(createdCircleCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-[#FAF8F5] flex flex-col justify-center py-8 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="mx-auto w-12 h-12 rounded-xl bg-[#C97B4B] flex items-center justify-center text-white shadow-2xs mb-3">
          <HeartHandshake className="w-6 h-6" aria-hidden />
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-[#2D2318] tracking-tight">
          Create a New Care Circle
        </h1>
        <p className="mt-1 text-xs sm:text-sm text-[#5C4A38]">
          Keep the elderly person at the centre of their health decisions
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-6 px-6 sm:px-8 shadow-2xs rounded-xl border border-[#EBE4DB] flex flex-col gap-5">
          {step === 'form' ? (
            <form onSubmit={handleCreate} className="flex flex-col gap-5">
              <Input
                label="Care Circle Name *"
                placeholder="e.g. Devi Family Care"
                value={circleName}
                onChange={(e) => setCircleName(e.target.value)}
                required
              />

              <Input
                label="Elder's Full Name *"
                placeholder="e.g. Savitri Devi"
                value={elderName}
                onChange={(e) => setElderName(e.target.value)}
                required
              />

              <Input
                label="Passcode (6+ digits) *"
                type="password"
                placeholder="Choose a memorable 6-digit PIN"
                value={passcode}
                onChange={(e) => setPasscode(e.target.value)}
                required
                helperText="A simple 6-digit number works best for elderly mode."
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
                Create Care Circle
              </Button>
            </form>
          ) : (
            <div className="flex flex-col gap-6 text-center animate-fade-in">
              <div className="p-4 bg-[#EEF5EE] rounded-full w-16 h-16 mx-auto flex items-center justify-center text-[#1B5E20]">
                <ShieldCheck className="w-10 h-10" />
              </div>

              <div>
                <h2 className="text-2xl font-black text-[#1B5E20]">Circle Created Successfully!</h2>
                <p className="text-sm text-[#5C4A38] mt-2">
                  Below is your unique public Circle Code. Please save and store it securely:
                </p>
              </div>

              <div className="p-4 bg-[#FAF8F5] border-2 border-[#C97B4B] rounded-2xl flex items-center justify-between">
                <code className="text-2xl font-mono font-black text-[#2D2318] tracking-wider">
                  {createdCircleCode}
                </code>
                <Button size="sm" variant="secondary" onClick={copyCode} className="flex items-center gap-1.5">
                  {copied ? <Check className="w-4 h-4 text-[#1B5E20]" /> : <Copy className="w-4 h-4" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </Button>
              </div>

              <div className="text-xs text-[#8C4E00] bg-[#FFF3E0] p-3.5 rounded-xl border border-[#FFB74D] text-left">
                <strong>Storage Notice:</strong> Store this code in a secure location. You and your invited caretakers will use this circle code alongside your personal passcodes to sign in.
              </div>

              <Button
                variant="primary"
                size="lg"
                onClick={() => router.push('/elder')}
                className="w-full text-lg font-bold flex items-center justify-center gap-2"
              >
                <span>Proceed to Elder Home</span>
                <ArrowRight className="w-5 h-5" />
              </Button>
            </div>
          )}

          <div className="border-t border-[#EBE4DB] pt-4 text-center text-sm font-medium text-[#5C4A38]">
            Already have a Care Circle?{' '}
            <Link href="/login" className="text-[#C97B4B] font-bold hover:underline">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

