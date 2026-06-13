"""BM25 in-memory index, rebuilt on startup from DB articles."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


@dataclass
class BM25Index:
    article_ids: list[str] = field(default_factory=list)
    _index: BM25Okapi | None = None

    def build(self, articles: list[tuple[str, str]]) -> None:
        """articles: list of (id, text) tuples."""
        self.article_ids = [a[0] for a in articles]
        corpus = [_tokenize(a[1]) for a in articles]
        self._index = BM25Okapi(corpus)

    def search(self, query: str, top_k: int = 50) -> list[tuple[str, float]]:
        if self._index is None or not self.article_ids:
            return []
        tokens = _tokenize(query)
        scores = self._index.get_scores(tokens)
        ranked = sorted(
            zip(self.article_ids, scores.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )
        return [(aid, score) for aid, score in ranked[:top_k] if score > 0]


# Singleton — populated at app startup
bm25_index = BM25Index()
