"""News article ingestion — maxing out both API quotas.

Daily budget:
  GNews   100 req/day  → 9 categories × 10 pages × 10 articles = 90 req  → ~900  articles
  NewsAPI 1000 req/day → 7 keywords  × 140 pages × 100 articles = 980 req → ~98k articles possible
                         (stops early when API returns no new results)
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

from app.core.settings import get_settings
from app.db.models import Article
from app.services.embedding import embed_texts

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

# NewsAPI /everything keyword per category — broader coverage than /top-headlines
NEWSAPI_KEYWORD_MAP: dict[str, str] = {
    "general":       "breaking news today",
    "world":         "world news international",
    "nation":        "US national news",
    "business":      "business economy finance",
    "technology":    "technology AI software",
    "entertainment": "entertainment movies music",
    "sports":        "sports NFL NBA soccer",
    "science":       "science research discovery",
    "health":        "health medicine medical",
}

# GNews: 10 pages × 10 articles = 100 per category, 9 cats = 90 requests
GNEWS_PAGES_PER_CATEGORY = 10
GNEWS_PAGE_SIZE          = 10

# NewsAPI: 140 pages × 100 articles = 14,000 per keyword, 7 unique = 980 requests
NEWSAPI_PAGES_PER_KEYWORD = 140
NEWSAPI_PAGE_SIZE         = 100

# Small delay between paginated requests to be a good API citizen
REQUEST_DELAY_SECS = 0.25


# ── Helpers ───────────────────────────────────────────────────────────────────

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
    """Fetch up to GNEWS_PAGES_PER_CATEGORY pages for one category."""
    if not settings.gnews_api_key:
        logger.warning("GNEWS_API_KEY not set — skipping GNews")
        return []

    all_articles: list[dict[str, Any]] = []
    gnews_cat = GNEWS_CATEGORY_MAP.get(category, "general")

    async with httpx.AsyncClient(timeout=30) as client:
        for page in range(1, GNEWS_PAGES_PER_CATEGORY + 1):
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
                logger.info(f"GNews [{category}] p{page}: +{len(batch)} ({len(all_articles)} total)")
                if len(batch) < GNEWS_PAGE_SIZE:
                    break  # last page
                await asyncio.sleep(REQUEST_DELAY_SECS)
            except httpx.HTTPError as e:
                logger.error(f"GNews [{category}] p{page} error: {e}")
                break

    return all_articles


# ── NewsAPI fetcher (paginated, /everything) ──────────────────────────────────

async def fetch_all_newsapi(category: str, already_fetched_keywords: set[str]) -> list[dict[str, Any]]:
    """Paginate NewsAPI /everything for a keyword, up to NEWSAPI_PAGES_PER_KEYWORD pages."""
    if not settings.newsapi_key:
        logger.warning("NEWSAPI_KEY not set — skipping NewsAPI")
        return []

    keyword = NEWSAPI_KEYWORD_MAP.get(category, category)

    # Avoid re-fetching the same keyword (world + nation both map to same kw)
    if keyword in already_fetched_keywords:
        logger.info(f"NewsAPI [{category}]: skipping duplicate keyword '{keyword}'")
        return []
    already_fetched_keywords.add(keyword)

    all_articles: list[dict[str, Any]] = []
    total_available = None

    async with httpx.AsyncClient(timeout=30) as client:
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
                    logger.warning(f"NewsAPI [{category}]: plan limits pagination at page {page}")
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
                    logger.info(f"NewsAPI [{category}] p{page}: no more articles")
                    break

                all_articles.extend(batch)
                logger.info(f"NewsAPI [{category}] p{page}: +{len(batch)} ({len(all_articles)}/{total_available} total)")

                # Stop if we've retrieved everything available
                if len(all_articles) >= (total_available or 0):
                    break
                if len(batch) < NEWSAPI_PAGE_SIZE:
                    break

                await asyncio.sleep(REQUEST_DELAY_SECS)
            except httpx.HTTPError as e:
                logger.error(f"NewsAPI [{category}] p{page} error: {e}")
                break

    return all_articles


# ── Mappers ───────────────────────────────────────────────────────────────────

def map_gnews_article(raw: dict[str, Any], category: str) -> dict[str, Any]:
    source = raw.get("source", {})
    src_name = source.get("name") or source.get("url") or "GNews"
    return {
        "id":           str(uuid.uuid4()),
        "title":        _clean_title(raw.get("title")),
        "dek":          raw.get("description"),
        "body":         _strip_body(raw.get("content"), src_name),
        "category":     category.upper(),
        "source":       src_name,
        "author":       None,   # GNews free tier has no author field
        "url":          raw.get("url"),
        "image_url":    raw.get("image"),
        "published_at": _parse_date(raw.get("publishedAt")),
    }


def map_newsapi_article(raw: dict[str, Any], category: str) -> dict[str, Any]:
    source = raw.get("source", {})
    src_name = source.get("name") or "NewsAPI"
    title = _clean_title(raw.get("title"))
    if not title or title.lower() == "[removed]":
        return {}
    return {
        "id":           str(uuid.uuid4()),
        "title":        title,
        "dek":          raw.get("description"),
        "body":         _strip_body(raw.get("content"), src_name),
        "category":     category.upper(),
        "source":       src_name,
        "author":       _clean_author(raw.get("author")),
        "url":          raw.get("url"),
        "image_url":    raw.get("urlToImage"),
        "published_at": _parse_date(raw.get("publishedAt")),
    }


# ── DB helpers ────────────────────────────────────────────────────────────────

async def article_exists(db: AsyncSession, url: str) -> bool:
    result = await db.execute(select(Article.id).where(Article.url == url))
    return result.first() is not None


async def save_article(db: AsyncSession, article_data: dict[str, Any]) -> Article | None:
    if not article_data:
        return None
    url   = article_data.get("url")
    title = article_data.get("title", "").strip()
    if not url or not title:
        return None
    if await article_exists(db, url):
        return None

    text_for_embedding = f"{title} {article_data.get('dek') or ''}"
    try:
        embedding = embed_texts([text_for_embedding])[0]
    except Exception:
        embedding = None

    article = Article(
        id=article_data["id"],
        title=title,
        dek=article_data.get("dek"),
        body=article_data.get("body"),
        category=article_data["category"],
        source=article_data["source"],
        author=article_data.get("author"),
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

    fetched  = len(raw_articles)
    inserted = 0
    skipped  = 0
    seen_urls: set[str] = set()

    for article_data in raw_articles:
        url = article_data.get("url")
        if not url or url in seen_urls:
            skipped += 1
            continue
        seen_urls.add(url)
        result = await save_article(db, article_data)
        if result:
            inserted += 1
        else:
            skipped += 1

    await db.commit()
    logger.info(f"✓ [{category}] fetched={fetched} inserted={inserted} skipped={skipped}")
    return {"category": category, "fetched": fetched, "inserted": inserted, "skipped": skipped}


async def ingest_all_categories(
    db: AsyncSession,
    max_results: int | None = None,   # kept for API compat, ignored (always uses max)
) -> list[dict[str, Any]]:
    newsapi_done: set[str] = set()
    results = []
    for category in CATEGORIES:
        stats = await ingest_category(db, category, _newsapi_done=newsapi_done)
        results.append(stats)
    return results
