"""Cross-encoder reranker (ms-marco-MiniLM-L-6-v2), lazy-loaded."""
from __future__ import annotations
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentence_transformers import CrossEncoder


@lru_cache(maxsize=1)
def get_reranker() -> "CrossEncoder":
    from sentence_transformers import CrossEncoder
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(query: str, candidates: list[tuple[str, str]], top_k: int = 10) -> list[tuple[str, float]]:
    """
    candidates: list of (article_id, text)
    Returns sorted list of (article_id, score).
    """
    if not candidates:
        return []
    model = get_reranker()
    pairs = [(query, text) for _, text in candidates]
    scores = model.predict(pairs).tolist()
    ranked = sorted(zip([c[0] for c in candidates], scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
