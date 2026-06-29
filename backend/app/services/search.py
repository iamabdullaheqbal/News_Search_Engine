"""Hybrid search: BM25 + semantic (pgvector) + cross-encoder reranking."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
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
    # Count total matching articles
    count_stmt = (
        select(func.count())
        .select_from(Article)
        .where(Article.category == category.upper())
    )
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch only the requested page via SQL LIMIT/OFFSET
    stmt = (
        select(Article)
        .where(Article.category == category.upper())
        .order_by(Article.published_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    articles = result.scalars().all()
    return total, [_to_out(a) for a in articles]


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
    offset: int = 0,
) -> tuple[int, list[ArticleOut]]:
    """
    Fetch personalized feed with recency-weighted diversity.

    Ranking approach:
      - Score = recency_score * diversity_boost
      - recency_score: exponential decay, half-life 24h → recent articles score near 1.0
      - diversity_boost: penalises same-category back-to-back runs to spread topics
    """
    from datetime import datetime, timezone
    import math

    base_stmt = select(Article)
    if topics:
        base_stmt = base_stmt.where(Article.category.in_([t.upper() for t in topics]))

    # Fetch a larger candidate pool (5× limit) so ranking has something to work with
    pool_size = max(limit * 5, 100)
    stmt = base_stmt.order_by(Article.published_at.desc()).limit(pool_size)
    result = await db.execute(stmt)
    candidates = list(result.scalars().all())

    if not candidates:
        return 0, []

    now = datetime.now(timezone.utc)
    half_life_hours = 24.0

    def recency_score(article: Article) -> float:
        if article.published_at is None:
            return 0.0
        pub = article.published_at
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        age_hours = max(0.0, (now - pub).total_seconds() / 3600)
        return math.exp(-age_hours * math.log(2) / half_life_hours)

    # Sort by recency score descending
    scored = sorted(candidates, key=recency_score, reverse=True)

    # Diversity pass — limit consecutive same-category articles to 2
    diversified: list[Article] = []
    category_run: dict[str, int] = {}
    deferred: list[Article] = []

    for article in scored:
        cat = article.category
        run = category_run.get(cat, 0)
        if run < 2:
            diversified.append(article)
            category_run[cat] = run + 1
            # Reset other category counters to allow them again
            for k in list(category_run):
                if k != cat:
                    category_run[k] = max(0, category_run[k] - 1)
        else:
            deferred.append(article)

    # Append deferred articles at the end so nothing is lost
    diversified.extend(deferred)

    total = len(diversified)
    page = diversified[offset: offset + limit]
    return total, [_to_out(a) for a in page]


async def get_trending_titles(db: AsyncSession, limit: int = 5) -> list[str]:
    result = await db.execute(
        select(Article.title).order_by(Article.published_at.desc()).limit(limit)
    )
    return [row[0] for row in result.all()]
