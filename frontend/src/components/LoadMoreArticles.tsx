'use client';

import { useState, useTransition } from 'react';
import { getArticlesByCategory, toCardArticle, Article } from '@/lib/api';
import { ArticleCard } from './ArticleCard';

interface Props {
  category: string;
  initialArticles: Article[];
  total: number;
  pageSize?: number;
}

export function LoadMoreArticles({ category, initialArticles, total, pageSize = 20 }: Props) {
  const [articles, setArticles] = useState<Article[]>(initialArticles);
  // nextOffset tracks the real DB offset for the next fetch.
  // The server already fetched page 0 (offset 0..pageSize-1), so start at pageSize.
  const [nextOffset, setNextOffset] = useState(pageSize);
  const [isPending, startTransition] = useTransition();

  const displayedTotal = articles.length + 1; // +1 for the featured hero rendered above
  const hasMore = displayedTotal < total;

  const loadMore = () => {
    startTransition(async () => {
      try {
        const res = await getArticlesByCategory(category, pageSize, nextOffset);
        setArticles((prev) => [...prev, ...res.articles]);
        setNextOffset((prev) => prev + pageSize);
      } catch {
        // silently fail — user can retry
      }
    });
  };

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-12">
        {articles.map((article) => (
          <ArticleCard key={article.id} article={toCardArticle(article)} />
        ))}
      </div>

      {hasMore && (
        <div className="flex justify-center mt-12">
          <button
            onClick={loadMore}
            disabled={isPending}
            className="px-8 py-3 border border-charcoal text-xs font-bold tracking-widest uppercase hover:bg-charcoal hover:text-cream transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isPending ? 'Loading…' : `Load More  (${displayedTotal} of ${total})`}
          </button>
        </div>
      )}
    </>
  );
}
