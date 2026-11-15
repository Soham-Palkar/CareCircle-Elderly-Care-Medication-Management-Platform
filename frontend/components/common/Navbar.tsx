'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { HeartHandshake, Shield, User, Users, Stethoscope, Copy, Check, LogOut } from 'lucide-react';
import { getActiveRole } from '@/lib/auth/session';
import { Role } from '@/lib/api/types';
import { TextSizeControl } from './TextSizeControl';
import { LanguageSwitch } from './LanguageSwitch';
import { mockCircle } from '@/lib/api/mockData';

export function Navbar() {
  const [activeRole, setActiveRoleState] = useState<Role>('elder');
  const [copied, setCopied] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setActiveRoleState(getActiveRole());

    const handleAuthChange = () => {
      setActiveRoleState(getActiveRole());
    };
    window.addEventListener('carecircle_auth_change', handleAuthChange);
    return () => window.removeEventListener('carecircle_auth_change', handleAuthChange);
  }, []);

  const copyCircleCode = () => {
    navigator.clipboard.writeText(mockCircle.circleCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isElderRoute = pathname?.startsWith('/elder');
  const isCareRoute = pathname?.startsWith('/care');
  const isFamilyRoute = pathname?.startsWith('/family');
  const isDoctorRoute = pathname?.startsWith('/doctor');
  const isPublicRoute = !isElderRoute && !isCareRoute && !isFamilyRoute && !isDoctorRoute;

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-xs border-b border-[#EBE4DB] shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16 gap-3">
          {/* Logo & Role Context Badge */}
          <div className="flex items-center gap-3 min-w-0">
            <Link
              href={isElderRoute ? '/elder' : isFamilyRoute ? '/family' : isCareRoute ? '/care' : '/'}
              className="flex items-center gap-2.5 focus:outline-none focus:ring-2 focus:ring-[#C97B4B] rounded-lg p-0.5 shrink-0"
              aria-label="CareCircle Home"
            >
              <div className="w-9 h-9 rounded-xl bg-[#C97B4B] flex items-center justify-center text-white shadow-2xs">
                <HeartHandshake className="w-5 h-5" aria-hidden />
              </div>
              <span className="text-xl font-bold text-[#2D2318] tracking-tight">
                CareCircle
              </span>
            </Link>

            {/* Read-Only Context Indicator (Security is session/backend authenticated) */}
            {isElderRoute && (
              <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold bg-[#EEF5EE] text-[#1B5E20] border border-[#81C784]">
                <User className="w-3.5 h-3.5" aria-hidden />
                <span>Elder Mode</span>
              </span>
            )}
            {isCareRoute && (
              <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold bg-[#FFF3E0] text-[#8C4E00] border border-[#FFB74D]">
                <Shield className="w-3.5 h-3.5" aria-hidden />
                <span>Caretaker View</span>
              </span>
            )}
            {isFamilyRoute && (
              <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold bg-[#F0F4F8] text-[#1E3A8A] border border-[#BFDBFE]">
                <Users className="w-3.5 h-3.5" aria-hidden />
                <span>Family View</span>
              </span>
            )}
            {isDoctorRoute && (
              <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold bg-[#F2EDE6] text-[#5C4A38] border border-[#D6CCC0]">
                <Stethoscope className="w-3.5 h-3.5" aria-hidden />
                <span>Roadmap Preview</span>
              </span>
            )}
          </div>

          {/* Right Controls: Circle Code, A11y Text Size, Language, Auth Link */}
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            {!isPublicRoute && (
              <button
                onClick={copyCircleCode}
                title="Copy Circle Code"
                aria-label={`Circle Code ${mockCircle.circleCode}, click to copy`}
                className="hidden md:flex items-center gap-1.5 px-2.5 py-1 bg-[#FAF8F5] border border-[#D6CCC0] rounded-lg text-xs font-bold text-[#5C4A38] hover:bg-[#F2EDE6] transition-colors"
              >
                <span>Circle: {mockCircle.circleCode}</span>
                {copied ? <Check className="w-3.5 h-3.5 text-[#5C8C5A]" /> : <Copy className="w-3.5 h-3.5 text-[#8B7560]" />}
              </button>
            )}

            <TextSizeControl />
            <LanguageSwitch />

            {!isPublicRoute ? (
              <Link
                href="/login"
                title="Sign out or switch circle"
                aria-label="Sign out or switch circle"
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold text-[#5C4A38] hover:text-[#2D2318] hover:bg-[#F2EDE6] border border-transparent hover:border-[#D6CCC0] transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" aria-hidden />
                <span className="hidden sm:inline">Sign Out</span>
              </Link>
            ) : (
              <Link
                href="/login"
                className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold bg-[#C97B4B] text-white hover:bg-[#A5622D] shadow-2xs transition-colors"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
