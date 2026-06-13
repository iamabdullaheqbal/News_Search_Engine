"""Lazy-loaded sentence-transformer embedding service."""
from __future__ import annotations
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_model() -> "SentenceTransformer":
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    return model.encode(texts, normalize_embeddings=True).tolist()


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
