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
    <header className="sticky top-0 z-50 w-full border-b border-amber-200/40 bg-white/80 backdrop-blur-md">
      <div className="container flex h-14 items-center">
        <Link href="/" className="mr-6 flex items-center gap-2 group">
          <span className="text-2xl" aria-hidden="true">&#128214;</span>
          <span className="hidden font-bold sm:inline-block text-lg">
            Bhasha Kahani
          </span>
        </Link>

        <nav className="flex flex-1 items-center gap-1 md:justify-end">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-amber-50 hover:text-foreground'
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
