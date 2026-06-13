from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str

    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    # Frontend
    frontend_url: str

    # Cookie
    cookie_name: str
    refresh_cookie_name: str
    cookie_secure: bool
    cookie_samesite: str

    # News APIs
    gnews_api_key: str = ""
    gnews_api_url: str = "https://gnews.io/api/v4"
    newsapi_key: str = ""
    newsapi_url: str = "https://newsapi.org/v2"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
