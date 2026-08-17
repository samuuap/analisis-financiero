"""Unit tests for market-data providers and ticker validation."""

from __future__ import annotations

import sys
import types

import pandas as pd
import pytest
from src.tools import market_data
from src.utils import errors


def test_validate_ticker_normalizes():
    assert market_data.validate_ticker("  nvda ") == "NVDA"
    assert market_data.validate_ticker("brk-b") == "BRK-B"
    assert market_data.validate_ticker("VTI") == "VTI"


@pytest.mark.parametrize("bad", ["", "  ", "123", "A" * 20, "!!", "N VDA"])
def test_validate_ticker_invalid(bad):
    with pytest.raises(errors.InvalidTickerError):
        market_data.validate_ticker(bad)


def test_mock_market_data_is_valid(mock_market_provider):
    data = mock_market_provider.get_market_data("AAPL")
    assert data.ticker == "AAPL"
    assert data.symbol == "AAPL"
    assert data.is_valid
    assert data.price > 0
    assert len(data.close) == 260
    assert len(data.dates) == 260
    assert data.high_52w >= data.low_52w
    assert data.volume_ratio is not None


def test_mock_market_data_to_dataframe(mock_market_provider):
    data = mock_market_provider.get_market_data("MSFT")
    df = data.to_dataframe()
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 260


def test_yahoo_empty_dataframe_raises(monkeypatch):
    fake_yf = types.ModuleType("yfinance")

    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self, period="1y", interval="1d"):
            return pd.DataFrame()

    fake_yf.Ticker = FakeTicker
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
    provider = market_data.YahooMarketDataProvider()
    with pytest.raises(errors.MarketDataError):
        provider.get_market_data("NVDA")


def test_yahoo_valid_data_maps_fields(monkeypatch):
    fake_yf = types.ModuleType("yfinance")

    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self, period="1y", interval="1d"):
            return pd.DataFrame(
                {
                    "Open": [10, 11, 12, 13, 14],
                    "High": [11, 12, 13, 14, 15],
                    "Low": [9, 10, 11, 12, 13],
                    "Close": [10.5, 11.5, 12.5, 13.5, 14.5],
                    "Volume": [1000, 1100, 1200, 1300, 1400],
                }
            )

    fake_yf.Ticker = FakeTicker
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
    data = market_data.YahooMarketDataProvider().get_market_data("NVDA")
    assert data.price == pytest.approx(14.5)
    assert data.high_52w == pytest.approx(15.0)
    assert data.low_52w == pytest.approx(9.0)
