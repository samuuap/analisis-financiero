"""Technical analysis models."""

from __future__ import annotations

from pydantic import BaseModel

from src.models.enums import Sentiment


class TechnicalAnalysis(BaseModel):
    """Indicator values and an aggregated technical signal.

    Every metric may be ``None`` when there is insufficient price history to
    compute it (e.g. SMA200 with only a few months of data).
    """

    ticker: str
    sma20: float | None = None
    sma50: float | None = None
    sma200: float | None = None
    ema20: float | None = None
    rsi14: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    atr14: float | None = None
    volatility: float | None = None
    high_52w: float | None = None
    low_52w: float | None = None
    volume_ratio: float | None = None
    signal: Sentiment = Sentiment.NEUTRAL
    summary: str = ""
