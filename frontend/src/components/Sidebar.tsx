'use client';

import { TRENDING, LIVE_WIRE, CATEGORIES } from '@/lib/mock';
import { useFollows } from '@/hooks/useFollows';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const { follows, toggleFollow, isLoaded } = useFollows();

  return (
    <aside className="w-full lg:w-80 flex-shrink-0 space-y-12">
      {/* Trending Now */}
      <section>
        <h3 className="text-xs font-bold tracking-wider uppercase mb-6">Trending Now</h3>
        <div className="space-y-5">
          {TRENDING.map((title, i) => (
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
        <p className="text-sm text-charcoal-light mb-6 leading-relaxed">
          Tap a topic to personalize your feed. We store this in a cookie on your device — nothing leaves the browser.
        </p>
        {isLoaded && (
          <div className="flex flex-wrap gap-2">
            {CATEGORIES.map((category) => {
              const isFollowing = follows.includes(category);
              return (
                <button
                  key={category}
                  onClick={() => toggleFollow(category)}
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
        )}
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
