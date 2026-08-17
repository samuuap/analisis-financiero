"""Provider protocols used for dependency inversion.

Agents depend on these protocols, never on ``yfinance`` or ``ddgs`` directly,
so the data layer can be swapped (e.g. for mock mode) without touching the
analysis logic.
"""

from __future__ import annotations

from typing import Protocol

from src.models.market import MarketData
from src.models.news import NewsItem


class MarketDataProvider(Protocol):
    def get_market_data(self, ticker: str, period: str, interval: str) -> MarketData:
        """Fetch OHLCV history and summary fields for ``ticker``."""


class NewsProvider(Protocol):
    def search(self, ticker: str, limit: int) -> list[NewsItem]:
        """Return up to ``limit`` recent news items for ``ticker``."""
