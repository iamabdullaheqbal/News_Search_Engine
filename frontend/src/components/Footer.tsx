'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { useCategories } from '@/hooks/useCategories';

const Twitter = (props: React.SVGProps<SVGSVGElement>) => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"/></svg>;
const Facebook = (props: React.SVGProps<SVGSVGElement>) => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>;
const Instagram = (props: React.SVGProps<SVGSVGElement>) => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>;
const Linkedin = (props: React.SVGProps<SVGSVGElement>) => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>;
const Youtube = (props: React.SVGProps<SVGSVGElement>) => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33 2.78 2.78 0 0 0 1.94 2c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.33 29 29 0 0 0-.46-5.33z"/><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/></svg>;

export function Footer() {
  const categories = useCategories();
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.trim()) {
      setSubmitted(true);
      setTimeout(() => {
        setSubmitted(false);
        setEmail('');
      }, 3000);
    }
  };

  const company = ['About Veritas', 'Newsroom', 'Careers', 'Press', 'Contact'];
  const legal = ['Terms of Service', 'Privacy Policy', 'Cookie Settings', 'Accessibility', 'Editorial Standards'];

  return (
    <footer className="bg-charcoal text-cream mt-24">
      <div className="border-b border-cream/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div>
            <h2 className="font-serif italic text-3xl md:text-4xl leading-tight mb-2">
              The morning briefing, delivered.
            </h2>
            <p className="text-cream/60 text-sm leading-relaxed max-w-md">
              Sharp analysis on markets, policy, and culture — in your inbox before 7am, every weekday.
            </p>
          </div>
          <form onSubmit={handleSubmit} className="flex w-full md:justify-end">
            <div className="flex w-full max-w-md flex-col sm:flex-row border border-cream/20 bg-charcoal-light/30 focus-within:border-cream/60 transition-colors">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="min-w-0 flex-1 bg-transparent px-4 py-3 text-sm placeholder:text-cream/40 text-cream outline-none"
                aria-label="Email address"
              />
              <button
                type="submit"
                className="px-5 py-3 sm:py-0 bg-cream text-charcoal text-xs font-bold tracking-widest uppercase hover:bg-cream/80 transition-colors flex items-center justify-center gap-2"
              >
                {submitted ? 'Subscribed' : 'Subscribe'}
                {!submitted && <ArrowRight className="w-3.5 h-3.5" />}
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-10">
          <div className="col-span-2 lg:col-span-2">
            <Link href="/" className="font-serif italic text-4xl font-medium tracking-tight inline-block mb-4">
              Veritas
            </Link>
            <p className="text-cream/60 text-sm leading-relaxed max-w-sm mb-6">
              The global record — independent journalism for readers who want depth, context, and clarity.
            </p>
            <div className="flex items-center gap-4 text-cream/60">
              {[Twitter, Facebook, Instagram, Linkedin, Youtube].map((Icon, i) => (
                <a key={i} href="#" aria-label="Social link" className="hover:text-cream transition-colors">
                  <Icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-xxs font-bold tracking-widest uppercase mb-4 text-cream/40">Sections</h4>
            <ul className="space-y-2.5 text-sm">
              {categories.map((c) => (
                <li key={c}>
                  <Link
                    href={`/category/${c.toLowerCase()}`}
                    className="text-cream/80 hover:text-cream transition-colors capitalize"
                  >
                    {c.toLowerCase()}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-xxs font-bold tracking-widest uppercase mb-4 text-cream/40">Company</h4>
            <ul className="space-y-2.5 text-sm">
              {company.map((item) => (
                <li key={item}>
                  <a href="#" className="text-cream/80 hover:text-cream transition-colors">{item}</a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-xxs font-bold tracking-widest uppercase mb-4 text-cream/40">Legal</h4>
            <ul className="space-y-2.5 text-sm">
              {legal.map((item) => (
                <li key={item}>
                  <a href="#" className="text-cream/80 hover:text-cream transition-colors">{item}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="border-t border-cream/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-cream/50">
          <p>© {new Date().getFullYear()} Veritas Media Group. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span>Made for serious readers.</span>
            <span className="hidden md:inline">EN · US Edition</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
