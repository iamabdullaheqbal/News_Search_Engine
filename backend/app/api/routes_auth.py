import secrets
import urllib.parse

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.rate_limit import limiter
from app.core.settings import get_settings
from app.core.validators import validate_interest_topics, validate_single_interest
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import (
    AuthResponse,
    InterestToggleRequest,
    LoginRequest,
    RegisterRequest,
    SetInterestsRequest,
    UserOut,
)
from app.services.auth import (
    create_refresh_token,
    decode_token,
    get_access_jti,
    get_current_user,
    hash_password,
    verify_password,
)
from app.services.interest import get_user_interests
from app.services.token_store import (
    blacklist_access_token,
    consume_refresh_token,
    revoke_refresh_token,
    store_refresh_token,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
OAUTH_STATE_COOKIE = "veritas_oauth_state"

# Fixed error codes — never reflect raw provider errors in URLs
_OAUTH_ERROR_CODES = frozenset({
    "missing_code",
    "token_exchange_failed",
    "userinfo_failed",
    "missing_profile",
    "invalid_state",
    "account_exists",
    "oauth_failed",
})


def _oauth_error_redirect(code: str) -> RedirectResponse:
    safe_code = code if code in _OAUTH_ERROR_CODES else "oauth_failed"
    return RedirectResponse(f"{settings.frontend_url}/?auth_error={safe_code}")


def _set_auth_cookies(response: Response, user_id: int) -> None:
    from app.services.auth import create_access_token

    access_token = create_access_token(user_id)
    refresh_token, refresh_jti = create_refresh_token(user_id)
    store_refresh_token(refresh_jti, user_id)

    response.set_cookie(
        key=settings.cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/auth/refresh",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key=settings.cookie_name, path="/")
    response.delete_cookie(key=settings.refresh_cookie_name, path="/api/auth/refresh")


def _build_user_out(user: User, interests: list[str]) -> UserOut:
    return UserOut(id=user.id, email=user.email, name=user.name, interests=interests)


@router.post("/register", response_model=AuthResponse)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Unable to create account with these credentials",
        )
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        name=body.name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    _set_auth_cookies(response, user.id)
    return AuthResponse(user=_build_user_out(user, []))


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    _set_auth_cookies(response, user.id)
    interests = await get_user_interests(user, db)
    return AuthResponse(user=_build_user_out(user, interests))


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None, alias="veritas_refresh"),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    decoded = decode_token(refresh_token, expected_type="refresh")
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user_id, jti = decoded
    validated_user_id = consume_refresh_token(jti)
    if validated_user_id is None or validated_user_id != user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    _set_auth_cookies(response, user.id)
    interests = await get_user_interests(user, db)
    return AuthResponse(user=_build_user_out(user, interests))


@router.post("/logout")
async def logout(
    response: Response,
    token: Optional[str] = Cookie(default=None, alias="veritas_session"),
    refresh_token: Optional[str] = Cookie(default=None, alias="veritas_refresh"),
):
    if refresh_token:
        decoded = decode_token(refresh_token, expected_type="refresh")
        if decoded:
            _, jti = decoded
            revoke_refresh_token(jti)
    if token:
        jti = get_access_jti(token)
        if jti:
            blacklist_access_token(jti)
    _clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    interests = await get_user_interests(user, db)
    return _build_user_out(user, interests)


@router.post("/interests/toggle")
async def toggle_interest(
    body: InterestToggleRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        topic = validate_single_interest(body.topic)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    from app.services.interest import toggle_user_interest
    updated = await toggle_user_interest(user, topic, db)
    return {"interests": updated}


@router.put("/interests")
async def set_interests(
    body: SetInterestsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    topics = validate_interest_topics(body.topics)
    from app.services.interest import set_user_interests
    updated = await set_user_interests(user, topics, db)
    return {"interests": updated}


# ---------------------------------------------------------------------------
# Google OAuth
# ---------------------------------------------------------------------------

@router.get("/google")
async def google_login():
    """Redirect the browser to Google's OAuth consent screen."""
    if not settings.google_client_id:
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    state = secrets.token_urlsafe(32)
    params = urllib.parse.urlencode({
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "state": state,
    })
    redirect = RedirectResponse(f"{GOOGLE_AUTH_URL}?{params}")
    redirect.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=state,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=600,
        path="/api/auth",
    )
    return redirect


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle the redirect from Google, exchange code for user info, upsert user."""
    if error or not code:
        resp = _oauth_error_redirect("oauth_failed" if error else "missing_code")
        resp.delete_cookie(key=OAUTH_STATE_COOKIE, path="/api/auth")
        return resp

    stored_state = request.cookies.get(OAUTH_STATE_COOKIE)
    if not state or not stored_state or state != stored_state:
        resp = _oauth_error_redirect("invalid_state")
        resp.delete_cookie(key=OAUTH_STATE_COOKIE, path="/api/auth")
        return resp

    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        })
        if not token_resp.is_success:
            resp = _oauth_error_redirect("token_exchange_failed")
            resp.delete_cookie(key=OAUTH_STATE_COOKIE, path="/api/auth")
            return resp
        token_data = token_resp.json()

        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        if not userinfo_resp.is_success:
            resp = _oauth_error_redirect("userinfo_failed")
            resp.delete_cookie(key=OAUTH_STATE_COOKIE, path="/api/auth")
            return resp
        info = userinfo_resp.json()

    google_id = info.get("sub")
    email = info.get("email")
    name = info.get("name") or info.get("given_name") or email

    if not google_id or not email:
        resp = _oauth_error_redirect("missing_profile")
        resp.delete_cookie(key=OAUTH_STATE_COOKIE, path="/api/auth")
        return resp

    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if not user:
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            # Do not auto-link — require password login for existing accounts
            resp = _oauth_error_redirect("account_exists")
            resp.delete_cookie(key=OAUTH_STATE_COOKIE, path="/api/auth")
            return resp
        user = User(email=email, google_id=google_id, name=name)
        db.add(user)

    await db.commit()
    await db.refresh(user)

    success = RedirectResponse(f"{settings.frontend_url}/?auth_success=1", status_code=302)
    success.delete_cookie(key=OAUTH_STATE_COOKIE, path="/api/auth")
    _set_auth_cookies(success, user.id)
    return success
