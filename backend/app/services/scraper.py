"""Full article body scraper.

Fetches the original article URL and extracts clean paragraph text using
BeautifulSoup. Used at ingest time to replace the truncated API snippet
with the full article content.

Design decisions:
- Runs with a short timeout (10s) — scraping is best-effort, never blocks ingestion
- Skips paywalled / JS-heavy sites gracefully (returns None → falls back to snippet)
- Filters out boilerplate: nav, headers, footers, ads, short paragraphs < 40 chars
- Returns a list[str] of paragraph strings (matches the Article.body JSON format)
"""
from __future__ import annotations

import logging
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger("veritas")

# Tags whose content is always boilerplate
_SKIP_TAGS = {
    "script", "style", "noscript", "nav", "header", "footer",
    "aside", "figure", "figcaption", "form", "button", "iframe",
    "ad", "advertisement",
}

# CSS class / id substrings that indicate boilerplate containers
_SKIP_PATTERNS = re.compile(
    r"(nav|menu|sidebar|footer|header|cookie|banner|ad[-_]|"
    r"related|recommend|promo|newsletter|subscribe|social|share|"
    r"comment|widget|popup|modal|breadcrumb)",
    re.IGNORECASE,
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _is_boilerplate(tag: Tag) -> bool:
    """Return True if the tag looks like navigation/ads/sidebar content."""
    for attr in ("class", "id", "role", "data-testid"):
        val = tag.get(attr, "")
        text = " ".join(val) if isinstance(val, list) else str(val)
        if _SKIP_PATTERNS.search(text):
            return True
    return False


def _extract_paragraphs(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")

    # Remove known boilerplate tags outright
    for tag in soup.find_all(_SKIP_TAGS):
        tag.decompose()

    # Find the main content container — prefer <article>, then <main>, then <body>
    container = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", attrs={"role": "main"})
        or soup.body
    )
    if container is None:
        return []

    paragraphs: list[str] = []
    for p in container.find_all("p"):
        # Skip paragraphs inside boilerplate containers
        if any(_is_boilerplate(parent) for parent in p.parents if isinstance(parent, Tag)):
            continue
        text = p.get_text(separator=" ", strip=True)
        # Skip very short lines (captions, bylines, metadata snippets)
        if len(text) < 40:
            continue
        # Normalise whitespace
        text = re.sub(r"\s+", " ", text).strip()
        paragraphs.append(text)

    return paragraphs


async def scrape_article_body(url: str) -> list[str] | None:
    """Fetch `url` and return a list of paragraph strings, or None on failure."""
    if not url:
        return None
    try:
        async with httpx.AsyncClient(
            timeout=10,
            follow_redirects=True,
            headers=_HEADERS,
        ) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return None
            content_type = resp.headers.get("content-type", "")
            if "text/html" not in content_type:
                return None
            paragraphs = _extract_paragraphs(resp.text)
            return paragraphs if len(paragraphs) >= 2 else None
    except Exception as e:
        logger.debug(f"Scrape failed for {url}: {e}")
        return None
