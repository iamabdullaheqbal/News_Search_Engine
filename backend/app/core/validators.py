"""Shared input validation helpers.

Valid interest topics are loaded from the DB at startup via refresh_valid_topics()
and cached in memory. The hardcoded fallback covers the case where the DB is not
yet reachable (e.g. first boot before create_all runs).
"""
from __future__ import annotations

_FALLBACK_TOPICS = frozenset({
    "POLITICS", "ECONOMY", "TECH", "CLIMATE", "CULTURE",
    "SCIENCE", "MARKETS", "HEALTH", "SPORTS",
})

MAX_INTERESTS = 20

# Populated at startup by refresh_valid_topics(); falls back to _FALLBACK_TOPICS
_valid_topics: frozenset[str] = _FALLBACK_TOPICS


async def refresh_valid_topics(db) -> None:
    """Query distinct categories from Article table and update the in-memory set."""
    global _valid_topics
    try:
        from sqlalchemy import select
        from app.db.models import Article
        result = await db.execute(select(Article.category).distinct())
        topics = frozenset(row[0] for row in result.all() if row[0])
        if topics:
            _valid_topics = topics
    except Exception:
        pass  # keep whatever was set before


def get_valid_topics() -> frozenset[str]:
    return _valid_topics


def validate_interest_topics(topics: list[str]) -> list[str]:
    """Return normalized, DB-driven interest topics (deduplicated, order preserved)."""
    valid = _valid_topics
    seen: set[str] = set()
    validated: list[str] = []
    for topic in topics[:MAX_INTERESTS]:
        normalized = topic.strip().upper()
        if not normalized or normalized not in valid:
            continue
        if normalized not in seen:
            seen.add(normalized)
            validated.append(normalized)
    return validated


def validate_single_interest(topic: str) -> str:
    normalized = topic.strip().upper()
    if normalized not in _valid_topics:
        raise ValueError(f"Invalid topic. Valid topics: {sorted(_valid_topics)}")
    return normalized
