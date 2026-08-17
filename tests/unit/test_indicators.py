"""Unit tests for pure-Python technical indicators."""

from __future__ import annotations

import pandas as pd
import pytest
from src.models.enums import Sentiment
from src.utils import indicators


def _series(values: list[float]) -> pd.Series:
    return pd.Series(values, dtype="float64")


def test_sma_window3():
    result = indicators.sma(_series([1, 2, 3, 4, 5]), 3)
    assert result.iloc[-1] == pytest.approx(4.0)
    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])


def test_ema_window3_adjust_false():
    result = indicators.ema(_series([1, 2, 3, 4, 5]), 3)
    assert result.iloc[-1] == pytest.approx(4.0625)


def test_rsi_strictly_increasing_is_100():
    result = indicators.rsi(_series([float(i) for i in range(1, 61)]), 14)
    assert result.iloc[-1] == pytest.approx(100.0)


def test_rsi_strictly_decreasing_is_0():
    result = indicators.rsi(_series([float(i) for i in range(60, 0, -1)]), 14)
    assert result.iloc[-1] == pytest.approx(0.0)


def test_rsi_bounded_between_0_and_100():
    values = [44, 45, 46, 45, 44, 43, 42, 44, 46, 48, 47, 45, 44, 43, 45, 47, 49, 48, 46, 45]
    result = indicators.rsi(_series([float(v) for v in values]), 14)
    valid = result.dropna()
    assert not valid.empty
    assert valid.between(0.0, 100.0).all()


def test_macd_returns_three_series():
    close = _series([float(i) for i in range(1, 60)])
    line, signal, hist = indicators.macd(close)
    assert not pd.isna(line.iloc[-1])
    assert not pd.isna(signal.iloc[-1])
    assert hist.iloc[-1] == pytest.approx(line.iloc[-1] - signal.iloc[-1])


def test_atr_positive():
    high = _series([11.0] * 30)
    low = _series([9.0] * 30)
    close = _series([10.0 + i * 0.05 for i in range(30)])
    result = indicators.atr(high, low, close, 14)
    assert result.iloc[-1] > 0


def test_rolling_volatility_nonnegative():
    close = _series([100.0 + i * 0.2 for i in range(30)])
    result = indicators.rolling_volatility(close, 20)
    assert result.iloc[-1] >= 0


def test_compute_all_returns_expected_keys():
    n = 60
    df = pd.DataFrame(
        {
            "open": [float(i) for i in range(n)],
            "high": [float(i + 1) for i in range(n)],
            "low": [float(i - 1) for i in range(n)],
            "close": [float(i) for i in range(n)],
            "volume": [1_000_000.0 + i for i in range(n)],
        }
    )
    ind = indicators.compute_all(df)
    expected_keys = {
        "price",
        "sma20",
        "sma50",
        "sma200",
        "ema20",
        "rsi14",
        "macd",
        "macd_signal",
        "macd_histogram",
        "atr14",
        "volatility",
        "high_52w",
        "low_52w",
        "volume_ratio",
    }
    assert set(ind.keys()) == expected_keys
    assert ind["price"] == pytest.approx(float(n - 1))
    assert ind["high_52w"] == pytest.approx(float(n))
    assert ind["low_52w"] == pytest.approx(-1.0)


def test_determine_technical_signal_bullish():
    ind = {
        "price": 150.0,
        "ema20": 140.0,
        "sma20": 145.0,
        "sma50": 135.0,
        "sma200": 120.0,
        "rsi14": 55.0,
        "macd_histogram": 1.5,
    }
    assert indicators.determine_technical_signal(ind) is Sentiment.BULLISH


def test_determine_technical_signal_bearish():
    ind = {
        "price": 100.0,
        "ema20": 110.0,
        "sma20": 105.0,
        "sma50": 115.0,
        "sma200": 130.0,
        "rsi14": 45.0,
        "macd_histogram": -1.5,
    }
    assert indicators.determine_technical_signal(ind) is Sentiment.BEARISH


def test_determine_technical_signal_neutral_when_flat():
    ind = {
        "price": 100.0,
        "ema20": 100.0,
        "sma20": 100.0,
        "sma50": 100.0,
        "sma200": 100.0,
        "rsi14": 50.0,
        "macd_histogram": 0.0,
    }
    assert indicators.determine_technical_signal(ind) is Sentiment.NEUTRAL


def test_build_technical_analysis_from_market_data(mock_market_provider):
    data = mock_market_provider.get_market_data("NVDA")
    ta = indicators.build_technical_analysis(data)
    assert ta.ticker == "NVDA"
    assert ta.sma20 is not None
    assert ta.sma50 is not None
    assert ta.sma200 is not None
    assert ta.ema20 is not None
    assert ta.rsi14 is not None
    assert ta.macd is not None
    assert ta.macd_signal is not None
    assert ta.macd_histogram is not None
    assert ta.atr14 is not None
    assert ta.volatility is not None
    assert ta.high_52w is not None
    assert ta.low_52w is not None
    assert ta.volume_ratio is not None
    assert ta.signal in {Sentiment.BULLISH, Sentiment.NEUTRAL, Sentiment.BEARISH}
    assert ta.summary.startswith("Technical signal ")
