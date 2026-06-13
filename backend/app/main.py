import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.settings import get_settings
from app.db.database import engine, AsyncSessionLocal
from app.db.models import Base
from app.services.ingestion import seed_and_index
from app.api import routes_auth, routes_search, routes_articles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("veritas")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create any missing tables (safe no-op if they already exist)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.warning(f"create_all skipped or partial: {e}")

    # Seed articles and build BM25 index
    try:
        async with AsyncSessionLocal() as db:
            await seed_and_index(db)
    except Exception as e:
        logger.error(f"Startup seed/index failed: {e}", exc_info=True)

    yield


app = FastAPI(title="Veritas API", lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": str(exc) or "Internal server error"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router)
app.include_router(routes_search.router)
app.include_router(routes_articles.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
