'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { Search, X, Clock, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useKeyboardShortcut } from '@/hooks/useKeyboardShortcut';
import { searchArticles, Article } from '@/lib/api';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const RECENT_SEARCHES = ['Interest rates', 'Silicon valley', 'Climate summit'];

export function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Article[]>([]);
  const [searching, setSearching] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useKeyboardShortcut('Escape', onClose, false);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 10);
    } else {
      setQuery('');
      setResults([]);
    }
  }, [isOpen]);

  const doSearch = useCallback((q: string) => {
    if (!q.trim()) { setResults([]); return; }
    setSearching(true);
    searchArticles(q, undefined, 5)
      .then((res) => setResults(res.results))
      .catch(() => setResults([]))
      .finally(() => setSearching(false));
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(query), 300);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query, doSearch]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] sm:pt-[20vh] px-4">
      <div
        className="fixed inset-0 bg-cream/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="relative w-full max-w-2xl bg-cream border border-border shadow-2xl rounded-lg overflow-hidden flex flex-col max-h-[80vh]">
        <form
          onSubmit={handleSubmit}
          className="flex items-center px-4 py-3 border-b border-border"
        >
          <Search className="w-5 h-5 text-charcoal-light mr-3" />
          <input
            ref={inputRef}
            type="text"
            className="flex-1 bg-transparent border-none outline-none text-lg text-charcoal placeholder:text-charcoal-light/50 font-sans"
            placeholder="Search the global record..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            type="button"
            onClick={onClose}
            className="p-1 hover:bg-border rounded-md text-charcoal-light transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </form>

        <div className="overflow-y-auto flex-1 p-2">
          {query === '' ? (
            <div className="p-4 text-sm text-charcoal-light">
              <div className="flex items-center mb-3">
                <Clock className="w-4 h-4 mr-2" />
                <span className="font-medium tracking-wider text-xs uppercase">Recent Searches</span>
              </div>
              <div className="space-y-1">
                {RECENT_SEARCHES.map((term) => (
                  <button
                    key={term}
                    className="w-full text-left px-3 py-2 rounded-md hover:bg-border/50 transition-colors flex items-center justify-between group"
                    onClick={() => setQuery(term)}
                  >
                    <span>{term}</span>
                    <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            </div>
          ) : searching ? (
            <div className="p-8 text-center text-charcoal-light text-sm">Searching…</div>
          ) : results.length > 0 ? (
            <div className="py-2">
              {results.map((article) => (
                <Link
                  key={article.id}
                  href={`/article/${article.id}`}
                  onClick={onClose}
                  className="w-full text-left px-4 py-3 hover:bg-border/50 transition-colors flex items-start gap-4 group"
                >
                  {article.image_url && (
                    <img
                      src={article.image_url}
                      alt={article.title}
                      className="w-16 h-16 object-cover rounded"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xxs font-bold tracking-wider uppercase bg-charcoal text-cream px-1.5 py-0.5">
                        {article.category}
                      </span>
                      <span className="text-xs text-charcoal-light">{article.source}</span>
                    </div>
                    <h4 className="font-serif text-lg leading-tight group-hover:text-accent transition-colors truncate">
                      {article.title}
                    </h4>
                  </div>
                </Link>
              ))}
              <button
                onClick={handleSubmit}
                className="w-full text-left px-4 py-3 border-t border-border hover:bg-border/50 transition-colors flex items-center justify-between text-sm"
              >
                <span>
                  See all results for <strong>&ldquo;{query}&rdquo;</strong>
                </span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="p-8 text-center text-charcoal-light">
              No results found for &ldquo;{query}&rdquo;
            </div>
          )}
        </div>

        <div className="px-4 py-2 border-t border-border bg-cream-dark/30 text-xs text-charcoal-light flex justify-between items-center">
          <span>Search powered by Veritas</span>
          <span className="flex items-center gap-1">
            <kbd className="px-1.5 py-0.5 bg-border rounded text-xxs font-mono">ESC</kbd>
            to close
          </span>
        </div>
      </div>
    </div>
  );
}
