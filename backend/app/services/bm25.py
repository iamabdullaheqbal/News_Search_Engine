"""BM25 in-memory index, rebuilt on startup from DB articles."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from rank_bm25 import BM25Okapi

from app.services.text_processing import tokenize_for_bm25


def _index_tokens(text: str) -> list[str]:
    """Tokenize pre-lemmatized index text without re-lemmatizing."""
    return re.findall(r"\w+", text.lower())


@dataclass
class BM25Index:
    article_ids: list[str] = field(default_factory=list)
    _index: BM25Okapi | None = None

    def build(self, articles: list[tuple[str, str]]) -> None:
        """articles: list of (id, text) tuples."""
        self.article_ids = [article_id for article_id, _ in articles]
        corpus = [_index_tokens(text) for _, text in articles]
        self._index = BM25Okapi(corpus)

    def search(self, query: str, top_k: int = 50) -> list[tuple[str, float]]:
        if self._index is None or not self.article_ids:
            return []
        tokens = tokenize_for_bm25(query)
        if not tokens:
            return []
        scores = self._index.get_scores(tokens)
        ranked = sorted(
            zip(self.article_ids, scores.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )
        return [(aid, score) for aid, score in ranked[:top_k] if score > 0]


# Singleton — populated at app startup
bm25_index = BM25Index()
