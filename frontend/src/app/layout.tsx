import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Veritas — The Global Record',
  description: 'Independent journalism for readers who want depth, context, and clarity.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
