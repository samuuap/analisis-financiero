"""Unit tests for the EN/ES localization helpers."""

from __future__ import annotations

from src.models.enums import Sentiment
from src.utils.i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    normalize_language,
    sentiment_label,
    strategy_language_directive,
)


def test_supported_languages():
    assert SUPPORTED_LANGUAGES == ("en", "es")
    assert DEFAULT_LANGUAGE == "en"


def test_normalize_language_returns_supported_code():
    assert normalize_language("es") == "es"
    assert normalize_language("EN") == "en"
    assert normalize_language(" Es ") == "es"


def test_normalize_language_falls_back_to_default():
    assert normalize_language(None) == "en"
    assert normalize_language("") == "en"
    assert normalize_language("fr") == "en"
    assert normalize_language("spanish") == "en"


def test_strategy_language_directive():
    assert "English" in strategy_language_directive("en")
    assert "español" in strategy_language_directive("es")


def test_sentiment_label_localizes():
    assert sentiment_label(Sentiment.BULLISH, "es") == "alcista"
    assert sentiment_label(Sentiment.NEUTRAL, "es") == "neutral"
    assert sentiment_label(Sentiment.BEARISH, "es") == "bajista"
    assert sentiment_label(Sentiment.BULLISH, "en") == "bullish"
    assert sentiment_label(Sentiment.BEARISH, "en") == "bearish"


def test_sentiment_label_falls_back_to_english():
    assert sentiment_label(Sentiment.BULLISH, "fr") == "bullish"
