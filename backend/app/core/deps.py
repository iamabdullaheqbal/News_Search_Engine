"""Shared FastAPI dependencies."""
from __future__ import annotations

from fastapi import Header, HTTPException

from app.core.settings import get_settings

settings = get_settings()


async def verify_ingest_key(x_ingest_key: str = Header(..., alias="X-Ingest-Key")) -> None:
    if not settings.ingest_api_key or x_ingest_key != settings.ingest_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")
