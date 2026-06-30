"""Keep in-memory BM25 indexes in sync across workers via Redis."""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import get_settings

logger = logging.getLogger("veritas")
settings = get_settings()

BM25_VERSION_KEY = "veritas:bm25_version"
_local_version = 0
_redis = None
_redis_checked = False


def _get_redis():
    global _redis, _redis_checked
    if _redis_checked:
        return _redis
    _redis_checked = True
    try:
        import redis

        _redis = redis.from_url(settings.redis_url, decode_responses=True)
        _redis.ping()
    except Exception as e:
        logger.info("BM25 sync disabled (Redis unavailable): %s", type(e).__name__)
        _redis = None
    return _redis


def mark_bm25_rebuilt() -> None:
    """Call after rebuilding the in-memory BM25 index."""
    global _local_version
    client = _get_redis()
    if client is not None:
        try:
            _local_version = int(client.incr(BM25_VERSION_KEY))
            return
        except Exception as e:
            logger.warning("Failed to bump BM25 version in Redis: %s", e)
    _local_version += 1


async def ensure_bm25_fresh(db: AsyncSession) -> None:
    """Rebuild the local BM25 index when another worker has ingested new articles."""
    global _local_version
    client = _get_redis()
    if client is None:
        return

    try:
        remote_version = int(client.get(BM25_VERSION_KEY) or 0)
    except Exception as e:
        logger.warning("Failed to read BM25 version from Redis: %s", e)
        return

    if remote_version <= _local_version:
        return

    from app.services.ingestion_service import build_bm25_index

    logger.info("BM25 index stale (local=%s remote=%s); rebuilding...", _local_version, remote_version)
    await build_bm25_index(db, bump_version=False)
    _local_version = remote_version
