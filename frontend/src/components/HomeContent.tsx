'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { getFeed, Article } from '@/lib/api';
import { ArticleCard } from './ArticleCard';

// Adapter: map API Article to the shape ArticleCard expects
function toCardArticle(a: Article) {
  return {
    id: a.id,
    title: a.title,
    dek: a.dek,
    category: a.category,
    source: a.source,
    author: a.author,
    readTime: a.read_time ?? '',
    imageUrl: a.image_url ?? '',
    timestamp: a.timestamp ?? '',
    publishedAt: a.published_at,
  };
}

export function HomeContent() {
  const { user, loading: authLoading } = useAuth();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatedAt, setUpdatedAt] = useState('');

  useEffect(() => {
    if (authLoading) return; // wait for auth to resolve before fetching
    setLoading(true);
    getFeed(20)
      .then((data) => {
        setArticles(data);
        setUpdatedAt(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [authLoading, user]); // refetch when auth state changes

  const separator = '\u2215\u2215';
  const isPersonalized = !!(user?.interests?.length);
  const personalizedLabel = isPersonalized ? 'Personalized' : "Editor's Picks";

  const hero = articles[0];
  const gridArticles = articles.slice(1);

  return (
    <div className="flex-1 min-w-0">
      <div className="flex items-center justify-between border-b border-border pb-4 mb-8">
        <h1 className="text-sm font-bold tracking-widest uppercase">
          For You <span className="text-charcoal-light/50 mx-2">{separator}</span> {personalizedLabel}
        </h1>
        {updatedAt && <span className="text-xs text-charcoal-light">Updated {updatedAt}</span>}
      </div>

      {loading ? (
        <div className="space-y-8 animate-pulse">
          <div className="h-96 bg-cream-dark/40 rounded" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-48 bg-cream-dark/40 rounded" />
            ))}
          </div>
        </div>
      ) : articles.length === 0 ? (
        <div className="py-12 text-center border border-dashed border-border text-charcoal-light">
          <p className="font-serif text-xl mb-2">No recent articles in your followed topics.</p>
          <p className="text-sm">Try following more topics in the sidebar.</p>
        </div>
      ) : (
        <>
          {hero && (
            <div className="mb-12">
              <ArticleCard article={toCardArticle(hero)} featured />
            </div>
          )}
          {gridArticles.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-12">
              {gridArticles.map((article) => (
                <ArticleCard key={article.id} article={toCardArticle(article)} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
