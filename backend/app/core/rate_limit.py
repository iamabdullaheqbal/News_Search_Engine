"""Redis-backed rate limiting."""
from __future__ import annotations

import functools
import logging
import time

import redis
from fastapi import HTTPException, Request

from app.core.settings import get_settings

logger = logging.getLogger("veritas")
settings = get_settings()

_redis: redis.Redis | None = None
_redis_unavailable_until: float = 0.0   # epoch seconds; skip retries until this time
_REDIS_RETRY_INTERVAL = 30.0            # re-attempt connection every 30 s

_PERIOD_SECONDS = {"minute": 60, "hour": 3600}


def _get_redis() -> redis.Redis | None:
    """Return the Redis client, or None if Redis is known to be unavailable."""
    global _redis, _redis_unavailable_until

    now = time.monotonic()
    if now < _redis_unavailable_until:
        return None

    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def _mark_redis_unavailable() -> None:
    """Called when a Redis operation fails; suppresses retries for a short window."""
    global _redis, _redis_unavailable_until
    _redis = None  # force reconnect on next attempt
    _redis_unavailable_until = time.monotonic() + _REDIS_RETRY_INTERVAL


class Limiter:
    """Decorator-based rate limiter. Skips silently when Redis is unavailable."""

    def limit(self, rule: str):
        count_str, _, period = rule.partition("/")
        max_requests = int(count_str)
        window = _PERIOD_SECONDS.get(period, 60)

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                request: Request | None = kwargs.get("request")
                if request is None:
                    for arg in args:
                        if isinstance(arg, Request):
                            request = arg
                            break
                if request is None:
                    return await func(*args, **kwargs)

                r = _get_redis()
                if r is not None:
                    client_ip = request.client.host if request.client else "unknown"
                    key = f"rl:{client_ip}:{request.url.path}"
                    try:
                        current = r.incr(key)
                        if current == 1:
                            r.expire(key, window)
                        if current > max_requests:
                            raise HTTPException(status_code=429, detail="Too many requests")
                    except HTTPException:
                        raise
                    except Exception as e:
                        _mark_redis_unavailable()
                        logger.warning(
                            "Rate limiter: Redis unavailable (%s). "
                            "Rate limiting disabled for %ds.",
                            type(e).__name__,
                            _REDIS_RETRY_INTERVAL,
                        )

                return await func(*args, **kwargs)

            return wrapper

        return decorator


limiter = Limiter()
