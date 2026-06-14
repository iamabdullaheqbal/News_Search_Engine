"""Output sanitization helpers."""
from __future__ import annotations

from urllib.parse import urlparse


def sanitize_image_url(url: str | None) -> str | None:
    """Allow only HTTPS image URLs with a valid host."""
    if not url:
        return None
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return None
    if parsed.scheme != "https" or not parsed.netloc:
        return None
    return url.strip()
