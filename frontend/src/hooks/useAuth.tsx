'use client';

import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { getMe, login as apiLogin, register as apiRegister, logout as apiLogout, toggleInterest as apiToggle, refreshToken, User } from '@/lib/api';

interface AuthState {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  toggleInterest: (topic: string) => Promise<void>;
}

const AuthContext = createContext<AuthState>({
  user: null,
  loading: true,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  toggleInterest: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if Google OAuth just completed (backend redirected back with ?auth_success=1)
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('auth_success') === '1') {
        const clean = window.location.pathname + window.location.hash;
        window.history.replaceState({}, '', clean);
      }
      if (params.get('auth_error')) {
        const code = params.get('auth_error')!;
        const messages: Record<string, string> = {
          account_exists: 'An account with this email already exists. Sign in with your password instead.',
          invalid_state: 'Sign-in session expired. Please try again.',
          oauth_failed: 'Google sign-in failed. Please try again.',
        };
        console.warn('Google OAuth error:', messages[code] ?? code);
        const clean = window.location.pathname + window.location.hash;
        window.history.replaceState({}, '', clean);
      }
    }

    // Try access token first; if expired, attempt silent refresh
    getMe()
      .then(setUser)
      .catch(() =>
        refreshToken()
          .then(({ user }) => setUser(user))
          .catch(() => setUser(null))
      )
      .finally(() => setLoading(false));
  }, []);

  // Re-validate auth when user switches back to this tab after being away.
  // Access tokens expire in 30 minutes — this catches the case where a user
  // leaves the tab open and returns to find their session expired.
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState !== 'visible') return;
      getMe()
        .then(setUser)
        .catch(() =>
          refreshToken()
            .then(({ user }) => setUser(user))
            .catch(() => setUser(null))
        );
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { user } = await apiLogin(email, password);
    setUser(user);
  }, []);

  const register = useCallback(async (name: string, email: string, password: string) => {
    const { user } = await apiRegister(name, email, password);
    setUser(user);
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  const toggleInterest = useCallback(async (topic: string) => {
    const { interests } = await apiToggle(topic);
    setUser((prev) => prev ? { ...prev, interests } : prev);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, toggleInterest }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
