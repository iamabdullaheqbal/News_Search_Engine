import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft, Twitter, Facebook, Link as LinkIcon, Bookmark } from 'lucide-react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { ArticleCard } from '@/components/ArticleCard';
import { ALL_ARTICLES, getArticleById, getRelatedArticles } from '@/lib/mock';

export function generateStaticParams() {
  return ALL_ARTICLES.map((a) => ({ id: a.id }));
}

export default async function ArticleDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const article = getArticleById(id);
  if (!article) notFound();

  const related = getRelatedArticles(article);

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

            <h1 className="font-serif text-4xl md:text-6xl italic leading-tight mb-6">
              {article.title}
            </h1>

            {article.dek && (
              <p className="font-serif text-xl md:text-2xl text-charcoal-light leading-relaxed mb-8">
                {article.dek}
              </p>
            )}

            <div className="flex flex-wrap items-center justify-between gap-4 py-5 border-t border-b border-border mb-10 text-sm">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-charcoal text-cream flex items-center justify-center font-serif italic text-lg">
                  {(article.author || article.source).charAt(0)}
                </div>
                <div>
                  <p className="font-bold">{article.author || article.source}</p>
                  <p className="text-xs text-charcoal-light">
                    {article.publishedAt || article.timestamp} · {article.readTime}
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

          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mb-12">
            <figure>
              <img
                src={article.imageUrl}
                alt={article.title}
                className="w-full h-auto max-h-[600px] object-cover"
              />
              <figcaption className="text-xs text-charcoal-light mt-3 italic">
                Photograph for Veritas
              </figcaption>
            </figure>
          </div>

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
              <div className="border-t border-b border-border py-8 flex gap-5 items-start">
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
                    {article.category.toLowerCase()} and adjacent beats. They have reported from
                    twelve countries over the past decade.
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
                {related.map((r) => (
                  <ArticleCard key={r.id} article={r} />
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
