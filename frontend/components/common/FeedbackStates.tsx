'use client';

import React from 'react';
import { Loader2, AlertCircle, Inbox, WifiOff } from 'lucide-react';
import { Button } from '../ui/Button';

export function LoadingState({ message = 'Loading details...' }: { message?: string }) {
  return (
    <div role="status" className="flex flex-col items-center justify-center p-12 gap-4 text-[#5C4A38]">
      <Loader2 className="w-10 h-10 animate-spin text-[#C97B4B]" aria-hidden />
      <p className="text-lg font-medium">{message}</p>
    </div>
  );
}

export function EmptyState({
  title = 'No items yet',
  description,
  actionLabel,
  onAction,
}: {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-3xl border border-dashed border-[#D6CCC0] gap-4">
      <div className="p-4 rounded-full bg-[#FAF8F5] text-[#8B7560]">
        <Inbox className="w-10 h-10" aria-hidden />
      </div>
      <div>
        <h3 className="text-xl font-bold text-[#2D2318]">{title}</h3>
        {description && <p className="text-base text-[#5C4A38] mt-1 max-w-sm">{description}</p>}
      </div>
      {actionLabel && onAction && (
        <Button onClick={onAction} variant="primary" className="mt-2">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

export function ErrorState({
  title = 'Could not load data',
  message = 'There was a problem communicating with the service.',
  onRetry,
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div role="alert" className="flex flex-col items-center justify-center p-8 text-center bg-[#FAEAEA] rounded-3xl border border-[#E57373] gap-4">
      <AlertCircle className="w-10 h-10 text-[#B71C1C]" aria-hidden />
      <div>
        <h3 className="text-xl font-bold text-[#8C2D2D]">{title}</h3>
        <p className="text-base text-[#5C4A38] mt-1">{message}</p>
      </div>
      {onRetry && (
        <Button onClick={onRetry} variant="secondary" className="mt-2">
          Try Again
        </Button>
      )}
    </div>
  );
}

export function OfflineBanner() {
  const [isOffline, setIsOffline] = React.useState(false);

  React.useEffect(() => {
    if (typeof window === 'undefined') return;
    setIsOffline(!navigator.onLine);
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOffline) return null;

  return (
    <div
      role="status"
      className="bg-[#3D2F22] text-[#FAF8F5] px-4 py-2.5 flex items-center justify-center gap-3 text-sm font-semibold"
    >
      <WifiOff className="w-4 h-4 text-[#FFB74D]" aria-hidden />
      <span>You are browsing offline. Actions will be recorded and synced once connection resumes.</span>
    </div>
  );
}

