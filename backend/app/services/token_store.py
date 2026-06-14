"""Server-side refresh token tracking and access-token revocation via Redis."""
from __future__ import annotations

import logging

import redis

from app.core.settings import get_settings

logger = logging.getLogger("veritas")
settings = get_settings()

_redis: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def store_refresh_token(jti: str, user_id: int) -> None:
    ttl = settings.refresh_token_expire_days * 86400
    _get_redis().setex(f"refresh:{jti}", ttl, str(user_id))


def consume_refresh_token(jti: str) -> int | None:
    """Atomically validate and revoke a refresh token (rotation). Returns user_id or None."""
    user_id = _get_redis().getdel(f"refresh:{jti}")
    return int(user_id) if user_id else None


def revoke_refresh_token(jti: str) -> None:
    _get_redis().delete(f"refresh:{jti}")


def blacklist_access_token(jti: str) -> None:
    ttl = settings.access_token_expire_minutes * 60
    _get_redis().setex(f"deny:{jti}", ttl, "1")


def is_access_token_blacklisted(jti: str) -> bool:
    if not jti:
        return False
    try:
        return _get_redis().exists(f"deny:{jti}") > 0
    except Exception:
        logger.warning("Redis unavailable for token blacklist check", exc_info=True)
        return False
