"""Unit tests for Pydantic models and enums."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from src.models.enums import Action, Sentiment
from src.models.market import MarketData
from src.models.news import NewsAnalysis, NewsItem
from src.models.strategy import StrategyRecommendation


def test_action_enum_values():
    assert {a.value for a in Action} == {"BUY", "HOLD", "SELL"}


def test_sentiment_enum_values():
    assert {s.value for s in Sentiment} == {"BULLISH", "NEUTRAL", "BEARISH"}


def test_confidence_upper_bound():
    with pytest.raises(ValidationError):
        StrategyRecommendation(ticker="NVDA", confidence=1.5)


def test_confidence_lower_bound():
    with pytest.raises(ValidationError):
        StrategyRecommendation(ticker="NVDA", confidence=-0.1)


def test_strategy_recommendation_defaults():
    rec = StrategyRecommendation(ticker="NVDA")
    assert rec.action is Action.HOLD
    assert rec.confidence == 0.0
    assert rec.bullish_factors == []
    assert rec.bearish_factors == []


def test_market_data_is_valid():
    data = MarketData(
        ticker="NVDA",
        symbol="NVDA",
        price=100.0,
        dates=["2026-01-01", "2026-01-02"],
        open=[99.0, 100.0],
        high=[101.0, 102.0],
        low=[98.0, 99.0],
        close=[99.0, 100.0],
        volume=[1000.0, 1100.0],
    )
    assert data.is_valid
    df = data.to_dataframe()
    assert df.shape == (2, 5)
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]


def test_market_data_invalid_when_empty():
    data = MarketData(ticker="NVDA", symbol="NVDA", price=100.0)
    assert not data.is_valid


def test_news_analysis_item_count():
    analysis = NewsAnalysis(
        ticker="NVDA",
        items=[NewsItem(title="a"), NewsItem(title="b"), NewsItem(title="c")],
    )
    assert analysis.item_count == 3
