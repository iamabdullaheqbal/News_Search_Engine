import { Suspense } from 'react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { SearchResults } from '@/components/SearchResults';

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
