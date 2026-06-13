from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, UserOut, TokenResponse
from app.services.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user,
)
from app.services.interest import get_user_interests
from app.core.settings import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


def _set_auth_cookies(response: Response, user_id: int) -> str:
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    # Access token cookie — short-lived
    response.set_cookie(
        key=settings.cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    # Refresh token cookie — long-lived, only sent to /api/auth/refresh
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/auth/refresh",
    )
    return access_token


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key=settings.cookie_name, path="/")
    response.delete_cookie(key=settings.refresh_cookie_name, path="/api/auth/refresh")


def _build_user_out(user: User, interests: list[str]) -> UserOut:
    return UserOut(id=user.id, email=user.email, name=user.name, interests=interests)


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        name=body.name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    access_token = _set_auth_cookies(response, user.id)
    return TokenResponse(access_token=access_token, user=_build_user_out(user, []))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = _set_auth_cookies(response, user.id)
    interests = await get_user_interests(user, db)
    return TokenResponse(access_token=access_token, user=_build_user_out(user, interests))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None, alias="veritas_refresh"),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    user_id = decode_token(refresh_token, expected_type="refresh")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    # Rotate both tokens
    access_token = _set_auth_cookies(response, user.id)
    interests = await get_user_interests(user, db)
    return TokenResponse(access_token=access_token, user=_build_user_out(user, interests))


@router.post("/logout")
async def logout(response: Response):
    _clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    interests = await get_user_interests(user, db)
    return _build_user_out(user, interests)


@router.post("/interests/toggle")
async def toggle_interest(
    body: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    topic = body.get("topic", "")
    if not topic:
        raise HTTPException(status_code=400, detail="topic required")
    from app.services.interest import toggle_user_interest
    updated = await toggle_user_interest(user, topic, db)
    return {"interests": updated}


@router.put("/interests")
async def set_interests(
    body: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    topics = body.get("topics", [])
    from app.services.interest import set_user_interests
    updated = await set_user_interests(user, topics, db)
    return {"interests": updated}
