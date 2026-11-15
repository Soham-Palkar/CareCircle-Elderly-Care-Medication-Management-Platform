'use client';

import React, { useState } from 'react';
import { AlertCircle, PhoneCall, CheckCircle2 } from 'lucide-react';
import { Button } from '../ui/Button';

export function HelpButton({ onAlertSent }: { onAlertSent?: () => void }) {
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleAlert = async () => {
    setLoading(true);
    // Simulate immediate caretaker alert
    await new Promise((resolve) => setTimeout(resolve, 800));
    setLoading(false);
    setSent(true);
    onAlertSent?.();
  };

  if (sent) {
    return (
      <div
        role="status"
        aria-live="assertive"
        className="p-8 bg-[#EEF5EE] border-3 border-[#81C784] rounded-3xl text-center flex flex-col items-center gap-4 animate-fade-in"
      >
        <CheckCircle2 className="w-16 h-16 text-[#1B5E20]" aria-hidden />
        <h3 className="text-3xl font-extrabold text-[#1B5E20]">Help Alert Sent</h3>
        <p className="text-2xl text-[#2D2318] font-semibold">
          Rajesh has received an urgent notification on his phone and will contact you immediately.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <Button
        variant="destructive"
        size="elder"
        loading={loading}
        onClick={handleAlert}
        aria-label="Alert Caretaker now"
        className="w-full min-h-[72px] text-3xl font-black bg-[#B71C1C] hover:bg-[#8B0000] border-3 border-[#E57373] shadow-xl flex items-center justify-center gap-4 rounded-3xl"
      >
        <AlertCircle className="w-10 h-10" aria-hidden />
        <span>Alert My Caretaker</span>
      </Button>
      <p className="text-xl text-center text-[#5C4A38] font-medium">
        Tapping this sends an instant priority alert to Rajesh and your family.
      </p>
    </div>
  );
}

