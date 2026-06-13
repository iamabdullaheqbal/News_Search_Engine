import Link from 'next/link';
import { Article } from '@/lib/mock';

interface ArticleCardProps {
  article: Article;
  featured?: boolean;
}

export function ArticleCard({ article, featured = false }: ArticleCardProps) {
  const hasImage = article.imageUrl.trim().length > 0;

  if (featured) {
    return (
      <Link href={`/article/${article.id}`} className="block group">
        <article>
          <div className="overflow-hidden mb-4">
            {hasImage ? (
              <img
                src={article.imageUrl}
                alt={article.title}
                className="w-full h-[400px] object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out"
              />
            ) : (
              <div className="w-full h-[400px] bg-cream-dark" aria-hidden="true" />
            )}
          </div>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-xs font-bold tracking-wider uppercase bg-charcoal text-cream px-2 py-1">
              {article.category}
            </span>
            <span className="text-xs text-charcoal-light font-medium">
              {article.source} · {article.readTime}
            </span>
          </div>
          <h2 className="font-serif text-4xl md:text-5xl italic leading-tight mb-4 group-hover:text-charcoal-light transition-colors">
            {article.title}
          </h2>
          {article.dek && (
            <p className="text-lg text-charcoal-light leading-relaxed max-w-3xl">{article.dek}</p>
          )}
        </article>
      </Link>
    );
  }

  return (
    <Link href={`/article/${article.id}`} className="block group h-full">
      <article className="flex flex-col h-full">
        <div className="overflow-hidden mb-3">
          {hasImage ? (
            <img
              src={article.imageUrl}
              alt={article.title}
              className="w-full h-48 object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out"
            />
          ) : (
            <div className="w-full h-48 bg-cream-dark" aria-hidden="true" />
          )}
        </div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xxs font-bold tracking-wider uppercase bg-charcoal text-cream px-1.5 py-0.5">
            {article.category}
          </span>
        </div>
        <h3 className="font-serif text-xl leading-snug mb-2 group-hover:text-charcoal-light transition-colors flex-1">
          {article.title}
        </h3>
        <div className="text-xs text-charcoal-light font-medium mt-auto pt-2 border-t border-border/50">
          {article.source} · {article.timestamp}
        </div>
      </article>
    </Link>
  );
}
