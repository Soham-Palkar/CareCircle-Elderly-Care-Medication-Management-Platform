'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n/context';
import { Languages } from 'lucide-react';

export function LanguageSwitch() {
  const { locale, setLocale } = useI18n();

  return (
    <div
      role="group"
      aria-label="Language options"
      className="flex items-center bg-[#F2EDE6] p-0.5 rounded-lg border border-[#D6CCC0]"
    >
      <Languages className="w-3.5 h-3.5 mx-1.5 text-[#5C4A38] hidden sm:block shrink-0" aria-hidden />
      <button
        type="button"
        onClick={() => setLocale('en')}
        aria-label="Switch to English"
        aria-pressed={locale === 'en'}
        className={`px-2 py-1 rounded-md text-xs font-semibold transition-colors ${
          locale === 'en' ? 'bg-white text-[#2D2318] shadow-2xs font-bold' : 'text-[#5C4A38] hover:text-[#2D2318]'
        }`}
      >
        EN
      </button>
      <button
        type="button"
        onClick={() => setLocale('hi')}
        aria-label="हिंदी में बदलें"
        aria-pressed={locale === 'hi'}
        className={`px-2 py-1 rounded-md text-xs font-semibold transition-colors ${
          locale === 'hi' ? 'bg-white text-[#2D2318] shadow-2xs font-bold' : 'text-[#5C4A38] hover:text-[#2D2318]'
        }`}
      >
        हिंदी
      </button>
    </div>
  );
}
