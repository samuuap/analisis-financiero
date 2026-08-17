"""News-related data models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.models.enums import Sentiment


class NewsItem(BaseModel):
    """A single news article returned by a news provider."""

    title: str
    url: str | None = None
    source: str = "unknown"
    published: str | None = None
    snippet: str = ""


class NewsAnalysis(BaseModel):
    """Aggregated news analysis for a ticker, with a deterministic sentiment."""

    ticker: str
    items: list[NewsItem] = Field(default_factory=list)
    sentiment: Sentiment = Sentiment.NEUTRAL
    summary: str = ""
    key_themes: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)

    @property
    def item_count(self) -> int:
        return len(self.items)
