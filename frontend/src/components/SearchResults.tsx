'use client';

import { useEffect, useState, Fragment } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Search, X } from 'lucide-react';
import Link from 'next/link';
import { ALL_ARTICLES, CATEGORIES, Article } from '@/lib/mock';
import { cn } from '@/lib/utils';

type TimeFilter = 'any' | 'today' | 'week' | 'month';

export function SearchResults() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialQuery = searchParams.get('q') || '';
  const [query, setQuery] = useState(initialQuery);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>('any');

  useEffect(() => {
    setQuery(searchParams.get('q') || '');
  }, [searchParams]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const matchTime = (article: Article): boolean => {
    if (timeFilter === 'any') return true;
    if (timeFilter === 'today')
      return article.timestamp.includes('hour') || article.timestamp.includes('minute');
    if (timeFilter === 'week')
      return article.timestamp.includes('hour') || article.timestamp.includes('day');
    return true;
  };

  const allMatches = initialQuery
    ? ALL_ARTICLES.filter((a) => {
        const q = initialQuery.toLowerCase();
        return (
          a.title.toLowerCase().includes(q) ||
          a.category.toLowerCase().includes(q) ||
          (a.dek && a.dek.toLowerCase().includes(q)) ||
          a.source.toLowerCase().includes(q)
        );
      })
    : [];

  const results = allMatches.filter(
    (a) => (!activeCategory || a.category === activeCategory) && matchTime(a)
  );

  const highlight = (text: string): React.ReactNode => {
    if (!initialQuery) return text;
    const regex = new RegExp(`(${initialQuery})`, 'gi');
    const parts = text.split(regex);
    return parts.map((part, i) =>
      part.toLowerCase() === initialQuery.toLowerCase() ? (
        <mark key={i} className="bg-yellow-200/60 text-charcoal px-0.5">
          {part}
        </mark>
      ) : (
        <Fragment key={i}>{part}</Fragment>
      )
    );
  };

  return (
    <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 md:py-12">
      <div className="mb-8">
        <p className="text-xs font-bold tracking-widest uppercase text-charcoal-light mb-3">Search</p>
        <form
          onSubmit={handleSubmit}
          className="flex items-center border-b-2 border-charcoal pb-3 mb-2"
        >
          <Search className="w-6 h-6 text-charcoal-light mr-3" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search the global record..."
            className="flex-1 bg-transparent border-none outline-none font-serif italic text-3xl md:text-4xl text-charcoal placeholder:text-charcoal-light/40"
          />
          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('');
                router.push('/search');
              }}
              className="p-2 hover:bg-border rounded-md text-charcoal-light transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </form>

        {initialQuery && (
          <p className="text-sm text-charcoal-light">
            {results.length} result{results.length !== 1 ? 's' : ''} for{' '}
            <span className="font-medium text-charcoal">&ldquo;{initialQuery}&rdquo;</span>
          </p>
        )}
      </div>

      {initialQuery && (
        <>
          <div className="border-b border-border pb-6 mb-8 space-y-4">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-xxs font-bold tracking-widest uppercase text-charcoal-light mr-2">
                Section:
              </span>
              <button
                onClick={() => setActiveCategory(null)}
                className={cn(
                  'px-3 py-1 text-xs font-bold tracking-wider uppercase transition-all',
                  !activeCategory
                    ? 'bg-charcoal text-cream'
                    : 'bg-transparent text-charcoal border border-border hover:border-charcoal-light'
                )}
              >
                All
              </button>
              {CATEGORIES.map((c) => (
                <button
                  key={c}
                  onClick={() => setActiveCategory(activeCategory === c ? null : c)}
                  className={cn(
                    'px-3 py-1 text-xs font-bold tracking-wider uppercase transition-all',
                    activeCategory === c
                      ? 'bg-charcoal text-cream'
                      : 'bg-transparent text-charcoal border border-border hover:border-charcoal-light'
                  )}
                >
                  {c}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-xxs font-bold tracking-widest uppercase text-charcoal-light mr-2">
                Time:
              </span>
              {(['any', 'today', 'week', 'month'] as TimeFilter[]).map((t) => (
                <button
                  key={t}
                  onClick={() => setTimeFilter(t)}
                  className={cn(
                    'px-3 py-1 text-xs font-bold tracking-wider uppercase transition-all',
                    timeFilter === t
                      ? 'bg-charcoal text-cream'
                      : 'bg-transparent text-charcoal border border-border hover:border-charcoal-light'
                  )}
                >
                  {t === 'any' ? 'Any time' : `Past ${t}`}
                </button>
              ))}
            </div>
          </div>

          {results.length === 0 ? (
            <div className="py-20 text-center">
              <p className="font-serif italic text-3xl mb-3">No matches found.</p>
              <p className="text-charcoal-light mb-8">Try a broader query or remove some filters.</p>
            </div>
          ) : (
            <div className="space-y-10">
              {results.map((article) => (
                <Link
                  key={article.id}
                  href={`/article/${article.id}`}
                  className="flex flex-col md:flex-row gap-6 group pb-10 border-b border-border last:border-b-0"
                >
                  <div className="md:w-64 flex-shrink-0 overflow-hidden">
                    <img
                      src={article.imageUrl}
                      alt={article.title}
                      className="w-full h-48 md:h-40 object-cover transform group-hover:scale-105 transition-transform duration-700"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-xxs font-bold tracking-wider uppercase bg-charcoal text-cream px-1.5 py-0.5">
                        {article.category}
                      </span>
                      <span className="text-xs text-charcoal-light">
                        {article.source} · {article.timestamp}
                      </span>
                    </div>
                    <h2 className="font-serif text-2xl md:text-3xl leading-tight mb-2 group-hover:text-charcoal-light transition-colors">
                      {highlight(article.title)}
                    </h2>
                    {article.dek && (
                      <p className="text-charcoal-light leading-relaxed">{highlight(article.dek)}</p>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </>
      )}

      {!initialQuery && (
        <div className="py-20 text-center">
          <p className="font-serif italic text-3xl mb-3">What would you like to know?</p>
          <p className="text-charcoal-light">Search across every section of the global record.</p>
        </div>
      )}
    </main>
  );
}
