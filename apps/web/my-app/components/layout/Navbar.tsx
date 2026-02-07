'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BookOpen, Bookmark, Home, User } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useUserStore } from '@/store';

const navItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/stories', label: 'Stories', icon: BookOpen },
  { href: '/bookmarks', label: 'Bookmarks', icon: Bookmark },
  { href: '/progress', label: 'Progress', icon: User },
];

export function Navbar() {
  const pathname = usePathname();
  const { isAuthenticated } = useUserStore();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <Link href="/" className="mr-6 flex items-center space-x-2">
          <BookOpen className="h-6 w-6" />
          <span className="hidden font-bold sm:inline-block">
            Bhasha Kahani
          </span>
        </Link>

        <nav className="flex flex-1 items-center space-x-2 md:justify-end">
          {navItems.map((item) => (
            <Button
              key={item.href}
              variant={pathname === item.href ? 'default' : 'ghost'}
              size="sm"
              className={cn(
                'h-8 justify-start',
                pathname === item.href && 'bg-primary text-primary-foreground'
              )}
              asChild
            >
              <Link href={item.href}>
                <item.icon className="mr-2 h-4 w-4" />
                {item.label}
              </Link>
            </Button>
          ))}
        </nav>

        <div className="ml-4 flex items-center space-x-2">
          {!isAuthenticated && (
            <Button size="sm" variant="outline">
              Sign In
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
