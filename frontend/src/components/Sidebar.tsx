'use client';

import { useEffect, useState } from 'react';
import { CATEGORIES, LIVE_WIRE } from '@/lib/mock';
import { getTrending } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { useFollows } from '@/hooks/useFollows';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const { user, toggleInterest } = useAuth();
  const { follows: cookieFollows, toggleFollow: toggleCookieFollow } = useFollows();
  const [trending, setTrending] = useState<string[]>([]);

  useEffect(() => {
    getTrending(5)
      .then((data) => setTrending(data))
      .catch(() => {/* backend not available yet */});
  }, []);

  // Determine current follows: DB for logged-in users, cookie for guests
  const follows = user ? user.interests : cookieFollows;

  const handleToggle = (category: string) => {
    if (user) {
      toggleInterest(category);
    } else {
      toggleCookieFollow(category);
    }
  };

  const privacyNote = user
    ? 'Your preferences are synced to your account.'
    : 'Tap a topic to personalize your feed. Stored in a cookie — nothing leaves the browser.';

  return (
    <aside className="w-full lg:w-80 flex-shrink-0 space-y-12">
      {/* Trending Now */}
      <section>
        <h3 className="text-xs font-bold tracking-wider uppercase mb-6">Trending Now</h3>
        <div className="space-y-5">
          {(trending.length > 0 ? trending : ['Loading…']).map((title, i) => (
            <article key={i} className="flex gap-4 group cursor-pointer">
              <span className="text-sm font-serif italic text-charcoal-light/50 mt-0.5">
                {String(i + 1).padStart(2, '0')}
              </span>
              <h4 className="font-serif text-lg leading-tight group-hover:text-charcoal-light transition-colors">
                {title}
              </h4>
            </article>
          ))}
        </div>
      </section>

      {/* Your Follows */}
      <section className="bg-cream-dark/30 border border-border p-6">
        <h3 className="text-xs font-bold tracking-wider uppercase mb-2">Your Follows</h3>
        <p className="text-sm text-charcoal-light mb-6 leading-relaxed">{privacyNote}</p>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((category) => {
            const isFollowing = follows.includes(category);
            return (
              <button
                key={category}
                onClick={() => handleToggle(category)}
                className={cn(
                  'px-3 py-1.5 text-xs font-bold tracking-wider uppercase transition-all duration-200',
                  isFollowing
                    ? 'bg-charcoal text-cream border border-charcoal'
                    : 'bg-cream text-charcoal border border-border hover:border-charcoal-light'
                )}
              >
                {category}
              </button>
            );
          })}
        </div>
      </section>

      {/* Live Wire */}
      <section>
        <div className="flex items-center gap-2 mb-6">
          <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          <h3 className="text-xs font-bold tracking-wider uppercase">Live Wire</h3>
        </div>
        <div className="space-y-0 border-t border-border">
          {LIVE_WIRE.map((item, i) => (
            <div key={i} className="py-4 border-b border-border flex gap-4 text-sm">
              <span className="font-bold text-charcoal min-w-[40px]">{item.time}</span>
              <p className="text-charcoal-light leading-snug">{item.text}</p>
            </div>
          ))}
        </div>
      </section>
    </aside>
  );
}
