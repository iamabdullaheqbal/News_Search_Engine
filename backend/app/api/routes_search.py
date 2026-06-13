import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.database import get_db
from app.schemas.search import SearchResponse
from app.services.search import search_articles

logger = logging.getLogger("veritas")
router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    try:
        total, results = await search_articles(q, db, category=category, limit=limit, offset=offset)
        return SearchResponse(query=q, total=total, results=results)
    except Exception as e:
        logger.error(f"Search error for '{q}': {e}", exc_info=True)
        raise
