"""Integration tests that hit real external services (DeepSeek, Yahoo, DuckDuckGo).

Run explicitly with:  pytest -m integration
These are skipped automatically when DEEPSEEK_API_KEY is not present.
"""

from __future__ import annotations

import os

import pytest
from src.config.settings import Settings
from src.crew.market_crew import MarketCrew
from src.models.enums import Action
from src.tools.market_data import YahooMarketDataProvider
from src.tools.news import DuckDuckGoNewsProvider

pytestmark = pytest.mark.integration

requires_key = pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY"),
    reason="DEEPSEEK_API_KEY is not set; skipping live integration test.",
)


@requires_key
def test_end_to_end_real_analysis():
    settings = Settings.from_env()
    crew = MarketCrew(
        news_provider=DuckDuckGoNewsProvider(ttl_seconds=settings.news_ttl_seconds),
        market_data_provider=YahooMarketDataProvider(),
        settings=settings,
    )
    report = crew.run(ticker="AAPL", period="1mo", interval="1d", news_limit=3, mock=False)
    assert report.ticker == "AAPL"
    assert report.recommendation.action in {Action.BUY, Action.HOLD, Action.SELL}
    assert 0.0 <= report.recommendation.confidence <= 1.0
