"""Standalone script to fetch articles from GNews + NewsAPI and save to DB."""
import asyncio
import logging
import sys
import os

# Ensure the backend app is importable
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("veritas")


async def main():
    from app.db.database import engine, AsyncSessionLocal
    from app.db.schema import ensure_schema
    from app.services.ingestion_service import ingest_all_categories, build_bm25_index

    async with engine.begin() as conn:
        await ensure_schema(conn)
    logger.info("Schema ready.")

    async with AsyncSessionLocal() as db:
        logger.info("Starting ingestion from GNews + NewsAPI...")
        results = await ingest_all_categories(db)

        total_fetched  = sum(r["fetched"]  for r in results)
        total_inserted = sum(r["inserted"] for r in results)
        total_skipped  = sum(r["skipped"]  for r in results)

        logger.info("=" * 50)
        logger.info(f"DONE — fetched={total_fetched}  inserted={total_inserted}  skipped={total_skipped}")
        for r in results:
            logger.info(f"  [{r['category']:14}] fetched={r['fetched']:4}  inserted={r['inserted']:4}  skipped={r['skipped']:4}")
        logger.info("=" * 50)

        logger.info("Building BM25 index...")
        await build_bm25_index(db)
        logger.info("BM25 index ready.")


if __name__ == "__main__":
    asyncio.run(main())
