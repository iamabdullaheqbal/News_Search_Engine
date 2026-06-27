import json
import logging
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import verify_ingest_key
from app.core.rate_limit import limiter
from app.core.settings import get_settings
from app.core.validators import validate_interest_topics
from app.db.database import get_db
from app.db.models import Article, User
from app.schemas.article import ArticleOut, ArticleDetail
from app.schemas.auth import FollowsRequest
from app.services.auth import get_current_user_optional
from app.services.ingestion_service import (
    CATEGORIES,
    ingest_all_categories,
    ingest_category,
)
from app.services.interest import get_user_interests, parse_cookie_interests
from app.services.search import (
    get_article_by_id,
    get_articles_by_category,
    get_feed_articles,
    get_trending_titles,
)

logger = logging.getLogger("veritas")
router = APIRouter(prefix="/api/articles", tags=["articles"])
settings = get_settings()

FOLLOWS_COOKIE = "veritas_follows"


# ---------------------------------------------------------------------------
# Public listing endpoints
# ---------------------------------------------------------------------------

@router.get("/categories", response_model=list[str])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Return all distinct categories present in the articles table, sorted."""
    result = await db.execute(
        select(Article.category).distinct().order_by(Article.category)
    )
    return [row[0] for row in result.all()]


@router.get("/", response_model=list[ArticleOut])
async def list_articles(
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Article).order_by(Article.published_at.desc())
    if category:
        stmt = stmt.where(Article.category == category.upper())
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    articles = result.scalars().all()
    from app.services.search import _to_out
    return [_to_out(a) for a in articles]


@router.get("/count")
async def article_count(
    category: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(func.count()).select_from(Article)
    if category:
        stmt = stmt.where(Article.category == category.upper())
    result = await db.execute(stmt)
    return {"count": result.scalar_one()}


@router.get("/feed", response_model=list[ArticleOut])
async def feed(
    limit: int = Query(default=20, ge=1, le=50),
    veritas_follows: Optional[str] = Cookie(default=None),
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    if user:
        topics = await get_user_interests(user, db)
    else:
        topics = validate_interest_topics(parse_cookie_interests(veritas_follows))
    return await get_feed_articles(topics, db, limit=limit)


@router.get("/trending", response_model=list[str])
async def trending(
    limit: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    return await get_trending_titles(db, limit=limit)


@router.get("/category/{category}", response_model=list[ArticleOut])
async def by_category(
    category: str,
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    _, articles = await get_articles_by_category(category, db, limit=limit, offset=offset)
    return articles


# ---------------------------------------------------------------------------
# Guest follow preferences (HttpOnly cookie) — must be before /{article_id}
# ---------------------------------------------------------------------------

@router.get("/follows")
async def get_follows(veritas_follows: Optional[str] = Cookie(default=None)):
    topics = validate_interest_topics(parse_cookie_interests(veritas_follows))
    return {"topics": topics}


@router.post("/follows")
async def set_follows(body: FollowsRequest, response: Response):
    topics = validate_interest_topics(body.topics)
    response.set_cookie(
        key=FOLLOWS_COOKIE,
        value=json.dumps(topics),
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=31536000,
        path="/",
    )
    return {"topics": topics}


@router.get("/{article_id}", response_model=ArticleDetail)
async def article_detail(article_id: str, db: AsyncSession = Depends(get_db)):
    article = await get_article_by_id(article_id, db)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


# ---------------------------------------------------------------------------
# Ingestion endpoint (admin only)
# ---------------------------------------------------------------------------

@router.post("/ingest")
@limiter.limit("5/minute")
async def ingest(
    request: Request,
    category: Optional[str] = Query(
        default=None,
        description=f"One of: {', '.join(CATEGORIES)}",
    ),
    max_results: int = Query(default=25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_ingest_key),
):
    """Trigger article ingestion from GNews and NewsAPI. Requires X-Ingest-Key header."""
    if category and category.lower() not in CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid category '{category}'. Valid: {CATEGORIES}",
        )
    try:
        if category:
            stats = await ingest_category(db, category.lower())
            return {"results": [stats]}
        stats = await ingest_all_categories(db, max_results)
        return {"results": stats}
    except Exception:
        logger.error("Ingestion endpoint error", exc_info=True)
        raise HTTPException(status_code=500, detail="Ingestion failed")
