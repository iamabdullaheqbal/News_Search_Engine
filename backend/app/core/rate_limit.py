"""Redis-backed rate limiting."""
from __future__ import annotations

import functools
import logging

import redis
from fastapi import HTTPException, Request

from app.core.settings import get_settings

logger = logging.getLogger("veritas")
settings = get_settings()

_redis: redis.Redis | None = None

_PERIOD_SECONDS = {"minute": 60, "hour": 3600}


def _get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


class Limiter:
    """Decorator-based rate limiter compatible with slowapi-style usage."""

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

                client_ip = request.client.host if request.client else "unknown"
                key = f"rl:{client_ip}:{request.url.path}"
                try:
                    r = _get_redis()
                    current = r.incr(key)
                    if current == 1:
                        r.expire(key, window)
                    if current > max_requests:
                        raise HTTPException(status_code=429, detail="Too many requests")
                except HTTPException:
                    raise
                except Exception:
                    logger.warning("Rate limit check failed — allowing request", exc_info=True)

                return await func(*args, **kwargs)

            return wrapper

        return decorator


limiter = Limiter()
