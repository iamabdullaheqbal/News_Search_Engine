"""Shared input validation helpers."""
from __future__ import annotations

VALID_INTEREST_TOPICS = frozenset({
    "POLITICS", "ECONOMY", "TECH", "CLIMATE", "CULTURE", "SCIENCE", "MARKETS",
})

MAX_INTERESTS = 20


def validate_interest_topics(topics: list[str]) -> list[str]:
    """Return normalized, allowlisted interest topics (deduplicated, order preserved)."""
    seen: set[str] = set()
    validated: list[str] = []
    for topic in topics[:MAX_INTERESTS]:
        normalized = topic.strip().upper()
        if not normalized or normalized not in VALID_INTEREST_TOPICS:
            continue
        if normalized not in seen:
            seen.add(normalized)
            validated.append(normalized)
    return validated


def validate_single_interest(topic: str) -> str:
    normalized = topic.strip().upper()
    if normalized not in VALID_INTEREST_TOPICS:
        raise ValueError(f"Invalid topic. Valid topics: {sorted(VALID_INTEREST_TOPICS)}")
    return normalized
