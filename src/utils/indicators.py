"""Pure-Python technical indicators computed with pandas/numpy.

All functions operate on pandas ``Series`` (or the OHLCV ``DataFrame``) so the
heavy lifting stays deterministic and free of any LLM dependency.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.models.enums import Sentiment
from src.models.market import MarketData
from src.models.technical import TechnicalAnalysis
from src.utils.i18n import normalize_language, sentiment_label


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Wilder's RSI."""
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / window, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def macd(
    series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Wilder's Average True Range."""
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1.0 / window, adjust=False).mean()


def rolling_volatility(
    close: pd.Series, window: int = 20, periods_per_year: int = 252
) -> pd.Series:
    """Annualized rolling standard deviation of daily returns."""
    returns = close.pct_change()
    return returns.rolling(window=window, min_periods=window).std() * (periods_per_year**0.5)


def _last(series: pd.Series) -> float | None:
    if series.empty:
        return None
    value = series.iloc[-1]
    return None if pd.isna(value) else float(value)


def compute_all(df: pd.DataFrame) -> dict[str, Any]:
    """Compute every indicator from an OHLCV DataFrame and return scalars.

    ``df`` must contain columns ``open``, ``high``, ``low``, ``close`` and
    ``volume`` (a datetime index is assumed but not required).
    """
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    macd_line, signal_line, histogram = macd(close)

    high_52w = float(high.tail(252).max()) if len(high) else None
    low_52w = float(low.tail(252).min()) if len(low) else None

    avg_volume = float(volume.tail(20).mean()) if len(volume) else None
    latest_volume = float(volume.iloc[-1]) if len(volume) else None
    volume_ratio = (latest_volume / avg_volume) if avg_volume and avg_volume > 0 else None

    return {
        "price": _last(close),
        "sma20": _last(sma(close, 20)),
        "sma50": _last(sma(close, 50)),
        "sma200": _last(sma(close, 200)),
        "ema20": _last(ema(close, 20)),
        "rsi14": _last(rsi(close, 14)),
        "macd": _last(macd_line),
        "macd_signal": _last(signal_line),
        "macd_histogram": _last(histogram),
        "atr14": _last(atr(high, low, close, 14)),
        "volatility": _last(rolling_volatility(close, 20)),
        "high_52w": high_52w,
        "low_52w": low_52w,
        "volume_ratio": volume_ratio,
    }


def determine_technical_signal(ind: dict[str, Any]) -> Sentiment:
    """Aggregate indicator values into a deterministic technical signal."""
    score = 0

    price = ind.get("price")
    ema20 = ind.get("ema20")
    sma20 = ind.get("sma20")
    sma50 = ind.get("sma50")
    sma200 = ind.get("sma200")
    rsi14 = ind.get("rsi14")
    macd_h = ind.get("macd_histogram")

    if price is not None and ema20 is not None:
        score += 1 if price > ema20 else -1 if price < ema20 else 0
    if sma20 is not None and sma50 is not None:
        score += 1 if sma20 > sma50 else -1 if sma20 < sma50 else 0
    if sma200 is not None and price is not None:
        score += 1 if price > sma200 else -1 if price < sma200 else 0
    if macd_h is not None:
        score += 1 if macd_h > 0 else -1 if macd_h < 0 else 0
    if rsi14 is not None:
        if rsi14 > 70:
            score -= 1  # overbought
        elif rsi14 < 30:
            score += 1  # oversold

    if score >= 2:
        return Sentiment.BULLISH
    if score <= -2:
        return Sentiment.BEARISH
    return Sentiment.NEUTRAL


def build_technical_analysis(market_data: MarketData, language: str = "en") -> TechnicalAnalysis:
    """Compute every indicator from ``MarketData`` and package a ``TechnicalAnalysis``."""
    ind = compute_all(market_data.to_dataframe())
    signal = determine_technical_signal(ind)
    summary = _summarize_technical(ind, signal, language)
    return TechnicalAnalysis(
        ticker=market_data.symbol,
        sma20=ind["sma20"],
        sma50=ind["sma50"],
        sma200=ind["sma200"],
        ema20=ind["ema20"],
        rsi14=ind["rsi14"],
        macd=ind["macd"],
        macd_signal=ind["macd_signal"],
        macd_histogram=ind["macd_histogram"],
        atr14=ind["atr14"],
        volatility=ind["volatility"],
        high_52w=ind["high_52w"],
        low_52w=ind["low_52w"],
        volume_ratio=ind["volume_ratio"],
        signal=signal,
        summary=summary,
    )


def _summarize_technical(ind: dict[str, Any], signal: Sentiment, language: str = "en") -> str:
    es = normalize_language(language) == "es"
    parts: list[str] = []
    if ind.get("price") is not None:
        parts.append(f"{'precio' if es else 'price'} {ind['price']:.2f}")
    if ind.get("rsi14") is not None:
        parts.append(f"RSI14 {ind['rsi14']:.1f}")
    sma20, sma50 = ind.get("sma20"), ind.get("sma50")
    if sma20 is not None and sma50 is not None:
        if sma20 > sma50:
            parts.append("SMA20 por encima de SMA50" if es else "SMA20 above SMA50")
        elif sma20 < sma50:
            parts.append("SMA20 por debajo de SMA50" if es else "SMA20 below SMA50")
        else:
            parts.append("SMA20 igual a SMA50" if es else "SMA20 equal to SMA50")
    body = "; ".join(parts)
    label = sentiment_label(signal, language)
    prefix = f"Señal técnica {label}" if es else f"Technical signal {label}"
    if body:
        return f"{prefix}. {body}"
    return f"{prefix}."
