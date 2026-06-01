import { useEffect } from 'react';

export function useKeyboardShortcut(key: string, callback: () => void, metaKey = true) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (
        e.key.toLowerCase() === key.toLowerCase() &&
        (metaKey ? e.metaKey || e.ctrlKey : true)
      ) {
        e.preventDefault();
        callback();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [key, callback, metaKey]);
}
