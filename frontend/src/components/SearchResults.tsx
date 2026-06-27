'use client';

import { useEffect, useState, Fragment, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Search, X } from 'lucide-react';
import Link from 'next/link';
import { useCategories } from '@/hooks/useCategories';
import { searchArticles, Article } from '@/lib/api';
import { cn } from '@/lib/utils';

type TimeFilter = 'any' | 'today' | 'week' | 'month';

export function SearchResults() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const categories = useCategories();
  const initialQuery = searchParams.get('q') || '';
  const [query, setQuery] = useState(initialQuery);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>('any');
  const [results, setResults] = useState<Article[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const nextQuery = searchParams.get('q') || '';
    queueMicrotask(() => {
      setQuery(nextQuery);
      setActiveCategory(null);
    });
  }, [searchParams]);

  const doSearch = useCallback(async (q: string, cat: string | null) => {
    if (!q.trim()) return;
    setLoading(true);
    try {
      const res = await searchArticles(q, cat ?? undefined, 50);
      setResults(res.results);
      setTotal(res.total);
    } catch {
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    queueMicrotask(() => {
      if (initialQuery) doSearch(initialQuery, activeCategory);
      else { setResults([]); setTotal(0); }
    });
  }, [initialQuery, activeCategory, doSearch]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const matchTime = (article: Article): boolean => {
    if (timeFilter === 'any') return true;
    const ts = article.timestamp ?? '';
    if (timeFilter === 'today') return ts.includes('hour') || ts.includes('minute');
    if (timeFilter === 'week') return ts.includes('hour') || ts.includes('day');
    return true;
  };

  const displayed = results.filter(matchTime);

  const highlight = (text: string): React.ReactNode => {
    if (!initialQuery) return text;
    const regex = new RegExp(`(${initialQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    return parts.map((part, i) =>
      part.toLowerCase() === initialQuery.toLowerCase() ? (
        <mark key={i} className="bg-yellow-200/60 text-charcoal px-0.5">{part}</mark>
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
          <Search className="w-5 h-5 sm:w-6 sm:h-6 text-charcoal-light mr-2 sm:mr-3 flex-shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search the global record..."
            className="min-w-0 flex-1 bg-transparent border-none outline-none font-serif italic text-2xl sm:text-3xl md:text-4xl text-charcoal placeholder:text-charcoal-light/40"
          />
          {query && (
            <button
              type="button"
              onClick={() => { setQuery(''); router.push('/search'); }}
              className="p-2 hover:bg-border rounded-md text-charcoal-light transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </form>

        {initialQuery && !loading && (
          <p className="text-sm text-charcoal-light">
            {displayed.length} result{displayed.length !== 1 ? 's' : ''} for{' '}
            <span className="font-medium text-charcoal">&ldquo;{initialQuery}&rdquo;</span>
          </p>
        )}
      </div>

      {initialQuery && (
        <>
          <div className="border-b border-border pb-6 mb-8 space-y-4">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-xxs font-bold tracking-widest uppercase text-charcoal-light mr-2">Section:</span>
              <button
                onClick={() => setActiveCategory(null)}
                className={cn(
                  'px-3 py-1 text-xs font-bold tracking-wider uppercase transition-all',
                  !activeCategory ? 'bg-charcoal text-cream' : 'bg-transparent text-charcoal border border-border hover:border-charcoal-light'
                )}
              >All</button>
              {categories.map((c) => (
                <button
                  key={c}
                  onClick={() => setActiveCategory(activeCategory === c ? null : c)}
                  className={cn(
                    'px-3 py-1 text-xs font-bold tracking-wider uppercase transition-all',
                    activeCategory === c ? 'bg-charcoal text-cream' : 'bg-transparent text-charcoal border border-border hover:border-charcoal-light'
                  )}
                >{c}</button>
              ))}
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-xxs font-bold tracking-widest uppercase text-charcoal-light mr-2">Time:</span>
              {(['any', 'today', 'week', 'month'] as TimeFilter[]).map((t) => (
                <button
                  key={t}
                  onClick={() => setTimeFilter(t)}
                  className={cn(
                    'px-3 py-1 text-xs font-bold tracking-wider uppercase transition-all',
                    timeFilter === t ? 'bg-charcoal text-cream' : 'bg-transparent text-charcoal border border-border hover:border-charcoal-light'
                  )}
                >{t === 'any' ? 'Any time' : `Past ${t}`}</button>
              ))}
            </div>
          </div>

          {loading ? (
            <div className="space-y-8 animate-pulse">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex flex-col sm:flex-row gap-6 pb-10 border-b border-border">
                  <div className="w-full sm:w-64 h-40 bg-cream-dark/40 rounded flex-shrink-0" />
                  <div className="flex-1 space-y-3">
                    <div className="h-4 bg-cream-dark/40 rounded w-1/4" />
                    <div className="h-8 bg-cream-dark/40 rounded" />
                    <div className="h-4 bg-cream-dark/40 rounded w-3/4" />
                  </div>
                </div>
              ))}
            </div>
          ) : displayed.length === 0 ? (
            <div className="py-20 text-center">
              <p className="font-serif italic text-3xl mb-3">No matches found.</p>
              <p className="text-charcoal-light mb-8">Try a broader query or remove some filters.</p>
            </div>
          ) : (
            <div className="space-y-10">
              {displayed.map((article) => (
                <Link
                  key={article.id}
                  href={`/article/${article.id}`}
                  className="flex flex-col md:flex-row gap-6 group pb-10 border-b border-border last:border-b-0"
                >
                  {article.image_url && (
                    <div className="md:w-64 flex-shrink-0 overflow-hidden">
                      <img
                        src={article.image_url}
                        alt={article.title}
                        className="w-full h-48 md:h-40 object-cover transform group-hover:scale-105 transition-transform duration-700"
                      />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
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
