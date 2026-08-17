"""Unit tests for news providers."""

from __future__ import annotations

import sys
import types

import pytest
from src.tools import news
from src.utils import errors


def test_sanitize_truncates_and_strips():
    assert news._sanitize("  hello world  ", 5) == "hello"
    assert news._sanitize(None, 5) == ""
    assert news._sanitize("a\x00b", 10) == "ab"


def test_to_item_maps_fields():
    item = news._to_item(
        {
            "title": "Great news",
            "body": "This is a snippet body",
            "date": "2026-08-17",
            "url": "https://example.com/x",
            "source": "Reuters",
        }
    )
    assert item.title == "Great news"
    assert item.snippet == "This is a snippet body"
    assert item.published == "2026-08-17"
    assert item.url == "https://example.com/x"
    assert item.source == "Reuters"


def test_to_item_defaults():
    item = news._to_item({"title": "Only title"})
    assert item.url is None
    assert item.source == "unknown"
    assert item.published is None
    assert item.snippet == ""


def test_mock_news_provider_returns_items(mock_news_provider):
    items = mock_news_provider.search("AAPL", limit=3)
    assert len(items) == 3
    for item in items:
        assert item.source == "MockNews"
        assert item.title
        assert item.url


def test_mock_news_provider_respects_limit(mock_news_provider):
    items = mock_news_provider.search("AAPL", limit=1)
    assert len(items) == 1
    assert items[0].title.startswith("AAPL")


def test_mock_news_provider_invalid_ticker(mock_news_provider):
    with pytest.raises(errors.InvalidTickerError):
        mock_news_provider.search("!bad!", 3)


def test_duckduckgo_empty_results_raises(monkeypatch):
    fake_ddgs = types.ModuleType("ddgs")

    class FakeDDGS:
        def news(self, query=None, region=None, safesearch=None, max_results=None):
            return []

    fake_ddgs.DDGS = FakeDDGS
    monkeypatch.setitem(sys.modules, "ddgs", fake_ddgs)
    provider = news.DuckDuckGoNewsProvider()
    with pytest.raises(errors.NewsError):
        provider.search("NVDA", 5)
