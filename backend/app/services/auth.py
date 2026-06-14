import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import get_settings
from app.db.database import get_db
from app.db.models import User
from app.services.token_store import is_access_token_blacklisted

settings = get_settings()

_MAX_PW_BYTES = 72


def _prepare_password(password: str) -> bytes:
    """Pre-hash with SHA-256 so bcrypt always receives <= 72 bytes."""
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > _MAX_PW_BYTES:
        pw_bytes = hashlib.sha256(pw_bytes).digest()
    return pw_bytes


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prepare_password(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_prepare_password(plain), hashed.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {
            "sub": str(user_id),
            "exp": expire,
            "type": "access",
            "jti": str(uuid.uuid4()),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(user_id: int) -> tuple[str, str]:
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh",
            "jti": jti,
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return token, jti


def decode_token(token: str, expected_type: str = "access") -> tuple[int, str] | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != expected_type:
            return None
        sub = payload.get("sub")
        jti = payload.get("jti", "")
        return (int(sub), jti) if sub else None
    except JWTError:
        return None


def get_access_jti(token: str) -> str | None:
    decoded = decode_token(token, expected_type="access")
    return decoded[1] if decoded else None


async def get_current_user_optional(
    token: Optional[str] = Cookie(default=None, alias="veritas_session"),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    decoded = decode_token(token, expected_type="access")
    if not decoded:
        return None
    user_id, jti = decoded
    if is_access_token_blacklisted(jti):
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
