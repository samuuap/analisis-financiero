"""Deterministic, lexical news-sentiment classification (no LLM involved)."""

from __future__ import annotations

from src.models.enums import Sentiment
from src.models.news import NewsAnalysis, NewsItem
from src.utils.i18n import normalize_language, sentiment_label

BULLISH_TERMS = {
    "beat",
    "beats",
    "growth",
    "grow",
    "surge",
    "surges",
    "soar",
    "soars",
    "rally",
    "rallies",
    "upgrade",
    "upgraded",
    "outperform",
    "strong",
    "record",
    "profit",
    "profits",
    "bullish",
    "gain",
    "gains",
    "rise",
    "rises",
    "higher",
    "outlook",
    "buyback",
    "dividend",
    "expansion",
    "partnership",
    "wins",
    "win",
    "approval",
    "breakthrough",
    "positive",
    "beat expectations",
    "raised guidance",
    "upside",
    "accelerate",
    "revenue growth",
}

BEARISH_TERMS = {
    "miss",
    "misses",
    "decline",
    "declines",
    "fall",
    "falls",
    "drop",
    "drops",
    "plunge",
    "plunges",
    "downgrade",
    "downgraded",
    "underperform",
    "weak",
    "loss",
    "losses",
    "bearish",
    "lawsuit",
    "layoff",
    "layoffs",
    "recall",
    "investigation",
    "fraud",
    "negative",
    "missed expectations",
    "lowered guidance",
    "downside",
    "cut",
    "cuts",
    "risk",
    "risks",
    "warning",
    "warns",
    "selloff",
    "crash",
    "debt",
    "bankruptcy",
    "delisting",
    "short",
    "slump",
    "slumps",
}


def classify_text(text: str) -> Sentiment:
    """Classify a single piece of text by counting bullish vs bearish terms."""
    lowered = (text or "").lower()
    bullish = sum(1 for term in BULLISH_TERMS if term in lowered)
    bearish = sum(1 for term in BEARISH_TERMS if term in lowered)
    if bullish > bearish:
        return Sentiment.BULLISH
    if bearish > bullish:
        return Sentiment.BEARISH
    return Sentiment.NEUTRAL


def classify_news(items: list[NewsItem]) -> Sentiment:
    """Aggregate per-item sentiment into a single directional signal."""
    score = 0
    for item in items:
        s = classify_text(f"{item.title} {item.snippet}")
        if s is Sentiment.BULLISH:
            score += 1
        elif s is Sentiment.BEARISH:
            score -= 1
    if score > 0:
        return Sentiment.BULLISH
    if score < 0:
        return Sentiment.BEARISH
    return Sentiment.NEUTRAL


def build_news_analysis(ticker: str, items: list[NewsItem], language: str = "en") -> NewsAnalysis:
    """Assemble a ``NewsAnalysis`` from raw items (sentiment + summary)."""
    sentiment = classify_news(items)
    sources = sorted({item.source for item in items if item.source})
    themes = [item.title for item in items[:5]]
    label = sentiment_label(sentiment, language)
    if normalize_language(language) == "es":
        summary = (
            f"Se encontraron {len(items)} noticia(s) para {ticker}; "
            f"el sentimiento general es {label}."
        )
    else:
        summary = (
            f"Found {len(items)} news item(s) for {ticker}; "
            f"overall sentiment is {label}."
        )
    return NewsAnalysis(
        ticker=ticker,
        items=items,
        sentiment=sentiment,
        summary=summary,
        key_themes=themes,
        sources=sources,
    )
