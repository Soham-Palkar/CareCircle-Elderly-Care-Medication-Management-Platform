'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n/context';
import { Type } from 'lucide-react';

export function TextSizeControl() {
  const { textSize, setTextSize, t } = useI18n();

  return (
    <div
      role="group"
      aria-label="Text size options"
      className="flex items-center bg-[#F2EDE6] p-0.5 rounded-lg border border-[#D6CCC0]"
    >
      <Type className="w-3.5 h-3.5 mx-1.5 text-[#5C4A38] hidden sm:block shrink-0" aria-hidden />
      <span className="sr-only">{t('common.textSize', 'Text size')}</span>
      <button
        type="button"
        onClick={() => setTextSize('normal')}
        aria-label="Normal text size (18px)"
        aria-pressed={textSize === 'normal'}
        className={`px-2 py-1 rounded-md text-xs font-semibold transition-colors ${
          textSize === 'normal' ? 'bg-white text-[#2D2318] shadow-2xs font-bold' : 'text-[#5C4A38] hover:text-[#2D2318]'
        }`}
      >
        A
      </button>
      <button
        type="button"
        onClick={() => setTextSize('large')}
        aria-label="Large text size (20px)"
        aria-pressed={textSize === 'large'}
        className={`px-2 py-1 rounded-md text-xs font-semibold transition-colors ${
          textSize === 'large' ? 'bg-white text-[#2D2318] shadow-2xs font-bold' : 'text-[#5C4A38] hover:text-[#2D2318]'
        }`}
      >
        A+
      </button>
      <button
        type="button"
        onClick={() => setTextSize('elder')}
        aria-label="Elderly text size (24px+ AAA)"
        aria-pressed={textSize === 'elder'}
        className={`px-2 py-1 rounded-md text-xs font-bold transition-colors ${
          textSize === 'elder'
            ? 'bg-[#C97B4B] text-white shadow-2xs'
            : 'text-[#5C4A38] hover:text-[#2D2318]'
        }`}
      >
        24px
      </button>
    </div>
  );
}
