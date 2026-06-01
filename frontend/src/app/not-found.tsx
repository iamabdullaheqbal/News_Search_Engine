import Link from 'next/link';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-24 text-center">
        <h1 className="font-serif italic text-5xl mb-4">Page not found</h1>
        <p className="text-charcoal-light mb-8">
          This page may have been moved or removed.
        </p>
        <Link
          href="/"
          className="inline-block bg-charcoal text-cream px-6 py-3 text-xs font-bold tracking-widest uppercase hover:bg-charcoal-light transition-colors"
        >
          Return Home
        </Link>
      </main>
      <Footer />
    </div>
  );
}
