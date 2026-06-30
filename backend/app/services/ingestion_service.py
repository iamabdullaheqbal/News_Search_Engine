"""News article ingestion — targeting 1000 articles from each API.

Daily budget (free tiers):
  GNews   100 req/day, max 10 articles/request
          → 9 categories × ~11 requests each  = 99 req  → ~990 articles
          (general & world get 12 requests, rest get 11)

  NewsAPI 100 req/day, max 100 articles/request, page 1 only
          → 9 categories × 6 keywords each   = 54 req  → up to 5400 raw articles
          (deduplication brings real yield to ~1000–1500 unique articles)
"""
from __future__ import annotations

import asyncio
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.category_map import assign_frontend_category
from app.core.settings import get_settings
from app.db.models import Article
from app.services.bm25_sync import mark_bm25_rebuilt
from app.services.embedding import embed_texts
from app.services.scraper import scrape_article_body
from app.services.text_processing import build_retrieval_text, lemmatize_text

logger = logging.getLogger("veritas")
settings = get_settings()

# ── Categories ───────────────────────────────────────────────────────────────

CATEGORIES = [
    "general", "world", "nation", "business",
    "technology", "entertainment", "sports", "science", "health",
]

GNEWS_CATEGORY_MAP: dict[str, str] = {
    "general":       "general",
    "world":         "world",
    "nation":        "nation",
    "business":      "business",
    "technology":    "technology",
    "entertainment": "entertainment",
    "sports":        "sports",
    "science":       "science",
    "health":        "health",
}

# NewsAPI /everything keywords per category — more keywords = more unique articles
# within the 100 req/day budget (9 categories × 6 keywords = 54 requests, well under limit)
NEWSAPI_KEYWORD_MAP: dict[str, list[str]] = {
    "general":       ["breaking news today", "current events headlines", "top stories world", "latest news update", "headline news", "major news today"],
    "world":         ["world news international", "global affairs news", "international headlines", "foreign news today", "global politics", "world events"],
    "nation":        ["US national news", "domestic political news", "American news today", "US government policy", "US elections legislation", "federal news USA"],
    "business":      ["business economy finance", "stock market investing", "corporate earnings news", "global trade economy", "startup funding venture", "market trends business"],
    "technology":    ["technology AI software", "tech innovation gadgets", "artificial intelligence news", "cybersecurity data breach", "tech companies products", "software development cloud"],
    "entertainment": ["entertainment movies music", "celebrity news Hollywood", "streaming TV shows", "film industry awards", "pop culture entertainment", "gaming esports news"],
    "sports":        ["sports NFL NBA soccer", "sports scores results", "Olympics athletics news", "tennis golf sports", "transfer football sports", "sports championship league"],
    "science":       ["science research discovery", "space astronomy NASA", "climate environment science", "biology medicine research", "physics chemistry breakthrough", "scientific study findings"],
    "health":        ["health medicine medical", "public health disease", "mental health wellness", "nutrition diet fitness", "healthcare policy hospital", "medical research treatment"],
}

# ── Pagination constants ──────────────────────────────────────────────────────

# GNews free tier: max 10 articles/request, 100 req/day
# Distribute 99 requests across 9 categories:
#   general & world → 12 requests each  (12 × 2 = 24)
#   remaining 7     → 11 requests each  (11 × 7 = 77)
#   total = 101 → trim general to 11 to stay at 99
GNEWS_PAGE_SIZE = 10  # hard limit on free tier
GNEWS_REQUESTS_PER_CATEGORY: dict[str, int] = {
    "general":       12,
    "world":         12,
    "nation":        11,
    "business":      11,
    "technology":    11,
    "entertainment": 11,
    "sports":        11,
    "science":       10,
    "health":        10,
}  # total = 99 requests → up to 990 articles

# NewsAPI free tier: 100 articles/request, page 1 only, 100 req/day
# 9 categories × 6 keywords = 54 requests → up to 5400 raw, ~1000+ unique after dedup
NEWSAPI_PAGES_PER_KEYWORD = 1   # free plan is locked to page 1
NEWSAPI_PAGE_SIZE         = 100

# Small delay between paginated requests to be a good API citizen
REQUEST_DELAY_SECS = 0.25


# ── Helpers ───────────────────────────────────────────────────────────────────

def _estimate_read_time(title: str, dek: str | None, body: str | None) -> str:
    text = f"{title} {dek or ''} {body or ''}"
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

