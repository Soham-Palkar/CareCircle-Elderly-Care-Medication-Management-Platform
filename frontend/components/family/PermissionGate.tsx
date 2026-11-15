'use client';

import React from 'react';
import { Lock } from 'lucide-react';

export interface PermissionGateProps {
  /** The kind of content that is hidden — used in the message */
  contentLabel?: string;
  title?: string;
  message?: string;
  /** Children shown when access IS granted */
  children?: React.ReactNode;
  /** Whether access is granted */
  granted?: boolean;
}

export function PermissionGate({
  children,
  granted = false,
  contentLabel = 'this information',
  title = 'Access not granted',
  message,
}: PermissionGateProps) {
  if (granted && children) return <>{children}</>;

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex flex-col items-center justify-center gap-6 py-16 px-6 text-center bg-white rounded-3xl border border-[#D6CCC0]"
    >
      <div className="w-20 h-20 rounded-full bg-[#F5EDE0] flex items-center justify-center">
        <Lock className="text-[#C97B4B]" size={36} aria-hidden="true" />
      </div>
      <div className="max-w-md">
        <h2 className="text-2xl font-bold text-[#2D2318] mb-2">{title}</h2>
        <p className="text-base text-[#5C4A38] leading-relaxed">
          {message ||
            `Your elder has not shared ${contentLabel} with you yet. If you believe this is a mistake, ask them to update their sharing settings.`}
        </p>
      </div>
    </div>
  );
}
