import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft, Link as LinkIcon, Bookmark } from 'lucide-react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { ArticleCard } from '@/components/ArticleCard';
import type { Article, ArticleDetail } from '@/lib/api';

const Twitter = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z" />
  </svg>
);

const Facebook = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" />
  </svg>
);

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function fetchArticle(id: string): Promise<ArticleDetail | null> {
  try {
    const res = await fetch(`${BASE}/api/articles/${id}`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function fetchRelated(category: string, currentId: string) {
  try {
    const res = await fetch(`${BASE}/api/articles/category/${category}?limit=4`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return [];
    const articles = await res.json();
    return articles.filter((a: { id: string }) => a.id !== currentId).slice(0, 3);
  } catch {
    return [];
  }
}

export default async function ArticleDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const article = await fetchArticle(id);
  if (!article) notFound();

  const related = await fetchRelated(article.category, article.id);

  const toCardArticle = (a: typeof related[number]) => ({
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
  });

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <article>
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 md:pt-12">
            <Link
              href={`/category/${article.category.toLowerCase()}`}
              className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-charcoal-light hover:text-charcoal mb-6 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              {article.category}
            </Link>

            <h1 className="font-serif text-3xl sm:text-4xl md:text-6xl italic leading-tight mb-6">
              {article.title}
            </h1>

            {article.dek && (
              <p className="font-serif text-lg sm:text-xl md:text-2xl text-charcoal-light leading-relaxed mb-8">
                {article.dek}
              </p>
            )}

            <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center sm:justify-between gap-4 py-5 border-t border-b border-border mb-10 text-sm">
              <div className="flex min-w-0 items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-charcoal text-cream flex items-center justify-center font-serif italic text-lg">
                  {(article.author || article.source).charAt(0)}
                </div>
                <div className="min-w-0">
                  <p className="font-bold">{article.author || article.source}</p>
                  <p className="text-xs text-charcoal-light">
                    {article.published_at
                      ? new Date(article.published_at).toLocaleDateString('en-US', {
                          year: 'numeric', month: 'long', day: 'numeric',
                        })
                      : article.timestamp} · {article.read_time}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-charcoal-light">
                <button aria-label="Share on Twitter" className="p-2 hover:bg-border rounded transition-colors">
                  <Twitter className="w-4 h-4" />
                </button>
                <button aria-label="Share on Facebook" className="p-2 hover:bg-border rounded transition-colors">
                  <Facebook className="w-4 h-4" />
                </button>
                <button aria-label="Copy link" className="p-2 hover:bg-border rounded transition-colors">
                  <LinkIcon className="w-4 h-4" />
                </button>
                <span className="w-px h-5 bg-border mx-1" />
                <button aria-label="Save article" className="p-2 hover:bg-border rounded transition-colors">
                  <Bookmark className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {article.image_url && (
            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mb-12">
              <figure>
                <img
                  src={article.image_url}
                  alt={article.title}
                  className="w-full h-auto max-h-[600px] object-cover"
                />
                <figcaption className="text-xs text-charcoal-light mt-3 italic">
                  Photograph for Veritas
                </figcaption>
              </figure>
            </div>
          )}

          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
            {article.body && article.body.length > 0 && (
              <div className="space-y-6 font-serif text-lg md:text-xl leading-relaxed text-charcoal">
                {article.body.map((paragraph, i) => (
                  <p
                    key={i}
                    className={
                      i === 0
                        ? 'first-letter:font-bold first-letter:text-6xl first-letter:font-serif first-letter:mr-2 first-letter:float-left first-letter:leading-none first-letter:mt-1'
                        : ''
                    }
                  >
                    {paragraph}
                  </p>
                ))}
              </div>
            )}

            <div className="flex items-center justify-center my-12">
              <div className="w-2 h-2 bg-charcoal" />
            </div>

            {article.author && (
              <div className="border-t border-b border-border py-8 flex flex-col sm:flex-row gap-5 items-start">
                <div className="w-14 h-14 rounded-full bg-charcoal text-cream flex items-center justify-center font-serif italic text-2xl flex-shrink-0">
                  {article.author.charAt(0)}
                </div>
                <div>
                  <p className="text-xxs font-bold tracking-widest uppercase text-charcoal-light mb-1">
                    By the author
                  </p>
                  <h3 className="font-serif text-2xl mb-2">{article.author}</h3>
                  <p className="text-sm text-charcoal-light leading-relaxed">
                    {article.author} is a correspondent for {article.source}, covering{' '}
                    {article.category.toLowerCase()} and adjacent beats.
                  </p>
                </div>
              </div>
            )}
          </div>
        </article>

        {related.length > 0 && (
          <section className="bg-cream-dark/40 border-t border-border py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <h2 className="text-xs font-bold tracking-widest uppercase border-b border-charcoal pb-3 mb-8">
                More in {article.category.toLowerCase()}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-x-8 gap-y-12">
                {related.map((r: Article) => (
                  <ArticleCard key={r.id} article={toCardArticle(r)} />
                ))}
              </div>
            </div>
          </section>
        )}
      </main>
      <Footer />
    </div>
  );
}
