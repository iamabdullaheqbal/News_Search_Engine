from datetime import datetime
from pydantic import BaseModel


class ArticleOut(BaseModel):
    id: str
    title: str
    dek: str | None = None
    category: str
    source: str
    author: str | None = None
    read_time: str | None = None
    image_url: str | None = None
    published_at: datetime | None = None
    timestamp: str | None = None  # human-relative, computed in service

    model_config = {"from_attributes": True}


class ArticleDetail(ArticleOut):
    body: list[str] | None = None  # parsed from JSON
