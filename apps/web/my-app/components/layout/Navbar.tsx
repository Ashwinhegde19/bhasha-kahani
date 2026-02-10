'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BookOpen, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/stories', label: 'Stories', icon: BookOpen },
];

export function Navbar() {
  const pathname = usePathname();

  // Hide navbar on the play page for immersive experience
  if (pathname.startsWith('/play/')) return null;

  return (
    <header className="sticky top-0 z-50 w-full glass-card border-b-0 relative">
      <div className="container mx-auto px-4 flex h-14 items-center">
        <Link href="/" className="mr-6 flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-rose-500 flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow">
            <BookOpen className="w-4 h-4 text-white" />
          </div>
          <span className="hidden font-bold sm:inline-block text-lg gradient-text">
            Bhasha Kahani
          </span>
        </Link>

        <nav className="flex flex-1 items-center gap-1.5 md:justify-end">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-2 rounded-full text-sm font-semibold transition-all',
                  isActive
                    ? 'bg-gradient-to-r from-primary to-rose-500 text-white shadow-sm'
                    : 'text-muted-foreground hover:bg-accent hover:text-foreground',
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
      {/* Decorative gradient bottom border */}
      <div
        className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-primary/40 to-transparent"
        aria-hidden="true"
      />
    </header>
  );
}
