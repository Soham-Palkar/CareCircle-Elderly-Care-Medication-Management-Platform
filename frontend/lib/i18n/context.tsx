'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import enMessages from '../../messages/en.json';
import hiMessages from '../../messages/hi.json';

type Locale = 'en' | 'hi';
type TextSize = 'normal' | 'large' | 'elder';

interface I18nContextType {
  locale: Locale;
  setLocale: (loc: Locale) => void;
  textSize: TextSize;
  setTextSize: (size: TextSize) => void;
  t: (key: string, fallback?: string) => string;
}

const I18nContext = createContext<I18nContextType>({
  locale: 'en',
  setLocale: () => {},
  textSize: 'normal',
  setTextSize: () => {},
  t: (key: string) => key,
});

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('en');
  const [textSize, setTextSizeState] = useState<TextSize>('normal');

  useEffect(() => {
    const savedLocale = localStorage.getItem('carecircle_locale') as Locale;
    if (savedLocale === 'en' || savedLocale === 'hi') {
      setLocaleState(savedLocale);
    }
    const savedSize = localStorage.getItem('carecircle_textsize') as TextSize;
    if (savedSize === 'normal' || savedSize === 'large' || savedSize === 'elder') {
      setTextSizeState(savedSize);
    }
  }, []);

  const setLocale = (loc: Locale) => {
    setLocaleState(loc);
    localStorage.setItem('carecircle_locale', loc);
  };

  const setTextSize = (size: TextSize) => {
    setTextSizeState(size);
    localStorage.setItem('carecircle_textsize', size);
  };

  const t = (keyPath: string, fallback?: string): string => {
    const messages = locale === 'hi' ? hiMessages : enMessages;
    const parts = keyPath.split('.');
    let current: any = messages;

    for (const part of parts) {
      if (current && typeof current === 'object' && part in current) {
        current = current[part];
      } else {
        return fallback || keyPath;
      }
    }

    return typeof current === 'string' ? current : fallback || keyPath;
  };

  return (
    <I18nContext.Provider value={{ locale, setLocale, textSize, setTextSize, t }}>
      <div
        className={`min-h-screen text-[#2D2318] bg-[#FAF8F5] ${
          textSize === 'elder'
            ? 'elder-text-mode'
            : textSize === 'large'
            ? 'large-text-mode'
            : 'base-text-mode'
        }`}
      >
        {children}
      </div>
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}

