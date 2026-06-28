"""Hybrid search: BM25 + semantic (pgvector) + cross-encoder reranking."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.sanitize import sanitize_image_url
from app.db.models import Article
from app.schemas.article import ArticleDetail, ArticleOut
from app.services.bm25 import bm25_index
from app.services.embedding import embed_query
from app.services.reranker import rerank

logger = logging.getLogger("veritas")

_BM25_K = 30
_SEM_K = 30
_RERANK_K = 20


def _relative_time(dt: datetime | None) -> str:
    if dt is None:
        return ""
    now = datetime.now(timezone.utc)
    diff = now - dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else now - dt
    secs = int(diff.total_seconds())
    if secs < 3600:
        mins = max(1, secs // 60)
        return f"{mins} minute{'s' if mins != 1 else ''} ago"
    if secs < 86400:
        hrs = secs // 3600
        return f"{hrs} hour{'s' if hrs != 1 else ''} ago"
    days = secs // 86400
    return f"{days} day{'s' if days != 1 else ''} ago"


def _to_out(article: Article) -> ArticleOut:
    return ArticleOut(
        id=article.id,
        title=article.title,
        dek=article.dek,
        category=article.category,
        source=article.source,
        author=article.author,
        read_time=article.read_time,
        image_url=sanitize_image_url(article.image_url),
        published_at=article.published_at,
        timestamp=_relative_time(article.published_at),
    )


def _to_detail(article: Article) -> ArticleDetail:
    body: list[str] | None = None
    if article.body:
        try:
            body = json.loads(article.body)
        except Exception:
            body = [article.body]
    out = _to_out(article)
    return ArticleDetail(**out.model_dump(), body=body)


async def search_articles(
    query: str,
    db: AsyncSession,
    category: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[int, list[ArticleOut]]:
    bm25_hits = bm25_index.search(query, top_k=_BM25_K)
    bm25_ids = {aid for aid, _ in bm25_hits}

    sem_ids: set[str] = set()
    try:
        q_vec = embed_query(query)
        stmt = (
            select(Article.id)
            .where(Article.embedding.isnot(None))
            .order_by(Article.embedding.cosine_distance(q_vec))
            .limit(_SEM_K)
        )
        sem_result = await db.execute(stmt)
        sem_ids = {row[0] for row in sem_result.all()}
    except Exception as e:
        logger.warning(f"Semantic search unavailable, falling back to BM25 only: {e}")

    candidate_ids = list(bm25_ids | sem_ids)
    if not candidate_ids:
        return 0, []

    stmt = select(Article).where(Article.id.in_(candidate_ids))
    if category:
        stmt = stmt.where(Article.category == category.upper())
    result = await db.execute(stmt)
    articles = list(result.scalars().all())

    if not articles:
        return 0, []

    try:
        candidates_for_rerank = [
            (a.id, f"{a.title} {a.dek or ''} {a.category}") for a in articles
        ]
        ranked = rerank(query, candidates_for_rerank, top_k=_RERANK_K)
        ranked_ids = [aid for aid, _ in ranked]
        id_map = {a.id: a for a in articles}
        ordered = [id_map[aid] for aid in ranked_ids if aid in id_map]
        reranked_set = set(ranked_ids)
        ordered += [a for a in articles if a.id not in reranked_set]
    except Exception as e:
        logger.warning(f"Reranker unavailable, falling back to BM25 ordering: {e}")
        bm25_score_map = {aid: score for aid, score in bm25_hits}
        ordered = sorted(articles, key=lambda a: bm25_score_map.get(a.id, 0.0), reverse=True)

    total = len(ordered)
    page = ordered[offset : offset + limit]
    return total, [_to_out(a) for a in page]


async def get_articles_by_category(
    category: str, db: AsyncSession, limit: int = 20, offset: int = 0
) -> tuple[int, list[ArticleOut]]:
    stmt = (
        select(Article)
        .where(Article.category == category.upper())
        .order_by(Article.published_at.desc())
    )
    result = await db.execute(stmt)
    articles = result.scalars().all()
    total = len(articles)
    page = articles[offset : offset + limit]
    return total, [_to_out(a) for a in page]


async def get_article_by_id(article_id: str, db: AsyncSession) -> ArticleDetail | None:
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        return None
    return _to_detail(article)


async def get_feed_articles(
    topics: list[str],
    db: AsyncSession,
    limit: int = 20,
) -> list[ArticleOut]:
    stmt = select(Article).order_by(Article.published_at.desc())
    if topics:
        stmt = stmt.where(Article.category.in_([t.upper() for t in topics]))
    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    return [_to_out(a) for a in result.scalars().all()]


async def get_trending_titles(db: AsyncSession, limit: int = 5) -> list[str]:
    result = await db.execute(
        select(Article.title).order_by(Article.published_at.desc()).limit(limit)
    )
    return [row[0] for row in result.all()]
