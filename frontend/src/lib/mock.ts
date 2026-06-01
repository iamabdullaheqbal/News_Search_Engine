export const CATEGORIES = [
  'POLITICS',
  'ECONOMY',
  'TECH',
  'CLIMATE',
  'CULTURE',
  'SCIENCE',
  'MARKETS',
];

export interface Article {
  id: string;
  title: string;
  dek?: string;
  category: string;
  source: string;
  author?: string;
  readTime: string;
  imageUrl: string;
  timestamp: string;
  publishedAt?: string;
  body?: string[];
}

const sampleBody = [
  'The shift has been quiet, methodical, and largely invisible to consumers — but its consequences are already reshaping global supply chains in ways that economists are only beginning to fully model.',
  'Over the past eighteen months, a coalition of governments and private enterprises has committed unprecedented capital to onshoring critical manufacturing capacity. The decisions, made in boardrooms and cabinet meetings on three continents, mark a deliberate reversal of three decades of globalization orthodoxy.',
  '"What we are witnessing is not deglobalization," said Marta Reinhardt, senior fellow at the Peterson Institute. "It is the construction of a parallel logistics architecture — one designed for resilience rather than efficiency."',
  'The numbers tell their own story. Permitting activity for advanced manufacturing facilities in the United States is up 340 percent year-over-year. Federal subsidies, when combined with state-level incentives, now cover an average of 38 percent of capital costs for qualifying projects.',
  'Skeptics caution that the transition is far from complete. Specialized labor remains scarce, and the regulatory frameworks meant to accelerate construction have themselves become bottlenecks. Several flagship projects have already slipped their original timelines by twelve months or more.',
  'Still, the direction of travel is unmistakable. For the first time since the late 1990s, capital expenditure on domestic industrial capacity has outpaced expenditure on overseas expansion. The implications, both economic and geopolitical, will take years to fully resolve.',
];

export const HERO_ARTICLE: Article = {
  id: 'hero-1',
  title: 'The Silent Re-Shoring of Global Silicon Production',
  dek: 'Inside the $200 billion race to build the next generation of chip fabrication plants on North American soil.',
  category: 'TECH',
  source: 'The Wall Street Journal',
  author: 'Eleanor Hayes',
  readTime: '14 min read',
  imageUrl: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=2000',
  timestamp: '2 hours ago',
  publishedAt: 'June 1, 2026',
  body: sampleBody,
};

