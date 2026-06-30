"""Hybrid search: BM25 + semantic (pgvector) + cross-encoder reranking."""
from __future__ import annotations

import json
import logging
import math
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.sanitize import sanitize_image_url
from app.db.models import Article, ReadHistory
from app.schemas.article import ArticleDetail, ArticleOut
from app.services.bm25 import bm25_index
from app.services.bm25_sync import ensure_bm25_fresh
from app.services.embedding import embed_query
from app.services.ml_executor import run_ml
from app.services.reranker import rerank
from app.services.text_processing import build_retrieval_text

logger = logging.getLogger("veritas")

_BM25_K = 30
_SEM_K = 30
_RERANK_K = 20
_RRF_K = 60


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


def _format_live_time(dt: datetime | None) -> str:
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%H:%M")


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


def _article_rerank_text(article: Article) -> str:
    return f"{build_retrieval_text(article.title, article.dek, article.body)} {article.category}"


def _rrf_merge(
    bm25_hits: list[tuple[str, float]],
    sem_ids: list[str],
    top_k: int,
) -> list[str]:
    scores: dict[str, float] = {}
    for rank, (article_id, _) in enumerate(bm25_hits):
        scores[article_id] = scores.get(article_id, 0.0) + 1.0 / (_RRF_K + rank + 1)
    for rank, article_id in enumerate(sem_ids):
        scores[article_id] = scores.get(article_id, 0.0) + 1.0 / (_RRF_K + rank + 1)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [article_id for article_id, _ in ranked[:top_k]]


async def search_articles(
    query: str,
    db: AsyncSession,
    category: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[int, list[ArticleOut]]:
    await ensure_bm25_fresh(db)

    bm25_hits = bm25_index.search(query, top_k=_BM25_K)
    sem_ids: list[str] = []
    try:
        q_vec = await run_ml(embed_query, query)
        stmt = (
            select(Article.id)
            .where(Article.embedding.isnot(None))
            .order_by(Article.embedding.cosine_distance(q_vec))
            .limit(_SEM_K)
        )
        sem_result = await db.execute(stmt)
        sem_ids = [row[0] for row in sem_result.all()]
    except Exception as e:
        logger.warning("Semantic search unavailable, falling back to BM25 only: %s", e)

    candidate_ids = _rrf_merge(bm25_hits, sem_ids, top_k=_BM25_K + _SEM_K)
    if not candidate_ids:
        return 0, []

    stmt = select(Article).where(Article.id.in_(candidate_ids))
    if category:
        stmt = stmt.where(Article.category == category.upper())
    result = await db.execute(stmt)
    articles = list(result.scalars().all())
    if not articles:
        return 0, []

    id_map = {article.id: article for article in articles}

    try:
        candidates_for_rerank = [
            (article.id, _article_rerank_text(article)) for article in articles
        ]
        ranked = await run_ml(rerank, query, candidates_for_rerank, _RERANK_K)
        ranked_ids = [aid for aid, _ in ranked]
        ordered = [id_map[aid] for aid in ranked_ids if aid in id_map]
        reranked_set = set(ranked_ids)
        rrf_order = {aid: idx for idx, aid in enumerate(candidate_ids)}
        remaining = sorted(
            (article for article in articles if article.id not in reranked_set),
            key=lambda article: rrf_order.get(article.id, len(candidate_ids)),
        )
        ordered.extend(remaining)
    except Exception as e:
        logger.warning("Reranker unavailable, falling back to RRF ordering: %s", e)
        ordered = [id_map[aid] for aid in candidate_ids if aid in id_map]

    total = len(ordered)
    page = ordered[offset : offset + limit]
    return total, [_to_out(article) for article in page]


async def get_articles_by_category(
    category: str, db: AsyncSession, limit: int = 20, offset: int = 0
) -> tuple[int, list[ArticleOut]]:
    count_stmt = (
        select(func.count())
        .select_from(Article)
        .where(Article.category == category.upper())
    )
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = (
        select(Article)
        .where(Article.category == category.upper())
        .order_by(Article.published_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    articles = result.scalars().all()
    return total, [_to_out(article) for article in articles]


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
    user_id: int | None = None,
) -> tuple[int, list[ArticleOut]]:
    """
    Personalized feed: recency-weighted ranking with category diversity
    and deprioritization of articles the user has already read.
    """
    read_ids: set[str] = set()
    if user_id is not None:
        read_result = await db.execute(
            select(ReadHistory.article_id).where(ReadHistory.user_id == user_id)
        )
        read_ids = {row[0] for row in read_result.all()}

    base_stmt = select(Article)
    if topics:
        base_stmt = base_stmt.where(Article.category.in_([topic.upper() for topic in topics]))

    pool_size = max(limit * 5, 100)
    stmt = base_stmt.order_by(Article.published_at.desc()).limit(pool_size)
    result = await db.execute(stmt)
    candidates = list(result.scalars().all())
    if not candidates:
        return 0, []

    now = datetime.now(timezone.utc)
    half_life_hours = 24.0

    def feed_score(article: Article) -> float:
        if article.published_at is None:
            recency = 0.0
        else:
            pub = article.published_at
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            age_hours = max(0.0, (now - pub).total_seconds() / 3600)
            recency = math.exp(-age_hours * math.log(2) / half_life_hours)
        if article.id in read_ids:
            recency *= 0.35
        return recency

    scored = sorted(candidates, key=feed_score, reverse=True)

    diversified: list[Article] = []
    category_run: dict[str, int] = {}
    deferred: list[Article] = []

    for article in scored:
        cat = article.category
        run = category_run.get(cat, 0)
        if run < 2:
            diversified.append(article)
            category_run[cat] = run + 1
            for key in list(category_run):
                if key != cat:
                    category_run[key] = max(0, category_run[key] - 1)
        else:
            deferred.append(article)

    diversified.extend(deferred)

    total = len(diversified)
    page = diversified[offset : offset + limit]
    return total, [_to_out(article) for article in page]


async def get_trending_titles(db: AsyncSession, limit: int = 5) -> list[str]:
    """Most-read article titles in the last 7 days, falling back to latest headlines."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    trending_stmt = (
        select(Article.title, func.count(ReadHistory.id).label("reads"))
        .join(ReadHistory, ReadHistory.article_id == Article.id)
        .where(ReadHistory.read_at >= cutoff)
        .group_by(Article.id, Article.title)
        .order_by(func.count(ReadHistory.id).desc(), Article.published_at.desc())
        .limit(limit)
    )
    result = await db.execute(trending_stmt)
    titles = [row[0] for row in result.all()]

    if len(titles) >= limit:
        return titles

    remaining = limit - len(titles)
    recent_stmt = select(Article.title).order_by(Article.published_at.desc()).limit(remaining)
    if titles:
        recent_stmt = recent_stmt.where(Article.title.notin_(titles))
    recent_result = await db.execute(recent_stmt)
    titles.extend(row[0] for row in recent_result.all())
    return titles


async def get_live_wire(db: AsyncSession, limit: int = 5) -> list[dict[str, str]]:
    """Latest headlines with publication time for the sidebar live wire."""
    result = await db.execute(
        select(Article.title, Article.published_at)
        .order_by(Article.published_at.desc())
        .limit(limit)
    )
    items: list[dict[str, str]] = []
    for title, published_at in result.all():
        items.append({"time": _format_live_time(published_at), "text": title})
    return items
