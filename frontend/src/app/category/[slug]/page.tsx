import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Sidebar } from '@/components/Sidebar';
import { ArticleCard } from '@/components/ArticleCard';
import { CATEGORIES, getArticlesByCategory } from '@/lib/mock';

const CATEGORY_TAGLINES: Record<string, string> = {
  POLITICS: 'Power, policy, and the people who shape them.',
  ECONOMY: 'Capital, labor, and the forces driving global growth.',
  TECH: 'The companies and ideas redefining how we work and live.',
  CLIMATE: 'The science, policy, and economics of a changing planet.',
  CULTURE: 'Art, ideas, and the texture of contemporary life.',
  SCIENCE: 'Discoveries, breakthroughs, and the frontiers of knowledge.',
  MARKETS: 'Equities, bonds, currencies — the daily ledger.',
};

export function generateStaticParams() {
  return CATEGORIES.map((c) => ({ slug: c.toLowerCase() }));
}

export default async function CategoryPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const category = slug.toUpperCase();
  if (!CATEGORIES.includes(category)) notFound();

  const articles = getArticlesByCategory(category);
  const tagline = CATEGORY_TAGLINES[category] || '';
  const featured = articles[0];
  const rest = articles.slice(1);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <div className="border-b border-charcoal pb-6 mb-12">
          <p className="text-xs font-bold tracking-widest uppercase text-charcoal-light mb-3">Section</p>
          <h1 className="font-serif text-6xl md:text-7xl italic leading-none mb-4">
            {category.charAt(0) + category.slice(1).toLowerCase()}
          </h1>
          <p className="text-lg text-charcoal-light max-w-2xl">{tagline}</p>
        </div>

        <div className="flex flex-col lg:flex-row gap-12 lg:gap-16">
          <div className="flex-1 min-w-0">
            {articles.length === 0 ? (
              <div className="py-24 text-center border border-dashed border-border text-charcoal-light">
                <p className="font-serif text-2xl mb-2">No stories in this section yet.</p>
                <p className="text-sm">Check back soon.</p>
              </div>
            ) : (
              <>
                {featured && (
                  <div className="mb-12">
                    <ArticleCard article={featured} featured />
                  </div>
                )}
                {rest.length > 0 && (
                  <>
                    <h2 className="text-xs font-bold tracking-widest uppercase border-b border-border pb-3 mb-8">
                      More in {category.toLowerCase()}
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-12">
                      {rest.map((article) => (
                        <ArticleCard key={article.id} article={article} />
                      ))}
                    </div>
                  </>
                )}
              </>
            )}
          </div>
          <Sidebar />
        </div>
      </main>
      <Footer />
    </div>
  );
}
