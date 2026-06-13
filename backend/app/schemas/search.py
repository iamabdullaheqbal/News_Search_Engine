from pydantic import BaseModel
from app.schemas.article import ArticleOut


class SearchRequest(BaseModel):
    q: str
    category: str | None = None
    limit: int = 20
    offset: int = 0


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[ArticleOut]
