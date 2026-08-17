"""Core enumerations shared across the analysis pipeline."""

from enum import StrEnum


class Action(StrEnum):
    """Final investment action emitted by the strategist."""

    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class Sentiment(StrEnum):
    """Directional sentiment for a signal or a set of news items."""

    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
