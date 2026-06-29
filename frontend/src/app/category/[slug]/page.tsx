import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Sidebar } from '@/components/Sidebar';
import { ArticleCard } from '@/components/ArticleCard';
import { LoadMoreArticles } from '@/components/LoadMoreArticles';
import { CATEGORY_TAGLINES, toCardArticle, Article, CategoryResponse } from '@/lib/api';

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
const PAGE_SIZE = 20;

async function fetchCategories(): Promise<string[]> {
  try {
    const res = await fetch(`${BASE}/api/articles/categories`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

async function fetchCategoryPage(category: string, offset = 0): Promise<CategoryResponse> {
  try {
    const res = await fetch(
      `${BASE}/api/articles/category/${category}?limit=${PAGE_SIZE}&offset=${offset}`,
      { next: { revalidate: 60 } }
    );
    if (!res.ok) return { total: 0, articles: [], limit: PAGE_SIZE, offset };
    return res.json();
  } catch {
    return { total: 0, articles: [], limit: PAGE_SIZE, offset };
  }
}

export const dynamic = 'force-dynamic';

export async function generateMetadata(
  { params }: { params: Promise<{ slug: string }> }
): Promise<Metadata> {
  const { slug } = await params;
  const category = slug.toUpperCase();
  const label = category.charAt(0) + category.slice(1).toLowerCase();
  const tagline = CATEGORY_TAGLINES[category] ?? '';
  return {
    title: label,
    description: tagline || `Latest ${label} news on Veritas.`,
  };
}

export default async function CategoryPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const category = slug.toUpperCase();

  const validCategories = await fetchCategories();
  if (!validCategories.includes(category)) notFound();

  const { articles, total } = await fetchCategoryPage(category);

  const tagline = CATEGORY_TAGLINES[category] ?? '';
  const featured = articles[0] as Article | undefined;
  const rest = articles.slice(1);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <div className="border-b border-charcoal pb-6 mb-8 md:mb-12">
          <p className="text-xs font-bold tracking-widest uppercase text-charcoal-light mb-3">Section</p>
          <h1 className="font-serif text-5xl sm:text-6xl md:text-7xl italic leading-none mb-4">
            {category.charAt(0) + category.slice(1).toLowerCase()}
          </h1>
          {tagline && (
            <p className="text-lg text-charcoal-light max-w-2xl">{tagline}</p>
          )}
          <p className="text-xs text-charcoal-light mt-3">
            {total.toLocaleString()} {total === 1 ? 'story' : 'stories'}
          </p>
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
                    <ArticleCard article={toCardArticle(featured)} featured />
                  </div>
                )}
                {rest.length > 0 && (
                  <>
                    <h2 className="text-xs font-bold tracking-widest uppercase border-b border-border pb-3 mb-8">
                      More in {category.toLowerCase()}
                    </h2>
                    {/* LoadMoreArticles is a client component that handles pagination */}
                    <LoadMoreArticles
                      category={category}
                      initialArticles={rest}
                      total={total}
                      pageSize={PAGE_SIZE}
                    />
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
