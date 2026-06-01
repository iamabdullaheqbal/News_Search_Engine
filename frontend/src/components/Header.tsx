'use client';

import { useState } from 'react';
import { Search } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { CATEGORIES } from '@/lib/mock';
import { useKeyboardShortcut } from '@/hooks/useKeyboardShortcut';
import { SearchModal } from './SearchModal';
import { cn } from '@/lib/utils';

export function Header() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const pathname = usePathname();
  useKeyboardShortcut('k', () => setIsSearchOpen(true));

  return (
    <>
      <header className="sticky top-0 z-40 bg-cream/90 backdrop-blur-md border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex-shrink-0">
              <Link href="/" className="font-serif italic text-4xl font-medium tracking-tight">
                Veritas
              </Link>
            </div>

            <div className="flex-1 max-w-2xl mx-8 hidden md:block">
              <button
                onClick={() => setIsSearchOpen(true)}
                className="w-full flex items-center px-4 py-2.5 bg-cream-dark/50 hover:bg-cream-dark border border-border rounded-sm transition-colors text-left group"
              >
                <Search className="w-4 h-4 text-charcoal-light mr-3 group-hover:text-charcoal transition-colors" />
                <span className="flex-1 text-sm text-charcoal-light group-hover:text-charcoal transition-colors">
                  Search the global record...
                </span>
                <kbd className="hidden sm:inline-block px-2 py-0.5 text-xxs font-mono font-medium text-charcoal-light bg-cream border border-border rounded">
                  CMD + K
                </kbd>
              </button>
            </div>

            <div className="flex items-center gap-6 text-sm font-bold tracking-wider uppercase">
              <button className="hidden sm:block hover:text-charcoal-light transition-colors">
                Login
              </button>
              <button className="bg-charcoal text-cream px-6 py-2.5 hover:bg-charcoal-light transition-colors">
                Subscribe
              </button>
            </div>
          </div>

          <nav className="flex items-center gap-8 overflow-x-auto py-4 scrollbar-hide text-xs font-bold tracking-wider uppercase text-charcoal-light">
            <Link
              href="/"
              className={cn(
                'whitespace-nowrap transition-colors',
                pathname === '/' ? 'text-charcoal' : 'hover:text-charcoal'
              )}
            >
              For You
            </Link>
            {CATEGORIES.map((category) => (
              <Link
                key={category}
                href={`/category/${category.toLowerCase()}`}
                className={cn(
                  'whitespace-nowrap transition-colors',
                  pathname === `/category/${category.toLowerCase()}`
                    ? 'text-charcoal'
                    : 'hover:text-charcoal'
                )}
              >
                {category}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </>
  );
}
