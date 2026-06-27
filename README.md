<div align="center">

# 🗞️ Veritas

### *Truth in Every Word.*

**AI-powered news search engine with hybrid retrieval — BM25 + semantic embeddings + cross-encoder reranking**

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16.2.6-000000?style=flat-square&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-19.2.4-61DAFB?style=flat-square&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=flat-square&logo=postgresql&logoColor=white)
![sentence-transformers](https://img.shields.io/badge/sentence--transformers-5.5.1-FFD43B?style=flat-square&logo=huggingface&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

</div>

---

## What Is Veritas

Veritas is a full-stack news aggregation and intelligent search platform. It pulls real articles from **GNews** and **NewsAPI**, stores them in PostgreSQL with vector embeddings, and serves them through a three-stage hybrid search pipeline that combines sparse keyword matching, dense semantic retrieval, and cross-encoder reranking.

The frontend is a Next.js App Router application with category-based browsing, personalized feeds, Google OAuth, and a clean editorial design. The backend is a fully async FastAPI service with JWT auth, Redis-backed token management, Celery for scheduled ingestion, and rate limiting.

---

## How Search Works

```
User submits query
        ↓
BM25 (rank-bm25)              Semantic (pgvector cosine)
top-30 candidates     +        top-30 candidates
        ↓                              ↓
            Union of candidate IDs
                    ↓
     Optional category filter (SQL WHERE)
                    ↓
  Cross-encoder reranking (ms-marco-MiniLM-L-6-v2)
     score each (query, title + dek + category) pair
                    ↓
        Top-20 reranked results
                    ↓
        Paginated ArticleOut response
```

**BM25** handles exact keyword matches and rare terms. **Semantic search** handles paraphrases and conceptual queries. The **cross-encoder** re-scores the union using the full query–document interaction, giving relevance quality well above either method alone.

---

## Key Features

- **Hybrid search** — BM25 + pgvector cosine similarity + cross-encoder reranking in a single pipeline
- **Dual-source ingestion** — GNews and NewsAPI with quota-aware pagination (~4,000+ articles per daily run)
- **Batch embeddings** — all articles in a category are embedded in a single `sentence-transformers` batch call at ingest time
- **Personalized feed** — logged-in users follow categories; guests use a cookie-backed follows system
- **JWT auth + Google OAuth** — httpOnly cookie delivery, refresh token rotation, Redis-backed revocation
- **Rate limiting** — Redis-backed per-IP rate limiter on search and auth endpoints
- **Dynamic categories** — category list is always read from the DB, no hardcoded lists anywhere
- **Celery scheduled ingestion** — background worker triggers periodic news fetches
- **Responsive editorial UI** — sticky nav, article cards, featured hero layout, search modal (CMD+K), RTL-safe
- **No mock data** — zero hardcoded articles; everything served from PostgreSQL

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Backend framework | FastAPI | ≥ 0.136.3 |
| ASGI server | Uvicorn | ≥ 0.48.0 |
| Database | PostgreSQL + pgvector | — |
| ORM | SQLAlchemy (async) | ≥ 2.0.50 |
| DB driver | asyncpg | ≥ 0.31.0 |
| Migrations | Alembic | ≥ 1.18.4 |
| Dense embeddings | sentence-transformers (`all-MiniLM-L6-v2`) | ≥ 5.5.1 |
| Cross-encoder reranking | sentence-transformers (`ms-marco-MiniLM-L-6-v2`) | ≥ 5.5.1 |
| Sparse retrieval | rank-bm25 (BM25Okapi) | ≥ 0.2.2 |
| Text processing | NLTK + spaCy | ≥ 3.9.4 / ≥ 3.8.14 |
| ML framework | scikit-learn | ≥ 1.9.0 |
| Auth | python-jose + bcrypt | ≥ 3.5.0 / ≥ 5.0.0 |
| Task queue | Celery | ≥ 5.6.3 |
| Cache / token store | Redis | ≥ 8.0.0 |
| HTTP client | httpx | ≥ 0.28.1 |
| Settings | pydantic-settings | ≥ 2.14.1 |
| Frontend framework | Next.js (App Router) | 16.2.6 |
| UI library | React | 19.2.4 |
| Styling | Tailwind CSS | v4 |
| Icons | lucide-react | ≥ 1.17.0 |
| Class utilities | clsx + tailwind-merge | ≥ 2.1.1 / ≥ 3.6.0 |
| Language | TypeScript | v5 |
| Package manager (Python) | uv | latest |

---

## Project Structure

```
News_Search_Engine/
├── backend/
│   ├── main.py                        # Uvicorn entry point
│   ├── pyproject.toml                 # Python dependencies (uv)
│   ├── .env                           # Environment variables
│   ├── .python-version                # Pins Python 3.13
│   ├── run_ingestion.py               # Standalone ingestion script
│   ├── fix_categories.py              # One-time DB category migration util
│   │
│   └── app/
│       ├── main.py                    # App factory, lifespan, CORS, routers
│       │
│       ├── api/
│       │   ├── routes_articles.py     # Articles, feed, trending, categories, ingest
│       │   ├── routes_auth.py         # Register, login, refresh, logout, Google OAuth
│       │   └── routes_search.py       # Hybrid search endpoint
│       │
│       ├── core/
│       │   ├── settings.py            # Pydantic settings (reads .env)
│       │   ├── category_map.py        # Ingestion → frontend category mapping + keyword overrides
│       │   ├── validators.py          # DB-driven interest topic validation
│       │   ├── rate_limit.py          # Redis-backed per-IP rate limiter
│       │   ├── sanitize.py            # Image URL sanitization
│       │   └── deps.py                # Ingest API key dependency
│       │
│       ├── db/
│       │   ├── database.py            # AsyncSessionLocal, engine, Base
│       │   └── models.py              # User, UserInterest, ReadHistory, Article
│       │
│       ├── schemas/
│       │   ├── article.py             # ArticleOut, ArticleDetail
│       │   ├── auth.py                # RegisterRequest, LoginRequest, UserOut, AuthResponse
│       │   └── search.py              # SearchRequest, SearchResponse
│       │
│       ├── services/
│       │   ├── search.py              # Hybrid search pipeline
│       │   ├── ingestion_service.py   # GNews + NewsAPI fetch, map, embed, save, BM25 build
│       │   ├── embedding.py           # Lazy-loaded all-MiniLM-L6-v2 sentence encoder
│       │   ├── reranker.py            # Lazy-loaded ms-marco-MiniLM-L-6-v2 cross-encoder
│       │   ├── bm25.py                # In-memory BM25Okapi index singleton
│       │   ├── auth.py                # JWT creation/decoding, password hashing
│       │   ├── interest.py            # User interest DB operations + cookie parsing
│       │   └── token_store.py         # Redis refresh token store + access token blacklist
│       │
│       └── tasks/
│           └── ingestion_tasks.py     # Celery task wrapper for scheduled ingestion
│
└── frontend/
    ├── package.json
    ├── next.config.ts                 # Security headers + /api/* proxy rewrites
    ├── tsconfig.json
    │
    └── src/
        ├── app/
        │   ├── layout.tsx             # Root layout — fetches categories SSR, mounts providers
        │   ├── page.tsx               # Home page (personalized feed + sidebar)
        │   ├── not-found.tsx          # 404 page
        │   ├── article/[id]/
        │   │   └── page.tsx           # Article detail + related articles
        │   ├── category/[slug]/
        │   │   └── page.tsx           # Category listing page (dynamic, DB-driven)
        │   └── search/
        │       └── page.tsx           # Search results page
        │
        ├── components/
        │   ├── Header.tsx             # Sticky nav with search bar (CMD+K) + mobile menu
        │   ├── Footer.tsx             # Newsletter signup + category links + social
        │   ├── Sidebar.tsx            # Trending now + follows widget + live wire ticker
        │   ├── HomeContent.tsx        # Personalized feed grid
        │   ├── ArticleCard.tsx        # Article card (featured + grid variants)
        │   ├── SearchModal.tsx        # Floating search overlay
        │   ├── SearchResults.tsx      # Full search results with category + time filters
        │   └── AuthModal.tsx          # Login / register modal with Google OAuth
        │
        ├── hooks/
        │   ├── useAuth.tsx            # Auth context — user state, login, logout, token refresh
        │   ├── useCategories.tsx      # Categories context (fed from SSR fetch in layout)
        │   ├── useFollows.ts          # Guest cookie-based category follows
        │   └── useKeyboardShortcut.ts # CMD+K shortcut hook
        │
        └── lib/
            ├── api.ts                 # Typed API client + shared types + CATEGORY_TAGLINES
            ├── sanitize.ts            # Image URL sanitization
            └── utils.ts               # cn() Tailwind class merger
```

---

## Prerequisites

- **Python 3.13+**
- **Node.js 18+**
- **PostgreSQL** with the [pgvector](https://github.com/pgvector/pgvector) extension enabled
- **Redis** (for token store and rate limiting — optional in development, auth still works without it)
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — Python package manager
- API keys for **[GNews](https://gnews.io)** and/or **[NewsAPI](https://newsapi.org)**

---

## Environment Variables

### Backend — `backend/.env`

```env
# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/veritas

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Frontend
FRONTEND_URL=http://localhost:3000

# Cookies
COOKIE_NAME=veritas_session
REFRESH_COOKIE_NAME=veritas_refresh
COOKIE_SECURE=False
COOKIE_SAMESITE=lax

# News APIs
GNEWS_API_KEY=your-gnews-key
NEWSAPI_KEY=your-newsapi-key

# Redis (optional — auth degrades gracefully if Redis is down)
REDIS_URL=redis://localhost:6379/2
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Admin ingestion key
INGEST_API_KEY=your-ingest-secret
```

### Frontend — `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running the Backend

```bash
cd backend

# Install dependencies
uv sync

# Start the server
uvicorn main:app --reload
```

Backend runs at **http://localhost:8000**

On first startup:
1. Database tables are created via `metadata.create_all`
2. The BM25 index is built from all articles in the DB
3. Valid interest topics are loaded from the DB into memory

API docs available at **http://localhost:8000/docs** (development only).

---

## Running the Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend runs at **http://localhost:3000**

All `/api/*` requests are proxied by Next.js rewrites to `localhost:8000` — no CORS issues in development.

---

## Ingesting News Articles

Run the standalone ingestion script to populate the database:

```bash
cd backend
uv run python run_ingestion.py
```

This fetches from both GNews and NewsAPI across all 9 categories, computes embeddings in batch, saves to the DB, and rebuilds the BM25 index. On a free-tier API account expect ~4,000+ articles per run.

You can also trigger ingestion via the API (requires `INGEST_API_KEY`):

```bash
# All categories
curl -X POST "http://localhost:8000/api/articles/ingest" \
  -H "X-Ingest-Key: your-ingest-secret"

# Single category
curl -X POST "http://localhost:8000/api/articles/ingest?category=technology" \
  -H "X-Ingest-Key: your-ingest-secret"
```

---

## API Endpoints

### Articles

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/articles/categories` | — | Distinct categories from DB |
| `GET` | `/api/articles/` | — | Paginated article list |
| `GET` | `/api/articles/count` | — | Article count (optionally by category) |
| `GET` | `/api/articles/feed` | optional | Personalized feed (user interests or cookie follows) |
| `GET` | `/api/articles/trending` | — | Top N article titles by recency |
| `GET` | `/api/articles/category/{category}` | — | Articles in a specific category |
| `GET` | `/api/articles/follows` | — | Guest follows from cookie |
| `POST` | `/api/articles/follows` | — | Set guest follows cookie |
| `GET` | `/api/articles/{id}` | — | Single article detail |
| `POST` | `/api/articles/ingest` | `X-Ingest-Key` | Trigger ingestion |

### Search

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/search?q=...` | — | Hybrid BM25 + semantic + rerank search |

Query params: `q` (required), `category`, `limit` (default 20, max 50), `offset`

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Email/password registration |
| `POST` | `/api/auth/login` | Login, sets httpOnly cookies |
| `POST` | `/api/auth/refresh` | Rotate refresh token, issue new access token |
| `POST` | `/api/auth/logout` | Revoke tokens, clear cookies |
| `GET` | `/api/auth/me` | Current user + interests |
| `POST` | `/api/auth/interests/toggle` | Toggle a followed category |
| `PUT` | `/api/auth/interests` | Replace full interests list |
| `GET` | `/api/auth/google` | Redirect to Google consent screen |
| `GET` | `/api/auth/google/callback` | Handle OAuth callback, upsert user |

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | `{ "status": "ok" }` |

---

## Article Response Shape

```json
{
  "id": "uuid-string",
  "title": "Article headline",
  "dek": "Short summary / subheadline",
  "category": "TECH",
  "source": "The Verge",
  "author": "Jane Smith",
  "read_time": "4 min read",
  "image_url": "https://...",
  "published_at": "2026-06-27T10:00:00+00:00",
  "timestamp": "3 hours ago"
}
```

Article detail additionally includes `body: string[]` — a JSON array of paragraphs.

---

## Search Response Shape

```json
{
  "query": "artificial intelligence chips",
  "total": 47,
  "results": [ ...ArticleOut[] ]
}
```

---

## Database Schema

```
users
  id, email, hashed_password, google_id, name, created_at

user_interests
  id, user_id → users.id, topic

read_history
  id, user_id → users.id, article_id, read_at

articles
  id (uuid), title, dek, body (JSON text), processed_text (lemmatized),
  category, source, author, read_time, image_url, url (unique),
  published_at, embedding (vector(384))
```

The `embedding` column stores 384-dimensional vectors from `all-MiniLM-L6-v2`, indexed by pgvector for cosine distance queries.

---

## Category Mapping

Raw ingestion categories from the news APIs are mapped to frontend display categories using keyword detection and a structural fallback:

| Frontend Category | Maps from | Keyword override |
|---|---|---|
| POLITICS | general, world, nation | — |
| ECONOMY | business | — |
| TECH | technology | — |
| CULTURE | entertainment | — |
| SPORTS | sports | — |
| SCIENCE | science | — |
| HEALTH | health | — |
| CLIMATE | any | climate/emissions/carbon/... keywords |
| MARKETS | any | stock market/nasdaq/fed rate/... keywords |

Categories are always read from the DB at runtime — adding new categories requires no code changes.

---

## Security Notes

- Access tokens are delivered in httpOnly, SameSite cookies — not localStorage
- Refresh tokens are server-side tracked in Redis (atomic rotation via `GETDEL`)
- Access tokens can be blacklisted in Redis on logout before their natural expiry
- Google OAuth uses a per-request CSRF state token stored in a short-lived httpOnly cookie
- Existing email accounts are never auto-linked to a Google login — prevents account takeover
- CSP, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` headers set on all frontend routes
- HSTS enabled in production
- Docs (`/docs`, `/redoc`) disabled in production

---

## Known Limitations

- **BM25 index is process-local** — each uvicorn worker and the Celery worker maintain separate in-memory indices. New articles won't appear in BM25 search until the next startup or index rebuild.
- **No Alembic migrations wired up** — schema is managed via `create_all` on startup. Destructive column changes require manual migration.
- **No test suite** — the project has no automated tests.
- **Redis optional** — when Redis is unavailable, token revocation is silently skipped. Auth cookies still clear on logout but tokens remain technically valid until natural expiry.

---

*Veritas is a personal project. Always verify important news through trusted, authoritative sources.*
