"""News article ingestion from GNews and NewsAPI."""
from __future__ import annotations

import logging
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

# Canonical categories used across the app
CATEGORIES = [
    "general", "world", "nation", "business",
    "technology", "entertainment", "sports", "science", "health",
]

# NewsAPI doesn't have 'world' or 'nation' — map them to 'general'
NEWSAPI_CATEGORY_MAP: dict[str, str] = {
    "general": "general",
    "world": "general",
    "nation": "general",
    "business": "business",
    "technology": "technology",
    "entertainment": "entertainment",
    "sports": "sports",
    "science": "science",
    "health": "health",
}


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

def _parse_date(raw_date: str | None) -> datetime | None:
    if not raw_date:
        return None
    try:
        normalized = raw_date.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).astimezone(timezone.utc)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# API fetchers
# ---------------------------------------------------------------------------

async def fetch_from_gnews(category: str, max_results: int = 25) -> list[dict[str, Any]]:
    if not settings.gnews_api_key:
        logger.warning("GNEWS_API_KEY not set, skipping GNews fetch")
        return []
    params = {
        "category": category,
        "max": max_results,
        "lang": "en",
        "token": settings.gnews_api_key,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{settings.gnews_api_url}/top-headlines", params=params)
        resp.raise_for_status()
        return resp.json().get("articles", [])


async def fetch_from_newsapi(category: str, max_results: int = 25) -> list[dict[str, Any]]:
    if not settings.newsapi_key:
        logger.warning("NEWSAPI_KEY not set, skipping NewsAPI fetch")
        return []
    mapped = NEWSAPI_CATEGORY_MAP.get(category, "general")
    params = {
        "category": mapped,
        "country": "us",
        "pageSize": max_results,
        "apiKey": settings.newsapi_key,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{settings.newsapi_url}/top-headlines", params=params)
        resp.raise_for_status()
        return resp.json().get("articles", [])


# ---------------------------------------------------------------------------
# Mappers
# ---------------------------------------------------------------------------

def map_gnews_article(raw: dict[str, Any], category: str) -> dict[str, Any]:
    source = raw.get("source", {})
    return {
        "id": str(uuid.uuid4()),
        "title": raw.get("title") or "",
        "dek": raw.get("description"),
        "body": None,
        "category": category.upper(),
        "source": source.get("name") or source.get("url") or "GNews",
        "author": None,
        "url": raw.get("url"),
        "image_url": raw.get("image"),
        "published_at": _parse_date(raw.get("publishedAt")),
    }


def map_newsapi_article(raw: dict[str, Any], category: str) -> dict[str, Any]:
    source = raw.get("source", {})
    return {
        "id": str(uuid.uuid4()),
        "title": raw.get("title") or "",
        "dek": raw.get("description"),
        "body": None,
        "category": category.upper(),
        "source": source.get("name") or "NewsAPI",
        "author": raw.get("author"),
        "url": raw.get("url"),
        "image_url": raw.get("urlToImage"),
        "published_at": _parse_date(raw.get("publishedAt")),
    }


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

async def article_exists(db: AsyncSession, url: str) -> bool:
    result = await db.execute(select(Article.id).where(Article.url == url))
    return result.first() is not None


async def save_article(db: AsyncSession, article_data: dict[str, Any]) -> Article | None:
    url = article_data.get("url")
    title = article_data.get("title", "").strip()

    if not url or not title:
        return None
    if await article_exists(db, url):
        return None

    # Generate embedding for the article
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
        await db.flush()  # catch unique violations early
        return article
    except Exception as e:
        await db.rollback()
        logger.debug(f"Skipped duplicate article ({url}): {e}")
        return None


# ---------------------------------------------------------------------------
# Ingestion orchestration
# ---------------------------------------------------------------------------

async def ingest_category(
    db: AsyncSession, category: str, max_results: int = 25
) -> dict[str, Any]:
    fetched = 0
    inserted = 0
    skipped = 0

    raw_articles: list[dict[str, Any]] = []

    # Fetch from GNews
    try:
        gnews_raw = await fetch_from_gnews(category, max_results)
        mapped = [map_gnews_article(a, category) for a in gnews_raw]
        raw_articles.extend(mapped)
    except httpx.HTTPError as e:
        logger.error(f"GNews fetch failed for '{category}': {e}")

    # Fetch from NewsAPI
    try:
        newsapi_raw = await fetch_from_newsapi(category, max_results)
        mapped = [map_newsapi_article(a, category) for a in newsapi_raw]
        raw_articles.extend(mapped)
    except httpx.HTTPError as e:
        logger.error(f"NewsAPI fetch failed for '{category}': {e}")

    fetched = len(raw_articles)

    # Dedupe by URL within this batch before hitting the DB
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

    logger.info(f"[{category}] fetched={fetched} inserted={inserted} skipped={skipped}")
    return {"category": category, "fetched": fetched, "inserted": inserted, "skipped": skipped}


async def ingest_all_categories(
    db: AsyncSession, max_results: int = 25
) -> list[dict[str, Any]]:
    results = []
    for category in CATEGORIES:
        stats = await ingest_category(db, category, max_results)
        results.append(stats)
    return results
