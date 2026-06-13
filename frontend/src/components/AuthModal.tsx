'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(name, email, password);
      }
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div className="fixed inset-0 bg-cream/80 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md bg-cream border border-border shadow-2xl p-8">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 hover:bg-border rounded-md text-charcoal-light transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="font-serif italic text-3xl mb-1">
          {mode === 'login' ? 'Sign in' : 'Create account'}
        </h2>
        <p className="text-sm text-charcoal-light mb-8">
          {mode === 'login' ? 'Welcome back.' : 'Join the global record.'}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="text-xxs font-bold tracking-widest uppercase text-charcoal-light block mb-1">
                Name
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border border-border bg-transparent px-3 py-2.5 text-sm outline-none focus:border-charcoal transition-colors"
                placeholder="Your name"
              />
            </div>
          )}
          <div>
            <label className="text-xxs font-bold tracking-widest uppercase text-charcoal-light block mb-1">
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-border bg-transparent px-3 py-2.5 text-sm outline-none focus:border-charcoal transition-colors"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="text-xxs font-bold tracking-widest uppercase text-charcoal-light block mb-1">
              Password
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-border bg-transparent px-3 py-2.5 text-sm outline-none focus:border-charcoal transition-colors"
              placeholder="••••••••"
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-charcoal text-cream py-3 text-xs font-bold tracking-widest uppercase hover:bg-charcoal-light transition-colors disabled:opacity-50"
          >
            {loading ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>

        <p className="text-sm text-charcoal-light text-center mt-6">
          {mode === 'login' ? (
            <>No account?{' '}
              <button onClick={() => setMode('register')} className="underline hover:text-charcoal">
                Register
              </button>
            </>
          ) : (
            <>Already have one?{' '}
              <button onClick={() => setMode('login')} className="underline hover:text-charcoal">
                Sign in
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
