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

## About

Veritas is an NLP course project built as part of the **Natural Language Processing** course at the **University of Management and Technology (UMT)**, Sialkot — BSCS 6th Semester.

The project applies NLP concepts studied in class — text embeddings, semantic similarity, and information retrieval — inside a full-stack web application. It aggregates real news articles from two public APIs, stores them with dense vector representations in PostgreSQL, and retrieves them through a three-stage hybrid search pipeline.

---

## How Search Works

```
User submits query
        ↓
BM25 (rank-bm25)              Semantic (pgvector cosine)
top-30 candidates     +        top-30 candidates
        ↓                              ↓
            Union of candidate IDs (RRF merge)
                    ↓
     Optional category filter (SQL WHERE)
                    ↓
  Cross-encoder reranking (ms-marco-MiniLM-L-6-v2)
     score each (query, title + dek + category) pair
                    ↓
        Top-20 reranked results
                    ↓
        Paginated response
```

**BM25** handles exact keyword matches with NLTK lemmatization at both index and query time.  
**Semantic search** handles paraphrases and conceptual queries via pgvector cosine distance on the same title+dek+body text used for BM25.  
**Reciprocal Rank Fusion (RRF)** merges BM25 and semantic candidate lists before reranking.  
**Cross-encoder** re-scores the union using full query–document attention, giving relevance quality well above either method alone.

---

## Key Features

- **Hybrid search** — BM25 + pgvector cosine similarity + cross-encoder reranking in a single pipeline
- **Dual-source ingestion** — GNews and NewsAPI with quota-aware pagination (~4,000+ articles per run)
- **Full body scraping** — concurrent scraper fetches full article text from source URLs at ingest time
- **Batch embeddings** — all articles embedded in a single `sentence-transformers` batch call per category
- **Personalized feed** — recency-weighted ranking with category diversity; deprioritizes articles you've already read
- **Trending** — most-read article titles in the last 7 days (falls back to latest headlines)
- **Live Wire** — latest headlines from the database with publication times
- **Read history** — article views tracked per user in the database
- **Semantically related articles** — article detail page shows 6 related articles found via the hybrid search pipeline, not just same-category articles
- **JWT auth + Google OAuth** — httpOnly cookie delivery with server-side refresh token rotation
- **Rate limiting** — per-IP rate limiter on search and auth endpoints, graceful Redis fallback
- **Dynamic categories** — category list always read from the DB at runtime
- **Celery scheduled ingestion** — background worker fetches new articles every 6 hours
- **Search pagination** — server-side offset pagination on both search results and category pages
- **Functional share buttons** — Twitter, Facebook, and copy-link all wired up on article pages
- **Persistent recent searches** — search history stored in localStorage
- **Token refresh on tab focus** — auth silently re-validates when user returns to the tab
- **Dynamic page titles** — every page has its own `<title>` based on article/category/query
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
| Dense embeddings | sentence-transformers (`all-MiniLM-L6-v2`) | ≥ 5.5.1 |
| Cross-encoder reranking | sentence-transformers (`ms-marco-MiniLM-L-6-v2`) | ≥ 5.5.1 |
| Sparse retrieval | rank-bm25 (BM25Okapi) | ≥ 0.2.2 |
| Text processing | NLTK (lemmatization) | ≥ 3.9.4 |
| Web scraping | BeautifulSoup4 + lxml | ≥ 4.12 / ≥ 5.2 |
| Auth | python-jose + bcrypt | ≥ 3.5.0 / ≥ 5.0.0 |
| Task queue | Celery | ≥ 5.6.3 |
| Cache / token store | Redis | ≥ 8.0.0 |
| HTTP client | httpx | ≥ 0.28.1 |
| Settings | pydantic-settings | ≥ 2.14.1 |
| Frontend framework | Next.js (App Router) | 16.2.6 |
| UI library | React | 19.2.4 |
| Styling | Tailwind CSS | v4 |
| Icons | lucide-react | ≥ 1.17.0 |
| Language | TypeScript | v5 |
| Package manager (Python) | uv | latest |

---

## Project Structure

