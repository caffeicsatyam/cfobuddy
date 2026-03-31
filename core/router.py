from functools import lru_cache
from sentence_transformers import SentenceTransformer
import numpy as np
from core.schemas import RouteTarget

# ══════════════════════════════════════════════════════════════════════════════
# EMBEDDING-BASED ROUTER (Primary)
# ══════════════════════════════════════════════════════════════════════════════

_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

ROUTE_DESCRIPTIONS = {
    RouteTarget.SQL.value: """
        Database queries, SQL, calculations, aggregations, averages, sums, counts,
        correlations, filtering data, grouping, ranking, trends in CSV data,
        mathematical operations on tables, data analysis, statistics
    """,
    RouteTarget.FINANCE.value: """
        Stock prices, market data, ticker symbols, earnings reports, balance sheets,
        cash flow, analyst ratings, PE ratios, market cap, dividends, financial metrics,
        company financials, real-time quotes, stock history
    """,
    RouteTarget.WEB_SEARCH.value: """
        Current news, latest information, recent events, web search, general knowledge,
        what is happening, today's news, external information, internet search
    """,
    RouteTarget.MODEL.value: """
        PDF documents, Word files, semantic search in documents, lookup by ID,
        account numbers, customer information, greetings, thanks, casual conversation,
        file search, document retrieval
    """
}

# Pre-compute embeddings at module load (one-time cost)
_route_embeddings = {
    route: _embedding_model.encode(desc, convert_to_tensor=False)
    for route, desc in ROUTE_DESCRIPTIONS.items()
}


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


@lru_cache(maxsize=512)  
def route_with_embeddings(query: str) -> str:
    """
    Route query using sentence transformer embeddings.
    Fast (~50ms) and accurate for most queries.
    """
    query_embedding = _embedding_model.encode(query, convert_to_tensor=False)
    
    similarities = {
        route: cosine_similarity(query_embedding, route_emb)
        for route, route_emb in _route_embeddings.items()
    }
    
    best_route = max(similarities, key=similarities.get)
    confidence = similarities[best_route]
    
    # If confidence is too low, fall back to keyword matching
    if confidence < 0.3:
        return route_with_keywords(query)
    
    return best_route


# ══════════════════════════════════════════════════════════════════════════════
# KEYWORD FALLBACK (Tier 2 - for edge cases)
# ══════════════════════════════════════════════════════════════════════════════

SQL_KEYWORDS = frozenset([
    "average", "sum", "count", "total", "calculate", "correlation", "corr",
    "group", "filter", "where", "top", "bottom", "rank", "trend", "aggregate",
    "query", "table", "database", "csv", "mean", "median", "std", "variance",
    "join", "merge", "pivot", "compare", "analysis", "statistics",
    "pm25", "pm10", "pm2.5", "air quality", "pollution", "sensor", "parameter",
    "location", "datetime", "value", "units", "measurement"
])

FINANCE_KEYWORDS = frozenset([
    "stock", "price", "market", "ticker", "earnings", "revenue", "profit",
    "analyst", "rating", "quote", "dividend", "ratio", "balance", "cash flow",
    "aapl", "tsla", "msft", "googl", "amzn", "meta", "nvda", "financial"
])

WEB_KEYWORDS = frozenset([
    "news", "latest", "current", "today", "search", "recent", "happening",
    "update", "article", "web", "internet", "google", "online"
])

MODEL_KEYWORDS = frozenset([
    "document", "pdf", "file", "lookup", "find", "search", "account",
    "customer", "id", "hello", "hi", "thanks", "thank", "help", "please"
])


def route_with_keywords(query: str) -> str:
    """
    Fallback keyword-based routing.
    Used when embedding confidence is low.
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    # Count keyword matches
    scores = {
        RouteTarget.SQL.value: len(query_words & SQL_KEYWORDS),
        RouteTarget.FINANCE.value: len(query_words & FINANCE_KEYWORDS),
        RouteTarget.WEB_SEARCH.value: len(query_words & WEB_KEYWORDS),
        RouteTarget.MODEL.value: len(query_words & MODEL_KEYWORDS),
    }
    
    max_score = max(scores.values())
    
    # If no keywords match, default to model (handles greetings, etc.)
    if max_score == 0:
        return RouteTarget.MODEL.value
    
    return max(scores, key=scores.get)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def fast_route(query: str) -> str:
    """
    Main routing function.
    Uses embeddings first (accurate + fast), keywords as fallback.
    """
    import time
    start = time.time()
    result = route_with_embeddings(query)
    elapsed = (time.time() - start) * 1000
    
    # print(f"FAST_ROUTE: '{query[:50]}...' → {result} ({elapsed:.2f}ms)")
    
    return result