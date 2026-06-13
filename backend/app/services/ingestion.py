"""Seed the DB with mock articles and build the BM25 index on startup."""
from __future__ import annotations
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Article
from app.services.bm25 import bm25_index
from app.services.embedding import embed_texts

_SAMPLE_BODY = json.dumps([
    "The shift has been quiet, methodical, and largely invisible to consumers — but its consequences are already reshaping global supply chains in ways that economists are only beginning to fully model.",
    "Over the past eighteen months, a coalition of governments and private enterprises has committed unprecedented capital to onshoring critical manufacturing capacity.",
    '"What we are witnessing is not deglobalization," said Marta Reinhardt, senior fellow at the Peterson Institute. "It is the construction of a parallel logistics architecture — one designed for resilience rather than efficiency."',
    "The numbers tell their own story. Permitting activity for advanced manufacturing facilities is up 340 percent year-over-year.",
    "Skeptics caution that the transition is far from complete. Specialized labor remains scarce, and the regulatory frameworks meant to accelerate construction have themselves become bottlenecks.",
    "Still, the direction of travel is unmistakable. For the first time since the late 1990s, capital expenditure on domestic industrial capacity has outpaced expenditure on overseas expansion.",
])

_now = datetime.now(timezone.utc)


def _dt(hours_ago: int) -> datetime:
    return _now - timedelta(hours=hours_ago)


SEED_ARTICLES = [
    {
        "id": "hero-1", "title": "The Silent Re-Shoring of Global Silicon Production",
        "dek": "Inside the $200 billion race to build the next generation of chip fabrication plants on North American soil.",
        "category": "TECH", "source": "The Wall Street Journal", "author": "Eleanor Hayes",
        "read_time": "14 min read",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=2000",
        "published_at": _dt(2),
    },
    {
        "id": "art-1", "title": "European Markets Rally on Unexpected Inflation Drop",
        "dek": "A surprise reading from Eurostat sent equities to a six-month high.",
        "category": "MARKETS", "source": "Financial Times", "author": "David Mercer",
        "read_time": "5 min read",
        "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(4),
    },
    {
        "id": "art-2", "title": "New Climate Accord Reached in Geneva",
        "dek": "Negotiators agree to binding emissions caps for heavy industry after a tense final round of talks.",
        "category": "CLIMATE", "source": "Reuters", "author": "Priya Anand",
        "read_time": "8 min read",
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(5),
    },
    {
        "id": "art-3", "title": "The Renaissance of Analog Photography",
        "dek": "Film stocks are flying off shelves and darkrooms are reopening.",
        "category": "CULTURE", "source": "The Atlantic", "author": "Sofia Kowalski",
        "read_time": "12 min read",
        "image_url": "https://images.unsplash.com/photo-1495106245177-55f53ab2e4dc?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(6),
    },
    {
        "id": "art-4", "title": "Breakthrough in Solid-State Battery Tech",
        "dek": "A Boston lab reports a cell density that could finally make long-range electric aviation commercially viable.",
        "category": "SCIENCE", "source": "MIT Technology Review", "author": "Dr. Henry Chen",
        "read_time": "9 min read",
        "image_url": "https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(8),
    },
    {
        "id": "art-5", "title": "Senate Passes Sweeping Infrastructure Bill",
        "dek": "The bipartisan package allocates $1.2 trillion across transit, broadband, and grid modernization.",
        "category": "POLITICS", "source": "Washington Post", "author": "James O'Neill",
        "read_time": "6 min read",
        "image_url": "https://images.unsplash.com/photo-1523292562811-8fa7962a78c8?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(10),
    },
    {
        "id": "art-6", "title": "Tech Giants Face New Antitrust Scrutiny",
        "dek": "Regulators on both sides of the Atlantic are coordinating their probes into platform dominance.",
        "category": "TECH", "source": "Bloomberg", "author": "Rachel Tan",
        "read_time": "7 min read",
        "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(12),
    },
    {
        "id": "art-7", "title": "The Quiet Return of Industrial Policy",
        "dek": "Governments are picking winners again — and economists are split on whether it will work this time.",
        "category": "ECONOMY", "source": "The Economist", "author": "Marcus Webb",
        "read_time": "11 min read",
        "image_url": "https://images.unsplash.com/photo-1473445730015-841f29a9490b?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(14),
    },
    {
        "id": "art-8", "title": "Coral Reefs Show Unexpected Recovery in Pacific",
        "dek": "A previously bleached reef system has rebounded, prompting scientists to revisit assumptions about resilience.",
        "category": "CLIMATE", "source": "Nature", "author": "Dr. Aisha Brennan",
        "read_time": "10 min read",
        "image_url": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(16),
    },
    {
        "id": "art-9", "title": "Wall Street Pivots to Private Credit",
        "dek": "As public debt markets cool, the largest asset managers are quietly building parallel lending businesses.",
        "category": "MARKETS", "source": "Bloomberg", "author": "David Mercer",
        "read_time": "8 min read",
        "image_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(18),
    },
    {
        "id": "art-10", "title": "Mars Sample Return Mission Sets New Date",
        "dek": "A joint NASA-ESA mission to retrieve geological samples has been rescheduled for early 2031.",
        "category": "SCIENCE", "source": "Scientific American", "author": "Dr. Henry Chen",
        "read_time": "7 min read",
        "image_url": "https://images.unsplash.com/photo-1614728263952-84ea256f9679?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(20),
    },
    {
        "id": "art-11", "title": "A New Generation of Opera Houses Opens",
        "dek": "From Shanghai to Reykjavik, civic ambition is being expressed once again through architecture.",
        "category": "CULTURE", "source": "The New Yorker", "author": "Sofia Kowalski",
        "read_time": "13 min read",
        "image_url": "https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(24),
    },
    {
        "id": "art-12", "title": "Coalition Talks Stall in The Hague",
        "dek": "The third round of negotiations has produced no agreement, raising the prospect of a snap election.",
        "category": "POLITICS", "source": "Reuters", "author": "Priya Anand",
        "read_time": "5 min read",
        "image_url": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(28),
    },
    {
        "id": "art-13", "title": "Open-Source AI Models Surpass Closed Rivals",
        "dek": "A new benchmark shows community-built systems leading on reasoning tasks for the first time.",
        "category": "TECH", "source": "The Information", "author": "Rachel Tan",
        "read_time": "9 min read",
        "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(32),
    },
    {
        "id": "art-14", "title": "Emerging Markets Quietly Outperform",
        "dek": "Capital is flowing back into Jakarta, Lagos, and São Paulo as developed-market yields compress.",
        "category": "ECONOMY", "source": "Financial Times", "author": "Marcus Webb",
        "read_time": "7 min read",
        "image_url": "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&q=80&w=1200",
        "published_at": _dt(36),
    },
]


async def seed_and_index(db: AsyncSession) -> None:
    """Insert seed articles if DB is empty, then build BM25 index."""
    result = await db.execute(select(Article).limit(1))
    if result.scalar_one_or_none() is None:
        # Compute embeddings in batch
        texts = [f"{a['title']} {a.get('dek', '')}" for a in SEED_ARTICLES]
        embeddings = embed_texts(texts)
        for data, emb in zip(SEED_ARTICLES, embeddings):
            article = Article(**{k: v for k, v in data.items()}, body=_SAMPLE_BODY, embedding=emb)
            db.add(article)
        await db.commit()

    # Build BM25 from all articles in DB
    all_result = await db.execute(select(Article.id, Article.title, Article.dek, Article.category))
    rows = all_result.all()
    bm25_index.build([(r[0], f"{r[1]} {r[2] or ''} {r[3]}") for r in rows])
