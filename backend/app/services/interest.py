"""Interest tracking: cookie for guests, DB for authenticated users."""
import json

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import validate_interest_topics, validate_single_interest
from app.db.models import User, UserInterest


async def get_user_interests(user: User, db: AsyncSession) -> list[str]:
    result = await db.execute(
        select(UserInterest.topic).where(UserInterest.user_id == user.id)
    )
    return [row[0] for row in result.all()]


async def set_user_interests(user: User, topics: list[str], db: AsyncSession) -> list[str]:
    validated = validate_interest_topics(topics)
    await db.execute(delete(UserInterest).where(UserInterest.user_id == user.id))
    for topic in validated:
        db.add(UserInterest(user_id=user.id, topic=topic))
    await db.commit()
    return validated


async def toggle_user_interest(user: User, topic: str, db: AsyncSession) -> list[str]:
    topic = validate_single_interest(topic)
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
        parsed = json.loads(cookie_val)
        if not isinstance(parsed, list):
            return []
        return [str(t) for t in parsed]
    except Exception:
        return []
