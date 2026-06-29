import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/hooks/useAuth';
import { CategoriesProvider } from '@/hooks/useCategories';

export const metadata: Metadata = {
  title: {
    default: 'Veritas — The Global Record',
    template: '%s | Veritas',
  },
  description: 'Independent journalism for readers who want depth, context, and clarity.',
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function fetchCategories(): Promise<string[]> {
  try {
    const res = await fetch(`${API_BASE}/api/articles/categories`, {
      next: { revalidate: 3600 }, // re-fetch at most once per hour
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const categories = await fetchCategories();

  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <CategoriesProvider categories={categories}>
            {children}
          </CategoriesProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
