'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, PhoneCall } from 'lucide-react';
import { HelpButton } from '@/components/elder/HelpButton';

export default function ElderHelpPage() {
  return (
    <div className="flex flex-col gap-8 pb-12">
      <div className="flex items-center gap-4">
        <Link
          href="/elder"
          aria-label="Back to main screen"
          className="p-3 bg-white border-2 border-[#D6CCC0] rounded-2xl text-[#1A150E] focus:outline-none focus:ring-4 focus:ring-[#C97B4B]"
        >
          <ArrowLeft className="w-8 h-8" aria-hidden />
        </Link>
        <div>
          <h1 className="text-4xl font-black text-[#1A150E]">Immediate Assistance</h1>
          <p className="text-2xl text-[#5C4A38] font-medium">Reach your caretaker right away</p>
        </div>
      </div>

      <div className="bg-white border-2 border-[#C4B29F] rounded-3xl p-8 sm:p-12 shadow-lg flex flex-col gap-8">
        <HelpButton />

        <div className="border-t border-[#EBE4DB] pt-8 flex flex-col gap-4 text-center">
          <h2 className="text-2xl font-bold text-[#1A150E]">Direct Contact</h2>
          <p className="text-2xl text-[#5C4A38] font-medium">
            You can also call Rajesh directly if you have your telephone nearby:
          </p>
          <a
            href="tel:+919876543210"
            className="inline-flex items-center justify-center gap-3 bg-[#FAF8F5] border-2 border-[#C97B4B] text-[#A5622D] hover:bg-[#F2EDE6] px-8 py-5 rounded-2xl text-2xl font-bold max-w-sm mx-auto w-full focus:outline-none focus:ring-4 focus:ring-[#C97B4B]"
          >
            <PhoneCall className="w-8 h-8" aria-hidden />
            <span>+91 98765 43210</span>
          </a>
        </div>
      </div>
    </div>
  );
}

