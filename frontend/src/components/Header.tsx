'use client';

import { useState } from 'react';
import { Menu, Search, X } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { CATEGORIES } from '@/lib/mock';
import { useKeyboardShortcut } from '@/hooks/useKeyboardShortcut';
import { useAuth } from '@/hooks/useAuth';
import { SearchModal } from './SearchModal';
import { AuthModal } from './AuthModal';
import { cn } from '@/lib/utils';

export function Header() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();
  useKeyboardShortcut('k', () => setIsSearchOpen(true));

  const closeMenu = () => setIsMenuOpen(false);
  const openAuthFromMenu = () => {
    closeMenu();
    setIsAuthOpen(true);
  };
  const handleLogout = async () => {
    closeMenu();
    await logout();
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-cream/90 backdrop-blur-md border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 md:h-20">
            <div className="flex min-w-0 flex-shrink-0 items-center">
              <Link
                href="/"
                onClick={closeMenu}
                className="font-serif italic text-3xl sm:text-4xl font-medium tracking-tight"
              >
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

            <div className="hidden md:flex items-center gap-6 text-sm font-bold tracking-wider uppercase">
              {user ? (
                <>
                  <span className="hidden sm:block text-charcoal-light text-xs">
                    {user.name || user.email.split('@')[0]}
                  </span>
                  <button
                    onClick={logout}
                    className="hidden sm:block hover:text-charcoal-light transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsAuthOpen(true)}
                  className="hidden sm:block hover:text-charcoal-light transition-colors"
                >
                  Login
                </button>
              )}
              <button className="bg-charcoal text-cream px-6 py-2.5 hover:bg-charcoal-light transition-colors">
                Subscribe
              </button>
            </div>

            <div className="flex items-center gap-1 md:hidden">
              <button
                onClick={() => setIsSearchOpen(true)}
                className="flex h-10 w-10 items-center justify-center text-charcoal hover:bg-border transition-colors"
                aria-label="Search"
              >
                <Search className="h-5 w-5" />
              </button>
              <button
                onClick={() => setIsMenuOpen((open) => !open)}
                className="flex h-10 w-10 items-center justify-center text-charcoal hover:bg-border transition-colors"
                aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
                aria-expanded={isMenuOpen}
              >
                {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8 overflow-x-auto py-4 scrollbar-hide text-xs font-bold tracking-wider uppercase text-charcoal-light">
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

        {isMenuOpen && (
          <div className="md:hidden border-t border-border bg-cream">
            <div className="px-4 py-5 space-y-6">
              <div className="space-y-1 text-xs font-bold tracking-wider uppercase text-charcoal-light">
                <Link
                  href="/"
                  onClick={closeMenu}
                  className={cn(
                    'block py-2 transition-colors',
                    pathname === '/' ? 'text-charcoal' : 'hover:text-charcoal'
                  )}
                >
                  For You
                </Link>
                {CATEGORIES.map((category) => (
                  <Link
                    key={category}
                    href={`/category/${category.toLowerCase()}`}
                    onClick={closeMenu}
                    className={cn(
                      'block py-2 transition-colors',
                      pathname === `/category/${category.toLowerCase()}`
                        ? 'text-charcoal'
                        : 'hover:text-charcoal'
                    )}
                  >
                    {category}
                  </Link>
                ))}
              </div>

              <div className="border-t border-border pt-5 space-y-3 text-sm font-bold tracking-wider uppercase">
                {user ? (
                  <>
                    <div className="text-xs normal-case tracking-normal text-charcoal-light">
                      Signed in as {user.name || user.email}
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full border border-border px-4 py-3 text-left hover:border-charcoal-light transition-colors"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <button
                    onClick={openAuthFromMenu}
                    className="w-full border border-border px-4 py-3 text-left hover:border-charcoal-light transition-colors"
                  >
                    Login
                  </button>
                )}
                <button className="w-full bg-charcoal text-cream px-4 py-3 text-left hover:bg-charcoal-light transition-colors">
                  Subscribe
                </button>
              </div>
            </div>
          </div>
        )}
      </header>

      <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />
    </>
  );
}
