"""Market data providers: Yahoo Finance (live) and a deterministic mock."""

from __future__ import annotations

import math
import re
from datetime import UTC, datetime, timedelta

from src.models.market import MarketData
from src.utils.errors import InvalidTickerError, MarketDataError

_TICKER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9.\-]{0,9}$")

_REQUIRED_COLUMNS = {"open", "high", "low", "close", "volume"}


def validate_ticker(ticker: str) -> str:
    """Normalize and validate a ticker symbol."""
    symbol = (ticker or "").strip().upper()
    if not _TICKER_RE.match(symbol):
        raise InvalidTickerError(f"Invalid ticker symbol: {ticker!r}")
    return symbol


class YahooMarketDataProvider:
    """Fetch OHLCV history via ``yfinance``."""

    def get_market_data(self, ticker: str, period: str = "1y", interval: str = "1d") -> MarketData:
        symbol = validate_ticker(ticker)
        try:
            import yfinance as yf
        except ImportError as exc:  # pragma: no cover - dependency present
            raise MarketDataError("yfinance is not installed.") from exc

        try:
            hist = yf.Ticker(symbol).history(period=period, interval=interval)
        except Exception as exc:
            raise MarketDataError(f"Failed to fetch market data for {symbol}: {exc}") from exc

        if hist is None or hist.empty:
            raise MarketDataError(f"No market data returned for ticker {symbol}.")

        df = hist.copy()
        df.columns = [str(c).lower().strip() for c in df.columns]
        if not _REQUIRED_COLUMNS.issubset(set(df.columns)):
            raise MarketDataError(f"Market data for {symbol} is missing required columns.")

        df = df.dropna(subset=list(_REQUIRED_COLUMNS))
        if df.empty:
            raise MarketDataError(f"Market data for {symbol} contained no valid rows.")

        if "date" in df.columns:
            date_col = "date"
        elif "datetime" in df.columns:
            date_col = "datetime"
        else:
            date_col = None
        if date_col:
            dates = [str(value)[:10] for value in df[date_col]]
        else:
            dates = [str(i) for i in range(len(df))]

        closes = [float(v) for v in df["close"]]
        price = closes[-1]
        if price <= 0:
            raise MarketDataError(f"Invalid (non-positive) price for {symbol}.")

        high_52w = float(df["high"].tail(252).max()) if len(df) else None
        low_52w = float(df["low"].tail(252).min()) if len(df) else None
        avg_volume = float(df["volume"].tail(20).mean()) if len(df) else None
        latest_volume = float(df["volume"].iloc[-1]) if len(df) else None
        volume_ratio = (latest_volume / avg_volume) if avg_volume and avg_volume > 0 else None

        return MarketData(
            ticker=symbol,
            symbol=symbol,
            price=price,
            currency="USD",
            market_data_timestamp=datetime.now(UTC),
            dates=dates,
            open=[float(v) for v in df["open"]],
            high=[float(v) for v in df["high"]],
            low=[float(v) for v in df["low"]],
            close=closes,
            volume=[float(v) for v in df["volume"]],
            high_52w=high_52w,
            low_52w=low_52w,
            volume_ratio=volume_ratio,
        )


class MockMarketDataProvider:
    """Deterministic OHLCV series (upward drift) for offline/mock runs."""

    def get_market_data(self, ticker: str, period: str = "1y", interval: str = "1d") -> MarketData:
        symbol = validate_ticker(ticker)
        n = 260
        base = 100.0
        end = datetime.now()
        dates = [(end - timedelta(days=n - 1 - i)).date().isoformat() for i in range(n)]

        opens: list[float] = []
        highs: list[float] = []
        lows: list[float] = []
        closes: list[float] = []
        volumes: list[float] = []
        for i in range(n):
            close = base + i * 0.25 + math.sin(i / 10.0) * 5.0
            opens.append(close - 0.5)
            highs.append(close + 1.0)
            lows.append(close - 1.0)
            closes.append(round(close, 2))
            volumes.append(1_000_000.0 + i * 1_000.0)

        return MarketData(
            ticker=symbol,
            symbol=symbol,
            price=closes[-1],
            currency="USD",
            market_data_timestamp=datetime.now(UTC),
            dates=dates,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            volume=volumes,
            high_52w=max(highs),
            low_52w=min(lows),
            volume_ratio=volumes[-1] / (sum(volumes[-20:]) / 20.0),
        )
