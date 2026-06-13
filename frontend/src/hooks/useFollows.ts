import { useState, useCallback } from 'react';

function getStoredFollows() {
  if (typeof document === 'undefined') return [];
  const match = document.cookie.match(new RegExp('(^| )veritas_follows=([^;]+)'));
  if (!match) return [];
  try {
    return JSON.parse(decodeURIComponent(match[2]));
  } catch (e) {
    console.error('Failed to parse follows cookie', e);
    return [];
  }
}

export function useFollows() {
  const [follows, setFollows] = useState<string[]>(getStoredFollows);
  const isLoaded = true;

  const toggleFollow = useCallback((topic: string) => {
    setFollows((prev) => {
      const newFollows = prev.includes(topic)
        ? prev.filter((t) => t !== topic)
        : [...prev, topic];
      document.cookie = `veritas_follows=${encodeURIComponent(JSON.stringify(newFollows))}; path=/; max-age=31536000`;
      return newFollows;
    });
  }, []);

  return { follows, toggleFollow, isLoaded };
}
