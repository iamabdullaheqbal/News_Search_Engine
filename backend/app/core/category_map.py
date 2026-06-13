"""Maps ingestion source categories → frontend display categories,
with keyword-based override for CLIMATE and MARKETS."""
from __future__ import annotations

FRONTEND_CATEGORIES = [
    "for-you", "politics", "economy", "tech",
    "climate", "culture", "science", "markets",
]

# Ingestion category → frontend category
CATEGORY_MAPPING: dict[str, str] = {
    "general":       "politics",
    "world":         "politics",
    "nation":        "politics",
    "business":      "economy",
    "technology":    "tech",
    "entertainment": "culture",
    "sports":        "culture",
    "science":       "science",
    "health":        "science",
}

CLIMATE_KEYWORDS = [
    "climate change", "global warming", "emissions", "carbon", "greenhouse",
    "fossil fuel", "renewable energy", "solar", "wind energy", "net zero",
    "ipcc", "paris agreement", "deforestation", "sea level", "arctic",
    "wildfire", "drought", "flood", "extreme weather", "biodiversity",
]

MARKETS_KEYWORDS = [
    "stock market", "nasdaq", "dow jones", "s&p 500", "wall street",
    "interest rates", "federal reserve", "fed rate", "inflation rate",
    "bond market", "treasury", "hedge fund", "private equity", "ipo",
    "earnings", "gdp", "recession", "bull market", "bear market",
    "cryptocurrency", "bitcoin", "forex", "commodity prices",
]


def assign_frontend_category(article_dict: dict) -> str:
    """Determine the frontend category for an article dict.
    Checks title+dek+body against climate/markets keyword lists first,
    then falls back to the CATEGORY_MAPPING lookup.
    """
    # Build a single searchable text blob
    text = " ".join(filter(None, [
        article_dict.get("title", ""),
        article_dict.get("dek", ""),
        article_dict.get("body", ""),
    ])).lower()

    for kw in CLIMATE_KEYWORDS:
        if kw in text:
            return "CLIMATE"

    for kw in MARKETS_KEYWORDS:
        if kw in text:
            return "MARKETS"

    # Fall back to structural mapping
    raw_cat = article_dict.get("category", "").lower()
    mapped = CATEGORY_MAPPING.get(raw_cat, "politics")
    return mapped.upper()
