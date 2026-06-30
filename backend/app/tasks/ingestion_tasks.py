import asyncio
import logging

from app.core.celery_app import celery_app
from app.db.database import AsyncSessionLocal
from app.services.ingestion_service import ingest_all_categories, build_bm25_index

logger = logging.getLogger("veritas")


async def _run_ingestion() -> list[dict]:
    async with AsyncSessionLocal() as db:
        results = await ingest_all_categories(db)
        total_inserted = sum(r["inserted"] for r in results)
        logger.info(f"Ingestion complete — total inserted: {total_inserted}")

        if total_inserted > 0:
            logger.info("Rebuilding BM25 index with newly ingested articles...")
            await build_bm25_index(db)
            logger.info("BM25 index rebuilt.")

    return results


@celery_app.task(name="app.tasks.ingestion_tasks.run_ingestion_task", bind=True)
def run_ingestion_task(self) -> list[dict]:
    """Celery task that runs the full async ingestion pipeline."""
    try:
        return asyncio.run(_run_ingestion())
    except Exception as exc:
        logger.error(f"Ingestion task failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60, max_retries=3)
