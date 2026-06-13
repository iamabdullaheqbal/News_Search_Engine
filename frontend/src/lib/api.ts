const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Article {
  id: string;
  title: string;
  dek?: string;
  category: string;
  source: string;
  author?: string;
  read_time?: string;
  image_url?: string;
  published_at?: string;
  timestamp?: string;
}

export interface ArticleDetail extends Article {
  body?: string[];
}

export interface User {
  id: number;
  email: string;
  name?: string;
  interests: string[];
}

export interface SearchResponse {
  query: string;
  total: number;
  results: Article[];
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  // In the browser, use a relative path — Next.js rewrites /api/* to the backend.
  // On the server (SSR), use the full URL directly.
  const url = typeof window === "undefined" ? `${BASE}${path}` : path;

  const res = await fetch(url, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

// Articles
export const getFeed = (limit = 20) =>
  apiFetch<Article[]>(`/api/articles/feed?limit=${limit}`);

export const getTrending = (limit = 5) =>
  apiFetch<string[]>(`/api/articles/trending?limit=${limit}`);

export const getArticlesByCategory = (category: string, limit = 20, offset = 0) =>
  apiFetch<Article[]>(`/api/articles/category/${category}?limit=${limit}&offset=${offset}`);

export const getArticleById = (id: string) =>
  apiFetch<ArticleDetail>(`/api/articles/${id}`);

// Search
export const searchArticles = (q: string, category?: string, limit = 20, offset = 0) => {
  const params = new URLSearchParams({ q, limit: String(limit), offset: String(offset) });
  if (category) params.set("category", category);
  return apiFetch<SearchResponse>(`/api/search?${params}`);
};

// Auth
export const register = (name: string, email: string, password: string) =>
  apiFetch<{ user: User }>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });

export const login = (email: string, password: string) =>
  apiFetch<{ user: User }>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

export const logout = () =>
  apiFetch<void>("/api/auth/logout", { method: "POST" });

export const getMe = () =>
  apiFetch<User>("/api/auth/me");

export const refreshToken = () =>
  apiFetch<{ user: User }>("/api/auth/refresh", { method: "POST" });

export const toggleInterest = (topic: string) =>
  apiFetch<{ interests: string[] }>("/api/auth/interests/toggle", {
    method: "POST",
    body: JSON.stringify({ topic }),
  });

// Google OAuth — redirects browser to Google consent screen
export const getGoogleAuthUrl = () => {
  const base = typeof window === "undefined" ? BASE : "";
  return `${base}/api/auth/google`;
};