```
News_Search_Engine/
├── backend/
│   ├── main.py                        # Uvicorn entry point
│   ├── pyproject.toml                 # Python dependencies (uv)
│   ├── .env                           # Environment variables (never commit)
│   ├── .python-version                # Pins Python 3.13
│   ├── run_ingestion.py               # Standalone ingestion script
│   │
│   └── app/
│       ├── main.py                    # App factory, lifespan, CORS, routers
│       │
│       ├── api/
│       │   ├── routes_articles.py     # Articles, feed, categories, ingest, read history
│       │   ├── routes_auth.py         # Register, login, refresh, logout, Google OAuth
│       │   └── routes_search.py       # Hybrid search endpoint
│       │
│       ├── core/
│       │   ├── settings.py            # Pydantic settings (reads .env)
│       │   ├── category_map.py        # Ingestion → frontend category mapping
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
│       │   ├── search.py              # Hybrid search + feed ranking pipeline
│       │   ├── ingestion_service.py   # GNews + NewsAPI fetch, embed, save, BM25 build
│       │   ├── scraper.py             # Full article body scraper (BeautifulSoup)
│       │   ├── embedding.py           # Lazy-loaded sentence encoder
│       │   ├── reranker.py            # Lazy-loaded cross-encoder
│       │   ├── bm25.py                # In-memory BM25Okapi index singleton
│       │   ├── auth.py                # JWT creation/decoding, password hashing
│       │   ├── interest.py            # User interest DB operations + cookie parsing
│       │   └── token_store.py         # Redis refresh token store + access token blacklist
│       │
│       └── tasks/
│           └── ingestion_tasks.py     # Celery task — runs every 6 hours
│
└── frontend/
    ├── package.json
    ├── next.config.ts                 # Security headers + /api/* proxy rewrites
    │
    └── src/
        ├── app/
        │   ├── layout.tsx             # Root layout — SSR category fetch, providers
        │   ├── page.tsx               # Home page (personalized feed + sidebar)
        │   ├── not-found.tsx          # 404 page
        │   ├── article/[id]/page.tsx  # Article detail + related articles
        │   ├── category/[slug]/page.tsx  # Category listing with load-more pagination
        │   └── search/page.tsx        # Search results with server-side pagination
        │
        ├── components/
        │   ├── Header.tsx             # Sticky nav with live search modal (CMD+K)
        │   ├── Footer.tsx             # Category links + newsletter
        │   ├── Sidebar.tsx            # Trending + follows + live wire
        │   ├── HomeContent.tsx        # Personalized feed with load more
        │   ├── ArticleCard.tsx        # Article card (featured + grid variants)
        │   ├── ArticleShareBar.tsx    # Functional Twitter/Facebook/copy-link buttons
        │   ├── LoadMoreArticles.tsx   # Client-side pagination component
        │   ├── SearchModal.tsx        # Live search overlay with recent searches
        │   ├── SearchResults.tsx      # Full search results with filters + pagination
        │   └── AuthModal.tsx          # Login / register modal with Google OAuth
        │
        ├── hooks/
        │   ├── useAuth.tsx            # Auth context with tab-focus token refresh
        │   ├── useCategories.tsx      # DB-driven categories context
        │   ├── useFollows.ts          # Guest cookie-based follows
        │   └── useKeyboardShortcut.ts # CMD+K shortcut hook
        │
        └── lib/
            ├── api.ts                 # Typed API client + shared types
            ├── sanitize.ts            # Image URL sanitization
            └── utils.ts               # cn() Tailwind class merger
```

---

## Prerequisites

