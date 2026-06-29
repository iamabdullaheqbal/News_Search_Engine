'use client';

import { useState } from 'react';
import { Link as LinkIcon, Bookmark, Check } from 'lucide-react';

const Twitter = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z" />
  </svg>
);

const Facebook = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" />
  </svg>
);

interface Props {
  title: string;
  url: string;
}

export function ArticleShareBar({ title, url }: Props) {
  const [copied, setCopied] = useState(false);

  const shareTwitter = () => {
    window.open(
      `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`,
      '_blank',
      'noopener,noreferrer,width=600,height=400',
    );
  };

  const shareFacebook = () => {
    window.open(
      `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
      '_blank',
      'noopener,noreferrer,width=600,height=400',
    );
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback for browsers that block clipboard without user gesture
      const ta = document.createElement('textarea');
      ta.value = url;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="flex items-center gap-2 text-charcoal-light">
      <button
        onClick={shareTwitter}
        aria-label="Share on Twitter"
        className="p-2 hover:bg-border rounded transition-colors"
      >
        <Twitter className="w-4 h-4" />
      </button>
      <button
        onClick={shareFacebook}
        aria-label="Share on Facebook"
        className="p-2 hover:bg-border rounded transition-colors"
      >
        <Facebook className="w-4 h-4" />
      </button>
      <button
        onClick={copyLink}
        aria-label={copied ? 'Link copied' : 'Copy link'}
        className="p-2 hover:bg-border rounded transition-colors"
      >
        {copied ? (
          <Check className="w-4 h-4 text-green-600" />
        ) : (
          <LinkIcon className="w-4 h-4" />
        )}
      </button>
      <span className="w-px h-5 bg-border mx-1" />
      <button
        aria-label="Save article"
        className="p-2 hover:bg-border rounded transition-colors"
      >
        <Bookmark className="w-4 h-4" />
      </button>
    </div>
  );
}
