"""Unit tests for the MarketCrew orchestration (mock mode)."""

from __future__ import annotations

import pytest
from src.crew.market_crew import MarketCrew
from src.models.enums import Action
from src.utils.errors import ConfigurationError, InvalidTickerError


def _crew(settings_no_key, mock_news_provider, mock_market_provider):
    return MarketCrew(
        news_provider=mock_news_provider,
        market_data_provider=mock_market_provider,
        settings=settings_no_key,
    )


def test_run_mock_returns_well_formed_report(
    settings_no_key, mock_news_provider, mock_market_provider
):
    report = _crew(settings_no_key, mock_news_provider, mock_market_provider).run(
        ticker="NVDA", mock=True
    )
    assert report.ticker == "NVDA"
    assert report.execution_id
    assert report.recommendation.action is Action.HOLD
    assert report.recommendation.confidence == 0.5
    assert "mock" in report.model
    assert report.price is not None and report.price > 0
    assert report.news_analysis is not None
    assert report.news_analysis.item_count == 3
    assert report.technical_analysis is not None
    assert report.high_52w is not None
    assert report.low_52w is not None


def test_run_without_key_and_no_mock_raises(
    settings_no_key, mock_news_provider, mock_market_provider
):
    with pytest.raises(ConfigurationError):
        _crew(settings_no_key, mock_news_provider, mock_market_provider).run(
            ticker="NVDA", mock=False
        )


def test_run_invalid_ticker_raises(settings_no_key, mock_news_provider, mock_market_provider):
    with pytest.raises(InvalidTickerError):
        _crew(settings_no_key, mock_news_provider, mock_market_provider).run(
            ticker="!bad!", mock=True
        )
