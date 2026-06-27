import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import routes_articles, routes_auth, routes_search
from app.core.settings import get_settings
from app.db.database import AsyncSessionLocal, engine
from app.db.models import Base
from app.services.ingestion_service import build_bm25_index
from app.core.validators import refresh_valid_topics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("veritas")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.warning(f"create_all skipped or partial: {e}")

    try:
        async with AsyncSessionLocal() as db:
            await build_bm25_index(db)
            await refresh_valid_topics(db)
    except Exception as e:
        logger.error(f"Startup BM25 index build failed: {e}", exc_info=True)

    yield


_docs_url = None if settings.is_production else "/docs"
_redoc_url = None if settings.is_production else "/redoc"

app = FastAPI(title="Veritas API", lifespan=lifespan, docs_url=_docs_url, redoc_url=_redoc_url)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Ingest-Key"],
)

app.include_router(routes_auth.router)
app.include_router(routes_search.router)
app.include_router(routes_articles.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
