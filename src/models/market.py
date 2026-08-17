"""Market data models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MarketData(BaseModel):
    """OHLCV series plus summary fields for a ticker.

    Series are stored as plain ``list[float]`` (and dates as ``list[str]``) so
    the model serializes cleanly to JSON for the strategist agent.
    """

    ticker: str
    symbol: str
    price: float
    currency: str = "USD"
    market_data_timestamp: datetime | None = None
    dates: list[str] = Field(default_factory=list)
    open: list[float] = Field(default_factory=list)
    high: list[float] = Field(default_factory=list)
    low: list[float] = Field(default_factory=list)
    close: list[float] = Field(default_factory=list)
    volume: list[float] = Field(default_factory=list)
    high_52w: float | None = None
    low_52w: float | None = None
    volume_ratio: float | None = None

    @property
    def is_valid(self) -> bool:
        return bool(self.close) and len(self.close) == len(self.dates) and self.price > 0

    def to_dataframe(self):
        """Reconstruct an OHLCV ``pandas.DataFrame`` for indicator computation."""
        import pandas as pd

        return pd.DataFrame(
            {
                "open": self.open,
                "high": self.high,
                "low": self.low,
                "close": self.close,
                "volume": self.volume,
            }
        )
