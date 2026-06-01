'use client';

import { ARTICLES, HERO_ARTICLE } from '@/lib/mock';
import { useFollows } from '@/hooks/useFollows';
import { ArticleCard } from './ArticleCard';

export function HomeContent() {
  const { follows, isLoaded } = useFollows();

  const displayArticles =
    isLoaded && follows.length > 0
      ? ARTICLES.filter((a) => follows.includes(a.category))
      : ARTICLES;

  const displayHero =
    isLoaded && follows.length > 0 && !follows.includes(HERO_ARTICLE.category)
      ? displayArticles[0] || HERO_ARTICLE
      : HERO_ARTICLE;

  const gridArticles = displayArticles.filter((a) => a.id !== displayHero.id);
  const personalizedLabel = isLoaded && follows.length > 0 ? 'Personalized' : "Editor's Picks";
  const separator = '\u2215\u2215';

  return (
    <div className="flex-1 min-w-0">
      <div className="flex items-center justify-between border-b border-border pb-4 mb-8">
        <h1 className="text-sm font-bold tracking-widest uppercase">
          For You <span className="text-charcoal-light/50 mx-2">{separator}</span> {personalizedLabel}
        </h1>
        <span className="text-xs text-charcoal-light">Updated 2m ago</span>
      </div>

      <div className="mb-12">
        <ArticleCard article={displayHero} featured />
      </div>

      {gridArticles.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-12">
          {gridArticles.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      ) : (
        <div className="py-12 text-center border border-dashed border-border text-charcoal-light">
          <p className="font-serif text-xl mb-2">No recent articles in your followed topics.</p>
          <p className="text-sm">Try following more topics in the sidebar.</p>
        </div>
      )}
    </div>
  );
}
