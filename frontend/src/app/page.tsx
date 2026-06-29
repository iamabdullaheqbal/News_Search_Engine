import type { Metadata } from 'next';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Sidebar } from '@/components/Sidebar';
import { HomeContent } from '@/components/HomeContent';

export const metadata: Metadata = {
  title: 'Veritas — The Global Record',
  description: 'Independent journalism for readers who want depth, context, and clarity.',
};

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <div className="flex flex-col lg:flex-row gap-12 lg:gap-16">
          <HomeContent />
          <Sidebar />
        </div>
      </main>
      <Footer />
    </div>
  );
}
