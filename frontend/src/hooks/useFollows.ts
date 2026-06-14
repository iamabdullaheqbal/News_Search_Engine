import { useState, useCallback, useEffect } from 'react';
import { getGuestFollows, setGuestFollows } from '@/lib/api';

export function useFollows() {
  const [follows, setFollows] = useState<string[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    getGuestFollows()
      .then(({ topics }) => setFollows(topics))
      .catch(() => setFollows([]))
      .finally(() => setIsLoaded(true));
  }, []);

  const toggleFollow = useCallback((topic: string) => {
    setFollows((prev) => {
      const newFollows = prev.includes(topic)
        ? prev.filter((t) => t !== topic)
        : [...prev, topic];
      setGuestFollows(newFollows).catch(console.error);
      return newFollows;
    });
  }, []);

  return { follows, toggleFollow, isLoaded };
}
