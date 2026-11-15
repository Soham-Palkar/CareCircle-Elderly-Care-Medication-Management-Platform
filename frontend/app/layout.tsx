import './globals.css';
import type { Metadata, Viewport } from 'next';
import { I18nProvider } from '@/lib/i18n/context';
import { Navbar } from '@/components/common/Navbar';
import { OfflineBanner } from '@/components/common/FeedbackStates';
import { LiveAnnouncer } from '@/components/common/LiveAnnouncer';

export const metadata: Metadata = {
  title: 'CareCircle — Elderly Care & Medication Management',
  description: 'Shared care platform keeping the elderly person in control, and family & caretakers informed.',
  manifest: '/manifest.webmanifest',
  icons: {
    icon: '/favicon.ico',
    apple: '/icons/icon-192.png',
  },
};

export const viewport: Viewport = {
  themeColor: '#C97B4B',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/manifest.webmanifest" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
      </head>
      <body>
        <I18nProvider>
          <OfflineBanner />
          <Navbar />
          <LiveAnnouncer />
          {children}
        </I18nProvider>
      </body>
    </html>
  );
}