def _parse_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def _clean_author(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.strip()
    # Drop URL-like values
    if raw.startswith("http") or (len(raw.split()) == 1 and "." in raw):
        return None
    # Take the first name before a comma (e.g. "John Smith, Reuters" → "John Smith")
    name = raw.split(",")[0].strip()
    name = re.sub(r"\(.*?\)", "", name).strip()
    # Reject if it looks like a publication rather than a person
    if len(name) > 60 or name.lower() in {"staff", "editors", "reuters", "ap", "afp"}:
        return None
    return name or None


def _clean_title(raw: str | None) -> str:
    if not raw:
        return ""
    # Strip trailing "- Source Name" appended by NewsAPI
    cleaned = re.sub(r"\s+-\s+[^-]{2,60}$", "", raw.strip())
    return cleaned or raw


def _strip_body(content: str | None, source: str) -> str | None:
    if not content:
        return None
    # GNews:   "... [N chars]"
    # NewsAPI: "text [+N chars]"
    text = re.sub(r"\s*\[[\+\d]+ chars?\]$", "...", content).strip()
    text = re.sub(r"\.\.\.\s*\[\d+ chars\]$", "...", text).strip()
    return text or None


# ── GNews fetcher (paginated) ─────────────────────────────────────────────────

async def fetch_all_gnews(category: str) -> list[dict[str, Any]]:
    """Fetch up to GNEWS_REQUESTS_PER_CATEGORY[category] pages for one category.

    Free tier: 10 articles/request. Each paginated call fetches one page of 10.
    """
    if not settings.gnews_api_key:
        logger.warning("GNEWS_API_KEY not set — skipping GNews")
        return []

    all_articles: list[dict[str, Any]] = []
    gnews_cat = GNEWS_CATEGORY_MAP.get(category, "general")
    max_requests = GNEWS_REQUESTS_PER_CATEGORY.get(category, 10)

    async with httpx.AsyncClient(timeout=30) as client:
        for page in range(1, max_requests + 1):
            try:
                params = {
                    "category": gnews_cat,
                    "max":      GNEWS_PAGE_SIZE,
                    "lang":     "en",
                    "page":     page,
                    "token":    settings.gnews_api_key,
                }
                resp = await client.get(f"{settings.gnews_api_url}/top-headlines", params=params)
                if resp.status_code == 429:
                    logger.warning(f"GNews rate limit hit at page {page} [{category}]")
                    break
                resp.raise_for_status()
                data = resp.json()
                batch = data.get("articles", [])
                if not batch:
                    logger.info(f"GNews [{category}] p{page}: no more articles")
                    break
                all_articles.extend(batch)
                logger.info(f"GNews [{category}] p{page}/{max_requests}: +{len(batch)} ({len(all_articles)} total)")
                if len(batch) < GNEWS_PAGE_SIZE:
                    break  # API returned a partial page — we've exhausted available articles
                await asyncio.sleep(REQUEST_DELAY_SECS)
            except httpx.HTTPError as e:
                logger.error(f"GNews [{category}] p{page} error: {e}")
                break

    return all_articles


# ── NewsAPI fetcher (paginated, /everything) ──────────────────────────────────

async def fetch_all_newsapi(category: str, already_fetched_keywords: set[str]) -> list[dict[str, Any]]:
    """Paginate NewsAPI /everything for keywords mapped to a category."""
    if not settings.newsapi_key:
        logger.warning("NEWSAPI_KEY not set — skipping NewsAPI")
        return []

    keywords = NEWSAPI_KEYWORD_MAP.get(category, [category])
    if isinstance(keywords, str):
        keywords = [keywords]

    all_articles: list[dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=30) as client:
        for keyword in keywords:
            if keyword in already_fetched_keywords:
                logger.info(f"NewsAPI [{category}]: skipping duplicate keyword '{keyword}'")
                continue
            already_fetched_keywords.add(keyword)

            total_available = None
            for page in range(1, NEWSAPI_PAGES_PER_KEYWORD + 1):
                try:
                    params = {
                        "q":        keyword,
                        "language": "en",
                        "sortBy":   "publishedAt",
                        "pageSize": NEWSAPI_PAGE_SIZE,
                        "page":     page,
                        "apiKey":   settings.newsapi_key,
                    }
                    resp = await client.get(f"{settings.newsapi_url}/everything", params=params)

                    if resp.status_code == 426:
                        # Developer plan doesn't support pagination past page 1
                        logger.warning(f"NewsAPI [{category}] for '{keyword}': plan limits pagination at page {page}")
                        break
                    if resp.status_code == 429:
                        logger.warning(f"NewsAPI rate limit hit at page {page} [{category}]")
                        break
                    resp.raise_for_status()
                    data = resp.json()

                    if data.get("status") == "error":
                        logger.warning(f"NewsAPI [{category}] p{page}: {data.get('message')}")
                        break

                    if total_available is None:
                        total_available = data.get("totalResults", 0)

                    batch = data.get("articles", [])
                    if not batch:
                        logger.info(f"NewsAPI [{category}] p{page} for '{keyword}': no more articles")
                        break

                    all_articles.extend(batch)
                    logger.info(f"NewsAPI [{category}] '{keyword}' p{page}: +{len(batch)} ({len(all_articles)}/{total_available} total)")

                    # Stop if we've retrieved everything available
                    if len(all_articles) >= (total_available or 0):
                        break
                    if len(batch) < NEWSAPI_PAGE_SIZE:
                        break

                    await asyncio.sleep(REQUEST_DELAY_SECS)
                except httpx.HTTPError as e:
                    logger.error(f"NewsAPI [{category}] for '{keyword}' p{page} error: {e}")
                    break

    return all_articles


# ── Mappers ───────────────────────────────────────────────────────────────────

def map_gnews_article(raw: dict[str, Any], category: str) -> dict[str, Any]:
    source = raw.get("source", {})
    src_name = source.get("name") or source.get("url") or "GNews"
    article = {
        "id":           str(uuid.uuid4()),
        "title":        _clean_title(raw.get("title")),
        "dek":          raw.get("description"),
        "body":         _strip_body(raw.get("content"), src_name),
        "category":     category,   # raw ingestion category, used by assign_frontend_category
        "source":       src_name,
        "author":       None,       # GNews free tier has no author field
        "url":          raw.get("url"),
        "image_url":    raw.get("image"),
        "published_at": _parse_date(raw.get("publishedAt")),
    }
    article["category"] = assign_frontend_category(article)
    return article


def map_newsapi_article(raw: dict[str, Any], category: str) -> dict[str, Any]:
    source = raw.get("source", {})
    src_name = source.get("name") or "NewsAPI"
    title = _clean_title(raw.get("title"))
    if not title or title.lower() == "[removed]":
        return {}
    article = {
        "id":           str(uuid.uuid4()),
        "title":        title,
        "dek":          raw.get("description"),
        "body":         _strip_body(raw.get("content"), src_name),
        "category":     category,   # raw ingestion category, used by assign_frontend_category
        "source":       src_name,
        "author":       _clean_author(raw.get("author")),
        "url":          raw.get("url"),
        "image_url":    raw.get("urlToImage"),
        "published_at": _parse_date(raw.get("publishedAt")),
    }
    article["category"] = assign_frontend_category(article)
    return article


# ── DB helpers ────────────────────────────────────────────────────────────────

async def article_exists(db: AsyncSession, url: str) -> bool:
    result = await db.execute(select(Article.id).where(Article.url == url))
    return result.first() is not None


async def save_article(
    db: AsyncSession,
    article_data: dict[str, Any],
    embedding: list[float] | None = None,
    scraped_body: list[str] | None = None,
) -> Article | None:
    """Persist a single article.

    - embedding: pre-computed externally for batch efficiency
    - scraped_body: full paragraphs from scraper; falls back to API snippet if None
    """
    if not article_data:
        return None
    url   = article_data.get("url")
    title = article_data.get("title", "").strip()
    if not url or not title:
        return None
    if await article_exists(db, url):
        return None

    import json as _json
    if scraped_body:
        body = _json.dumps(scraped_body)
    else:
        body = article_data.get("body")  # API truncated snippet

    read_time = _estimate_read_time(title, article_data.get("dek"), body)
    plain_text = build_retrieval_text(
        title,
        article_data.get("dek"),
        body=article_data.get("body"),
        scraped_body=scraped_body,
    )
    processed_text = lemmatize_text(plain_text)

    article = Article(
        id=article_data["id"],
        title=title,
        dek=article_data.get("dek"),
        body=body,
        processed_text=processed_text,
        category=article_data["category"],
        source=article_data["source"],
        author=article_data.get("author"),
        read_time=read_time,
        url=url,
        image_url=article_data.get("image_url"),
        published_at=article_data.get("published_at"),
        embedding=embedding,
    )
    db.add(article)
    try:
        await db.flush()
        return article
    except Exception as e:
        await db.rollback()
        logger.debug(f"Skipped duplicate ({url}): {e}")
        return None


# ── BM25 index bootstrap ──────────────────────────────────────────────────────

async def build_bm25_index(db: AsyncSession, *, bump_version: bool = True) -> None:
    """Load all articles from DB and build the in-memory BM25 index."""
    from app.services.bm25 import bm25_index

    all_result = await db.execute(
        select(Article.id, Article.title, Article.dek, Article.category, Article.processed_text)
    )
    rows = all_result.all()
    bm25_index.build(
        [(r[0], r[4] if r[4] else f"{r[1]} {r[2] or ''} {r[3]}") for r in rows]
    )
    if bump_version:
        mark_bm25_rebuilt()


# ── Orchestration ─────────────────────────────────────────────────────────────

async def ingest_category(
    db: AsyncSession,
    category: str,
    _newsapi_done: set[str] | None = None,
) -> dict[str, Any]:
    if _newsapi_done is None:
        _newsapi_done = set()

    raw_articles: list[dict[str, Any]] = []

    # GNews — paginated
    try:
        gnews_raw = await fetch_all_gnews(category)
        raw_articles.extend(map_gnews_article(a, category) for a in gnews_raw)
    except Exception as e:
        logger.error(f"GNews pipeline failed [{category}]: {e}")

    # NewsAPI — paginated /everything
    try:
        newsapi_raw = await fetch_all_newsapi(category, _newsapi_done)
        raw_articles.extend(map_newsapi_article(a, category) for a in newsapi_raw)
    except Exception as e:
        logger.error(f"NewsAPI pipeline failed [{category}]: {e}")

    # Deduplicate by URL before hitting the DB
    seen_urls: set[str] = set()
    unique_articles: list[dict[str, Any]] = []
    for a in raw_articles:
        url = a.get("url")
        if not url or not a.get("title", "").strip():
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)
        unique_articles.append(a)

    fetched  = len(raw_articles)
    skipped  = fetched - len(unique_articles)

    if not unique_articles:
        logger.info(f"✓ [{category}] fetched={fetched} inserted=0 skipped={skipped}")
        return {"category": category, "fetched": fetched, "inserted": 0, "skipped": skipped}

    # ── Concurrent scraping ───────────────────────────────────────────────────
    # Cap to 20 simultaneous HTTP connections to be polite to source servers.
    # Each scrape has a 10s timeout (enforced inside scrape_article_body).
    # Failures return None and fall back to the API snippet — never block ingestion.
    logger.info(f"[{category}] Scraping full bodies for {len(unique_articles)} articles...")
    semaphore = asyncio.Semaphore(20)

    async def _scrape_safe(url: str) -> list[str] | None:
        async with semaphore:
            return await scrape_article_body(url)

    scrape_tasks = [_scrape_safe(a["url"]) for a in unique_articles]
    scraped_bodies: list[list[str] | None] = await asyncio.gather(*scrape_tasks)

    scraped_count = sum(1 for b in scraped_bodies if b)
    logger.info(f"[{category}] Scraped full body for {scraped_count}/{len(unique_articles)} articles")

    # ── Batch embeddings ──────────────────────────────────────────────────────
    logger.info(f"[{category}] Computing embeddings for {len(unique_articles)} candidates...")
    texts_for_embedding = [
        build_retrieval_text(
            a["title"],
            a.get("dek"),
            body=a.get("body"),
            scraped_body=scraped,
        )
        for a, scraped in zip(unique_articles, scraped_bodies)
    ]
    try:
        embeddings = embed_texts(texts_for_embedding)
    except Exception as e:
        logger.warning(f"[{category}] Embedding batch failed, proceeding without embeddings: {e}")
        embeddings = [None] * len(unique_articles)

    # ── Save to DB ────────────────────────────────────────────────────────────
    inserted = 0
    for article_data, emb, scraped in zip(unique_articles, embeddings, scraped_bodies):
        result = await save_article(db, article_data, embedding=emb, scraped_body=scraped)
        if result:
            inserted += 1
        else:
            skipped += 1

    await db.commit()
    logger.info(f"✓ [{category}] fetched={fetched} inserted={inserted} skipped={skipped}")
    return {"category": category, "fetched": fetched, "inserted": inserted, "skipped": skipped}


async def ingest_all_categories(db: AsyncSession) -> list[dict[str, Any]]:
    newsapi_done: set[str] = set()
    results = []
    for category in CATEGORIES:
        stats = await ingest_category(db, category, _newsapi_done=newsapi_done)
        results.append(stats)
    return results