- **Python 3.13+**
- **Node.js 18+**
- **PostgreSQL** with the [pgvector](https://github.com/pgvector/pgvector) extension enabled
- **Redis** (optional in development — auth still works without it; rate limiting and BM25 cross-worker sync require Redis)
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — Python package manager
- API keys for **[GNews](https://gnews.io)** and/or **[NewsAPI](https://newsapi.org)**

### Quick infrastructure with Docker

```bash
docker compose up -d
```

This starts PostgreSQL (with pgvector) and Redis. Use `DATABASE_URL=postgresql+asyncpg://veritas:veritas@localhost:5432/veritas` in `backend/.env`.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values. **Never commit `.env` to version control.**

### Backend — `backend/.env`

```env
# Environment
ENVIRONMENT=development   # set to "production" to disable API docs

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/veritas

# JWT — use a long random string for SECRET_KEY
SECRET_KEY=<generate a strong random secret>
ALGORITHM=<jwt signing algorithm>
ACCESS_TOKEN_EXPIRE_MINUTES=<your chosen value>
REFRESH_TOKEN_EXPIRE_DAYS=<your chosen value>

# Google OAuth
GOOGLE_CLIENT_ID=<from Google Cloud Console>
GOOGLE_CLIENT_SECRET=<from Google Cloud Console>
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Frontend
FRONTEND_URL=http://localhost:3000

# Cookie settings
COOKIE_NAME=<your chosen name>
REFRESH_COOKIE_NAME=<your chosen name>
COOKIE_SECURE=False          # set True in production (HTTPS only)
COOKIE_SAMESITE=lax

# News APIs
GNEWS_API_KEY=<your GNews key>
NEWSAPI_KEY=<your NewsAPI key>

# Redis
REDIS_URL=redis://localhost:6379/2
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Admin ingestion endpoint
INGEST_API_KEY=<generate a strong random secret>
```

### Frontend — `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
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
1. Database tables are created
2. BM25 index is built from all articles in the DB
3. Both ML models (embedding + reranker) are warmed up — allow ~30–60s on first cold start
4. Valid interest topics are loaded from the DB

API docs available at **http://localhost:8000/docs** in development mode only.

---

## Running the Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend runs at **http://localhost:3000**

All `/api/*` requests are proxied to the backend — no CORS configuration needed in development.

---

## Ingesting News Articles

```bash
cd backend
uv run python run_ingestion.py
```

Fetches from GNews and NewsAPI across all 9 categories, scrapes full article bodies, computes batch embeddings, saves to the DB, and rebuilds the BM25 index. Expect ~4,000+ articles per run on free-tier API accounts.

**Re-run ingestion after upgrading** if you need to refresh existing article embeddings (now computed from title + dek + body, not title + dek only).

Ingestion can also be triggered via the admin endpoint:

```bash
# All categories
curl -X POST "http://localhost:8000/api/articles/ingest" \
  -H "X-Ingest-Key: <your INGEST_API_KEY>"

# Single category
curl -X POST "http://localhost:8000/api/articles/ingest?category=technology" \
  -H "X-Ingest-Key: <your INGEST_API_KEY>"
```

---

## API Reference

### Articles

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/articles/categories` | — | Distinct categories from DB |
| `GET` | `/api/articles/feed` | optional | Personalized ranked feed |
| `GET` | `/api/articles/trending` | — | Most-read titles (7-day window, recent fallback) |
| `GET` | `/api/articles/live-wire` | — | Latest headlines with publication times |
| `GET` | `/api/articles/category/{category}` | — | Paginated articles by category |
| `GET` | `/api/articles/{id}` | optional | Article detail + records read history |
| `GET` | `/api/articles/{id}/related` | — | Semantically related articles |
| `GET` | `/api/articles/follows` | — | Guest category follows (cookie) |
| `POST` | `/api/articles/follows` | — | Set guest category follows |
| `POST` | `/api/articles/ingest` | `X-Ingest-Key` | Trigger news ingestion |

### Search

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/search?q=...` | Hybrid BM25 + semantic + rerank search |

Params: `q` (required), `category`, `limit`, `offset`

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Email/password registration |
| `POST` | `/api/auth/login` | Login — sets httpOnly cookies |
| `POST` | `/api/auth/refresh` | Silent token rotation |
| `POST` | `/api/auth/logout` | Revoke tokens, clear cookies |
| `GET` | `/api/auth/me` | Current user + interests |
| `POST` | `/api/auth/interests/toggle` | Toggle a followed topic |
| `PUT` | `/api/auth/interests` | Replace interests list |
| `GET` | `/api/auth/google` | Initiate Google OAuth flow |
| `GET` | `/api/auth/google/callback` | Handle OAuth callback |

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
  id (uuid), title, dek, body (JSON paragraphs), processed_text (lemmatized),
  category, source, author, read_time, image_url, url (unique),
  published_at, embedding (vector(384))
```

The `embedding` column stores 384-dimensional vectors from `all-MiniLM-L6-v2` for pgvector cosine distance queries.

---

## Category Mapping

Raw API categories are mapped to frontend display categories using keyword detection:

| Frontend Category | Source categories | Keyword override |
|---|---|---|
| POLITICS | general, world, nation | — |
| ECONOMY | business | — |
| TECH | technology | — |
| CULTURE | entertainment | — |
| SPORTS | sports | — |
| SCIENCE | science | — |
| HEALTH | health | — |
| CLIMATE | any | climate / emissions / carbon keywords |
| MARKETS | any | stock market / nasdaq / fed rate keywords |

---

## Known Limitations

- **BM25 index is in-memory** — each worker holds its own copy; Redis version sync triggers rebuilds across workers after ingestion (requires Redis)
- **Schema bootstrap** — `ensure_schema()` creates tables and the pgvector HNSW index on startup; no Alembic migration history
- **No test suite** — the project has no automated tests
- **Redis is optional** — without Redis, token revocation is skipped, rate limiting is disabled, and BM25 sync across workers is unavailable

---

*NLP Course Project — BSCS 6th Semester, UMT Sialkot.*  
*Always verify important news through trusted, authoritative sources.*