export const ARTICLES: Article[] = [
  {
    id: 'art-1',
    title: 'European Markets Rally on Unexpected Inflation Drop',
    dek: 'A surprise reading from Eurostat sent equities to a six-month high, but analysts caution the picture is more fragile than it appears.',
    category: 'MARKETS',
    source: 'Financial Times',
    author: 'David Mercer',
    readTime: '5 min read',
    imageUrl: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&q=80&w=1200',
    timestamp: '4 hours ago',
    publishedAt: 'June 1, 2026',
    body: sampleBody,
  },
  {
    id: 'art-2',
    title: 'New Climate Accord Reached in Geneva',
    dek: 'Negotiators agree to binding emissions caps for heavy industry after a tense final round of talks.',
    category: 'CLIMATE',
    source: 'Reuters',
    author: 'Priya Anand',
    readTime: '8 min read',
    imageUrl: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1200',
    timestamp: '5 hours ago',
    publishedAt: 'June 1, 2026',
    body: sampleBody,
  },
  {
    id: 'art-3',
    title: 'The Renaissance of Analog Photography',
    dek: 'Film stocks are flying off shelves and darkrooms are reopening. A generation raised on pixels is rediscovering grain.',
    category: 'CULTURE',
    source: 'The Atlantic',
    author: 'Sofia Kowalski',
    readTime: '12 min read',
    imageUrl: 'https://images.unsplash.com/photo-1495106245177-55f53ab2e4dc?auto=format&fit=crop&q=80&w=1200',
    timestamp: '6 hours ago',
    publishedAt: 'May 31, 2026',
    body: sampleBody,
  },
  {
    id: 'art-4',
    title: 'Breakthrough in Solid-State Battery Tech',
    dek: 'A Boston lab reports a cell density that could finally make long-range electric aviation commercially viable.',
    category: 'SCIENCE',
    source: 'MIT Technology Review',
    author: 'Dr. Henry Chen',
    readTime: '9 min read',
    imageUrl: 'https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&q=80&w=1200',
    timestamp: '8 hours ago',
    publishedAt: 'May 31, 2026',
    body: sampleBody,
  },
  {
    id: 'art-5',
    title: 'Senate Passes Sweeping Infrastructure Bill',
    dek: 'The bipartisan package allocates $1.2 trillion across transit, broadband, and grid modernization over the next decade.',
    category: 'POLITICS',
    source: 'Washington Post',
    author: "James O'Neill",
    readTime: '6 min read',
    imageUrl: 'https://images.unsplash.com/photo-1523292562811-8fa7962a78c8?auto=format&fit=crop&q=80&w=1200',
    timestamp: '10 hours ago',
    publishedAt: 'May 31, 2026',
    body: sampleBody,
  },
  {
    id: 'art-6',
    title: 'Tech Giants Face New Antitrust Scrutiny',
    dek: 'Regulators on both sides of the Atlantic are coordinating their probes into platform dominance.',
    category: 'TECH',
    source: 'Bloomberg',
    author: 'Rachel Tan',
    readTime: '7 min read',
    imageUrl: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=1200',
    timestamp: '12 hours ago',
    publishedAt: 'May 31, 2026',
    body: sampleBody,
  },
  {
    id: 'art-7',
    title: 'The Quiet Return of Industrial Policy',
    dek: 'Governments are picking winners again — and economists are split on whether it will work this time.',
    category: 'ECONOMY',
    source: 'The Economist',
    author: 'Marcus Webb',
    readTime: '11 min read',
    imageUrl: 'https://images.unsplash.com/photo-1473445730015-841f29a9490b?auto=format&fit=crop&q=80&w=1200',
    timestamp: '14 hours ago',
    publishedAt: 'May 31, 2026',
    body: sampleBody,
  },
  {
    id: 'art-8',
    title: 'Coral Reefs Show Unexpected Recovery in Pacific',
    dek: 'A previously bleached reef system has rebounded, prompting scientists to revisit assumptions about resilience.',
    category: 'CLIMATE',
    source: 'Nature',
    author: 'Dr. Aisha Brennan',
    readTime: '10 min read',
    imageUrl: 'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&q=80&w=1200',
    timestamp: '16 hours ago',
    publishedAt: 'May 30, 2026',
    body: sampleBody,
  },
  {
    id: 'art-9',
    title: 'Wall Street Pivots to Private Credit',
    dek: 'As public debt markets cool, the largest asset managers are quietly building parallel lending businesses.',
    category: 'MARKETS',
    source: 'Bloomberg',
    author: 'David Mercer',
    readTime: '8 min read',
    imageUrl: 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&q=80&w=1200',
    timestamp: '18 hours ago',
    publishedAt: 'May 30, 2026',
    body: sampleBody,
  },
  {
    id: 'art-10',
    title: 'Mars Sample Return Mission Sets New Date',
    dek: 'A joint NASA-ESA mission to retrieve geological samples has been rescheduled for early 2031.',
    category: 'SCIENCE',
    source: 'Scientific American',
    author: 'Dr. Henry Chen',
    readTime: '7 min read',
    imageUrl: 'https://images.unsplash.com/photo-1614728263952-84ea256f9679?auto=format&fit=crop&q=80&w=1200',
    timestamp: '20 hours ago',
    publishedAt: 'May 30, 2026',
    body: sampleBody,
  },
  {
    id: 'art-11',
    title: 'A New Generation of Opera Houses Opens',
    dek: 'From Shanghai to Reykjavik, civic ambition is being expressed once again through architecture.',
    category: 'CULTURE',
    source: 'The New Yorker',
    author: 'Sofia Kowalski',
    readTime: '13 min read',
    imageUrl: 'https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?auto=format&fit=crop&q=80&w=1200',
    timestamp: '1 day ago',
    publishedAt: 'May 30, 2026',
    body: sampleBody,
  },
  {
    id: 'art-12',
    title: 'Coalition Talks Stall in The Hague',
    dek: 'The third round of negotiations has produced no agreement, raising the prospect of a snap election.',
    category: 'POLITICS',
    source: 'Reuters',
    author: 'Priya Anand',
    readTime: '5 min read',
    imageUrl: 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&q=80&w=1200',
    timestamp: '1 day ago',
    publishedAt: 'May 30, 2026',
    body: sampleBody,
  },
  {
    id: 'art-13',
    title: 'Open-Source AI Models Surpass Closed Rivals',
    dek: 'A new benchmark shows community-built systems leading on reasoning tasks for the first time.',
    category: 'TECH',
    source: 'The Information',
    author: 'Rachel Tan',
    readTime: '9 min read',
    imageUrl: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=1200',
    timestamp: '1 day ago',
    publishedAt: 'May 30, 2026',
    body: sampleBody,
  },
  {
    id: 'art-14',
    title: 'Emerging Markets Quietly Outperform',
    dek: 'Capital is flowing back into Jakarta, Lagos, and São Paulo as developed-market yields compress.',
    category: 'ECONOMY',
    source: 'Financial Times',
    author: 'Marcus Webb',
    readTime: '7 min read',
    imageUrl: 'https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&q=80&w=1200',
    timestamp: '1 day ago',
    publishedAt: 'May 30, 2026',
    body: sampleBody,
  },
];

export const ALL_ARTICLES: Article[] = [HERO_ARTICLE, ...ARTICLES];

export function getArticleById(id: string): Article | undefined {
  return ALL_ARTICLES.find((a) => a.id === id);
}

export function getArticlesByCategory(category: string): Article[] {
  return ALL_ARTICLES.filter((a) => a.category.toLowerCase() === category.toLowerCase());
}

export function getRelatedArticles(article: Article, limit = 3): Article[] {
  return ALL_ARTICLES.filter(
    (a) => a.id !== article.id && a.category === article.category
  ).slice(0, limit);
}

export const TRENDING = [
  'Global central banks announce coordinated rate hold',
  'Luxury automotive giants pivot back to hybrid drivetrains',
  'The underground movement saving lost cinematic history',
  'AI regulation framework proposed by EU commission',
  'Record-breaking heatwave sweeps across Southern Europe',
];

export const LIVE_WIRE = [
  { time: '12:45', text: 'FTSE 100 recovers early morning losses, closes up 0.2%.' },
  { time: '12:12', text: 'Prime Minister arrives in Brussels for emergency trade summit.' },
  { time: '11:58', text: 'SpaceX confirms successful landing of Heavy booster core.' },
  { time: '11:30', text: 'EU council greenlights AI transparency directive in plenary vote.' },
  { time: '10:15', text: 'Oil prices stabilize after brief spike amid supply concerns.' },
];
