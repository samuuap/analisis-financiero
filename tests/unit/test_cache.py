"""Unit tests for the TTL cache."""

from __future__ import annotations

import pytest
from src.tools.cache import TTLCache


def test_cache_set_get():
    cache = TTLCache(ttl_seconds=60)
    cache.set("k", "v")
    assert cache.get("k") == "v"
    assert "k" in cache
    assert len(cache) == 1


def test_cache_miss_returns_none():
    cache = TTLCache(ttl_seconds=60)
    assert cache.get("missing") is None
    assert "missing" not in cache


def test_cache_expiry(monkeypatch):
    clock = {"t": 1000.0}
    monkeypatch.setattr("src.tools.cache.time.time", lambda: clock["t"])
    cache = TTLCache(ttl_seconds=10)
    cache.set("k", "v")
    assert cache.get("k") == "v"
    clock["t"] = 1011.0
    assert cache.get("k") is None
    assert "k" not in cache


def test_cache_negative_ttl_raises():
    with pytest.raises(ValueError):
        TTLCache(ttl_seconds=-1)


def test_cache_purge(monkeypatch):
    clock = {"t": 1000.0}
    monkeypatch.setattr("src.tools.cache.time.time", lambda: clock["t"])
    cache = TTLCache(ttl_seconds=10)
    cache.set("expired", "v1")
    clock["t"] = 1005.0
    cache.set("fresh", "v2")
    clock["t"] = 1011.0
    cache.purge()
    assert "expired" not in cache
    assert "fresh" in cache
