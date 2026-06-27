"""Maps ingestion source categories → frontend display categories,
with keyword-based override for CLIMATE and MARKETS."""
from __future__ import annotations

FRONTEND_CATEGORIES = [
    "for-you", "politics", "economy", "tech",
    "climate", "culture", "science", "markets", "health", "sports",
]

# Ingestion category → frontend category (uppercase, stored in DB)
CATEGORY_MAPPING: dict[str, str] = {
    "general":       "POLITICS",
    "world":         "POLITICS",
    "nation":        "POLITICS",
    "business":      "ECONOMY",
    "technology":    "TECH",
    "entertainment": "CULTURE",
    "sports":        "SPORTS",
    "science":       "SCIENCE",
    "health":        "HEALTH",
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
    """Determine the stored (uppercase) frontend category for an article dict.
    Checks title+dek+body against climate/markets keyword lists first,
    then falls back to the CATEGORY_MAPPING lookup.
    """
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

    raw_cat = article_dict.get("category", "").lower()
    return CATEGORY_MAPPING.get(raw_cat, "POLITICS")
