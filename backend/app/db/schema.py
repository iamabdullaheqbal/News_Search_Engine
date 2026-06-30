"""Database schema bootstrap: pgvector extension, tables, and ANN index."""
from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.database import Base
from app.db.models import Article, ReadHistory, User, UserInterest  # noqa: F401

logger = logging.getLogger("veritas")


async def ensure_schema(conn: AsyncConnection) -> None:
    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    await conn.run_sync(Base.metadata.create_all)
    await conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_articles_embedding_hnsw
            ON articles USING hnsw (embedding vector_cosine_ops)
            WHERE embedding IS NOT NULL
            """
        )
    )
    logger.info("Database schema ready (tables + pgvector HNSW index).")
