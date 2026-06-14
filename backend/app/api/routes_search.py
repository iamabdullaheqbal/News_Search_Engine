import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import limiter
from app.db.database import get_db
from app.schemas.search import SearchResponse
from app.services.search import search_articles

logger = logging.getLogger("veritas")
router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
@limiter.limit("30/minute")
async def search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=200),
    category: Optional[str] = Query(default=None, max_length=100),
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    try:
        total, results = await search_articles(q, db, category=category, limit=limit, offset=offset)
        return SearchResponse(query=q, total=total, results=results)
    except Exception:
        logger.error("Search error", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed")
