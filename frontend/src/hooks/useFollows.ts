import { useState, useEffect, useCallback } from 'react';

export function useFollows() {
  const [follows, setFollows] = useState<string[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const match = document.cookie.match(new RegExp('(^| )veritas_follows=([^;]+)'));
    if (match) {
      try {
        setFollows(JSON.parse(decodeURIComponent(match[2])));
      } catch (e) {
        console.error('Failed to parse follows cookie', e);
      }
    }
    setIsLoaded(true);
  }, []);

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
