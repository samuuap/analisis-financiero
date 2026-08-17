"""News providers: DuckDuckGo (live) and a deterministic mock."""

from __future__ import annotations

from src.models.news import NewsItem
from src.tools.cache import TTLCache
from src.tools.market_data import validate_ticker
from src.utils.errors import NewsError

_MAX_TITLE = 300
_MAX_SNIPPET = 500
_MAX_SOURCE = 100


def _sanitize(text: str, limit: int) -> str:
    """Strip control characters and truncate untrusted external text."""
    cleaned = (text or "").replace("\x00", "").strip()
    return cleaned[:limit]


def _to_item(raw: dict) -> NewsItem:
    snippet = raw.get("body") or raw.get("snippet") or ""
    published = raw.get("date") or raw.get("published") or None
    return NewsItem(
        title=_sanitize(str(raw.get("title") or ""), _MAX_TITLE),
        url=raw.get("url") or raw.get("link") or None,
        source=_sanitize(str(raw.get("source") or "unknown"), _MAX_SOURCE),
        published=str(published)[:200] if published else None,
        snippet=_sanitize(str(snippet), _MAX_SNIPPET),
    )


class DuckDuckGoNewsProvider:
    """Search recent news via the ``ddgs`` DuckDuckGo wrapper."""

    def __init__(self, ttl_seconds: int = 900) -> None:
        self._cache = TTLCache(ttl_seconds)

    def search(self, ticker: str, limit: int = 10) -> list[NewsItem]:
        symbol = validate_ticker(ticker)
        cache_key = f"{symbol}:{limit}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            from ddgs import DDGS
        except ImportError as exc:  # pragma: no cover - dependency present
            raise NewsError("ddgs is not installed.") from exc

        try:
            results = DDGS().news(
                query=f"{symbol} stock",
                region="us-en",
                safesearch="moderate",
                max_results=limit,
            )
        except Exception as exc:
            raise NewsError(f"News search failed for {symbol}: {exc}") from exc

        items = [_to_item(raw) for raw in results]
        if not items:
            raise NewsError(f"No news found for ticker {symbol}.")

        self._cache.set(cache_key, items)
        return items


class MockNewsProvider:
    """Deterministic, clearly-labelled mock news for offline/mock runs."""

    def search(self, ticker: str, limit: int = 10) -> list[NewsItem]:
        symbol = validate_ticker(ticker)
        items = [
            NewsItem(
                title=f"{symbol} reports strong quarterly results",
                url="https://example.com/mock/1",
                source="MockNews",
                published="2026-08-17",
                snippet=(
                    "The company beat expectations, posting record profit and raising "
                    "full-year guidance. Revenue growth accelerated year over year."
                ),
            ),
            NewsItem(
                title=f"{symbol} faces a regulatory review",
                url="https://example.com/mock/2",
                source="MockNews",
                published="2026-08-16",
                snippet=(
                    "Analysts warn of downside risk as regulators open an investigation, "
                    "citing potential weakness in compliance."
                ),
            ),
            NewsItem(
                title=f"{symbol} announces a new strategic partnership",
                url="https://example.com/mock/3",
                source="MockNews",
                published="2026-08-15",
                snippet=(
                    "The partnership is expected to accelerate growth and expand the "
                    "company's market outlook."
                ),
            ),
        ]
        return items[:limit]
