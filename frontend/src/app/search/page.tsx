import { Suspense } from 'react';
import type { Metadata } from 'next';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { SearchResults } from '@/components/SearchResults';

export async function generateMetadata(
  { searchParams }: { searchParams: Promise<{ q?: string }> }
): Promise<Metadata> {
  const { q } = await searchParams;
  if (q?.trim()) {
    return {
      title: `"${q.trim()}"`,
      description: `Search results for "${q.trim()}" on Veritas.`,
    };
  }
  return {
    title: 'Search',
    description: 'Search across every section of the global record.',
  };
}

export default function SearchPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <Suspense fallback={<div className="flex-1" />}>
        <SearchResults />
      </Suspense>
      <Footer />
    </div>
  );
}
