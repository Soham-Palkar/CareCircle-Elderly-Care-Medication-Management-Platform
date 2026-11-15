'use client';

import React, { useState, useEffect } from 'react';
import { registerAnnouncer, AnnouncementPoliteness } from '@/lib/a11y/announcements';

export function LiveAnnouncer() {
  const [politeMessage, setPoliteMessage] = useState('');
  const [assertiveMessage, setAssertiveMessage] = useState('');

  useEffect(() => {
    registerAnnouncer((message: string, politeness: AnnouncementPoliteness = 'polite') => {
      if (politeness === 'assertive') {
        setAssertiveMessage(message);
        setTimeout(() => setAssertiveMessage(''), 4000);
      } else {
        setPoliteMessage(message);
        setTimeout(() => setPoliteMessage(''), 4000);
      }
    });
  }, []);

  return (
    <>
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {politeMessage}
      </div>
      <div
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"
      >
        {assertiveMessage}
      </div>
    </>
  );
}

