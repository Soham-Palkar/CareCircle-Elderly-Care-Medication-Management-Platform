'use client';

import { useState, useEffect } from 'react';

/**
 * Screen Reader Live Announcer
 * Triggers ARIA live region updates for important real-time events without interrupting focus.
 */

export type AnnouncementPoliteness = 'polite' | 'assertive';

let globalAnnounceFn: ((message: string, politeness?: AnnouncementPoliteness) => void) | null = null;

export function announce(message: string, politeness: AnnouncementPoliteness = 'polite') {
  if (globalAnnounceFn) {
    globalAnnounceFn(message, politeness);
  }
}

export function registerAnnouncer(fn: (message: string, politeness?: AnnouncementPoliteness) => void) {
  globalAnnounceFn = fn;
}

export function useReducedMotion(): boolean {
  const [prefersReduced, setPrefersReduced] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReduced(mediaQuery.matches);

    const handler = (e: MediaQueryListEvent) => setPrefersReduced(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return prefersReduced;
}

