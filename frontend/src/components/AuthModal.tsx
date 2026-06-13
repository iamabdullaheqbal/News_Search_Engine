'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { getGoogleAuthUrl } from '@/lib/api';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// Google "G" icon as inline SVG — no external dependency needed
function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" className="w-5 h-5" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  );
}

function Divider() {
  return (
    <div className="flex items-center gap-3 my-5">
      <span className="flex-1 h-px bg-border" />
      <span className="text-xxs font-bold tracking-widest uppercase text-charcoal-light">or</span>
      <span className="flex-1 h-px bg-border" />
    </div>
  );
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

  const handleGoogle = () => {
    // Full-page redirect to backend Google OAuth endpoint
    window.location.href = getGoogleAuthUrl();
  };

  const title = mode === 'login' ? 'Sign in' : 'Create account';
  const subtitle = mode === 'login' ? 'Welcome back.' : 'Join the global record.';
  const googleLabel = mode === 'login' ? 'Continue with Google' : 'Sign up with Google';
  const submitLabel = loading
    ? 'Please wait…'
    : mode === 'login' ? 'Sign in' : 'Create account';

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

        <h2 className="font-serif italic text-3xl mb-1">{title}</h2>
        <p className="text-sm text-charcoal-light mb-6">{subtitle}</p>

        {/* Google OAuth button */}
        <button
          type="button"
          onClick={handleGoogle}
          className="w-full flex items-center justify-center gap-3 border border-border py-2.5 text-sm font-medium hover:bg-cream-dark transition-colors"
        >
          <GoogleIcon />
          {googleLabel}
        </button>

        <Divider />

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
            {submitLabel}
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
