"""Interest tracking: cookie for guests, DB for authenticated users."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.models import User, UserInterest


async def get_user_interests(user: User, db: AsyncSession) -> list[str]:
    result = await db.execute(
        select(UserInterest.topic).where(UserInterest.user_id == user.id)
    )
    return [row[0] for row in result.all()]


async def set_user_interests(user: User, topics: list[str], db: AsyncSession) -> list[str]:
    await db.execute(delete(UserInterest).where(UserInterest.user_id == user.id))
    for topic in topics:
        db.add(UserInterest(user_id=user.id, topic=topic.upper()))
    await db.commit()
    return topics


async def toggle_user_interest(user: User, topic: str, db: AsyncSession) -> list[str]:
    topic = topic.upper()
    result = await db.execute(
        select(UserInterest).where(UserInterest.user_id == user.id, UserInterest.topic == topic)
    )
    existing = result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
    else:
        db.add(UserInterest(user_id=user.id, topic=topic))
    await db.commit()
    return await get_user_interests(user, db)


def parse_cookie_interests(cookie_val: str | None) -> list[str]:
    if not cookie_val:
        return []
    try:
        return json.loads(cookie_val)
    except Exception:
        return []
