"""One-time migration: remap raw ingestion categories → frontend categories in the DB."""
import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(__file__))
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("veritas")


async def main():
    from sqlalchemy import update, select, func
    from app.db.database import AsyncSessionLocal, engine
    from app.db.models import Article, Base
    from app.core.category_map import CATEGORY_MAPPING, CLIMATE_KEYWORDS, MARKETS_KEYWORDS

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Raw ingestion category → frontend category (uppercase)
    # Also handle already-uppercase variants from the previous run
    REMAP = {
        # lowercase (GNews/NewsAPI source categories)
        "general":       "POLITICS",
        "world":         "POLITICS",
        "nation":        "POLITICS",
        "business":      "ECONOMY",
        "technology":    "TECH",
        "entertainment": "CULTURE",
        "sports":        "SPORTS",
        "science":       "SCIENCE",
        "health":        "HEALTH",
        # uppercase (already stored from previous ingestion run)
        "GENERAL":       "POLITICS",
        "WORLD":         "POLITICS",
        "NATION":        "POLITICS",
        "BUSINESS":      "ECONOMY",
        "TECHNOLOGY":    "TECH",
        "ENTERTAINMENT": "CULTURE",
        "SPORTS":        "SPORTS",
        "SCIENCE":       "SCIENCE",
        "HEALTH":        "HEALTH",
    }

    async with AsyncSessionLocal() as db:
        # Count before
        total = (await db.execute(select(func.count()).select_from(Article))).scalar()
        logger.info(f"Total articles: {total}")

        updated = 0
        for old_cat, new_cat in REMAP.items():
            result = await db.execute(
                update(Article)
                .where(Article.category == old_cat)
                .values(category=new_cat)
            )
            if result.rowcount:
                logger.info(f"  {old_cat!r:20} → {new_cat!r:12}  ({result.rowcount} rows)")
                updated += result.rowcount

        await db.commit()
        logger.info(f"Done. Updated {updated} articles.")

        # Show resulting distribution
        rows = (await db.execute(
            select(Article.category, func.count()).group_by(Article.category).order_by(func.count().desc())
        )).all()
        logger.info("Category distribution after migration:")
        for cat, count in rows:
            logger.info(f"  {cat:15} {count}")


if __name__ == "__main__":
    asyncio.run(main())
