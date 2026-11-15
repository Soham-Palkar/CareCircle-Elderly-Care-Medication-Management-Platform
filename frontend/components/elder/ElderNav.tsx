'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, List, Mic, Users, HelpCircle } from 'lucide-react';
import { useI18n } from '@/lib/i18n/context';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { href: '/elder', icon: Home, labelKey: 'nav.home' },
  { href: '/elder/today', icon: List, labelKey: 'nav.today' },
  { href: '/elder/voice', icon: Mic, labelKey: 'nav.voice' },
  { href: '/elder/people', icon: Users, labelKey: 'nav.people' },
] as const;

export function ElderNav() {
  const pathname = usePathname();
  const { t } = useI18n();

  return (
    <nav
      aria-label="Main navigation"
      className="fixed bottom-0 left-0 right-0 bg-[#FAF8F5] border-t-2 border-[#E8E0D6] z-50 safe-area-bottom"
    >
      {/* Skip link target */}
      <div className="sr-only" id="nav-start" />

      {/* Help button — always visible at top of nav on mobile */}
      <div className="flex justify-center pt-2 px-4">
        <Link
          href="/elder/help"
          className={cn(
            'flex items-center gap-2 px-6 py-3 rounded-full text-[#FAF8F5] bg-[#B54B2E] font-bold text-xl',
            'min-h-[48px] min-w-[200px] justify-center',
            'focus:outline-none focus:ring-4 focus:ring-[#B54B2E] focus:ring-offset-2',
            'active:scale-95 transition-transform',
          )}
          aria-label="Get help — alert my caretaker"
        >
          <HelpCircle aria-hidden="true" size={28} />
          <span>Get Help</span>
        </Link>
      </div>

      <ul className="flex justify-around items-center px-2 pb-2 pt-1" role="list">
        {NAV_ITEMS.map(({ href, icon: Icon, labelKey }) => {
          const isActive =
            href === '/elder' ? pathname === '/elder' : pathname.startsWith(href);
          return (
            <li key={href}>
              <Link
                href={href}
                aria-current={isActive ? 'page' : undefined}
                className={cn(
                  'flex flex-col items-center gap-1 px-4 py-3 rounded-2xl min-w-[72px] min-h-[72px] justify-center',
                  'text-[20px] font-semibold transition-colors',
                  'focus:outline-none focus:ring-4 focus:ring-[#C97B4B] focus:ring-offset-2',
                  isActive
                    ? 'bg-[#FDF3E7] text-[#8B4513]'
                    : 'text-[#5C4A3A] hover:bg-[#F5EDE0]',
                )}
              >
                <Icon
                  aria-hidden="true"
                  size={32}
                  strokeWidth={isActive ? 2.5 : 2}
                />
                <span className="leading-none">{t(`elder.${labelKey}`)}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
