"""Shared text normalization for BM25 indexing and embedding."""
from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger("veritas")

_nltk_ready = False


def ensure_nltk_data() -> None:
    """Download NLTK corpora once at startup (not during ingestion)."""
    global _nltk_ready
    if _nltk_ready:
        return
    try:
        import nltk

        nltk.download("wordnet", quiet=True)
        nltk.download("omw-1.4", quiet=True)
        nltk.download("punkt", quiet=True)
        nltk.download("punkt_tab", quiet=True)
        _nltk_ready = True
    except Exception as e:
        logger.warning("Failed to download NLTK data: %s", e)


def lemmatize_text(text: str) -> str:
    if not text:
        return ""
    ensure_nltk_data()
    try:
        import nltk
        from nltk.stem import WordNetLemmatizer
        from nltk.tokenize import word_tokenize

        lemmatizer = WordNetLemmatizer()
        tokens = word_tokenize(text.lower())
        lemmatized = [lemmatizer.lemmatize(token) for token in tokens if token.isalnum()]
        return " ".join(lemmatized)
    except Exception as e:
        logger.warning("Error lemmatizing text: %s", e)
        return " ".join(re.findall(r"\w+", text.lower()))


def tokenize_for_bm25(text: str) -> list[str]:
    """Tokenize query/index text consistently for BM25."""
    return re.findall(r"\w+", lemmatize_text(text))


def build_retrieval_text(
    title: str,
    dek: str | None = None,
    body: str | list[str] | None = None,
    scraped_body: list[str] | None = None,
    max_chars: int = 8000,
) -> str:
    """Plain text used for embeddings and lemmatized BM25 indexing."""
    body_text = ""
    if scraped_body:
        body_text = " ".join(scraped_body)
    elif body:
        if isinstance(body, list):
            body_text = " ".join(body)
        else:
            try:
                parsed = json.loads(body)
                body_text = " ".join(parsed) if isinstance(parsed, list) else str(body)
            except (json.JSONDecodeError, TypeError):
                body_text = body

    parts = [title, dek or "", body_text]
    text = " ".join(part for part in parts if part).strip()
    if len(text) > max_chars:
        return text[:max_chars]
    return text
