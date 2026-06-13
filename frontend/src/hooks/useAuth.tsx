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
