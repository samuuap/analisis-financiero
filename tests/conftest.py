"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from src.config.settings import Settings
from src.tools.market_data import MockMarketDataProvider
from src.tools.news import MockNewsProvider


@pytest.fixture
def settings_no_key() -> Settings:
    """Settings with no DeepSeek key, so mock/offline paths never touch the API."""
    return Settings(deepseek_api_key="")


@pytest.fixture
def mock_news_provider() -> MockNewsProvider:
    return MockNewsProvider()


@pytest.fixture
def mock_market_provider() -> MockMarketDataProvider:
    return MockMarketDataProvider()
