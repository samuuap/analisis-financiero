"""Unit tests for the web layer: catalog localization and FastAPI endpoints."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from src.config.settings import Settings
from src.web.app import AnalyzeRequest, _build_crew, analyze, list_tickers
from src.web.catalog import CATALOG, get_catalog, is_known_symbol


def test_catalog_has_expected_entries():
    assert len(CATALOG) == 50
    symbols = [entry["symbol"] for entry in CATALOG]
    assert "NVDA" in symbols
    assert "AAPL" in symbols
    assert "XOM" in symbols


def test_get_catalog_english_shape():
    entries = get_catalog("en")
    assert len(entries) == len(CATALOG)
    for entry in entries:
        assert set(entry) == {
            "symbol",
            "name",
            "sector",
            "description",
            "trending",
            "color",
            "logo",
        }
        assert entry["description"]
        assert isinstance(entry["trending"], bool)


def test_get_catalog_spanish_localizes():
    en = {e["symbol"]: e for e in get_catalog("en")}
    es = {e["symbol"]: e for e in get_catalog("es")}
    assert es["NVDA"]["sector"] == "Semiconductores"
    assert es["NVDA"]["description"] != en["NVDA"]["description"]
    assert es["JPM"]["sector"] == "Banca"


def test_get_catalog_defaults_to_english():
    assert get_catalog() == get_catalog("en")
    assert get_catalog("fr") == get_catalog("en")


def test_is_known_symbol():
    assert is_known_symbol("NVDA") is True
    assert is_known_symbol("nvda") is True
    assert is_known_symbol("  aapl  ") is True
    assert is_known_symbol("FAKE") is False
    assert is_known_symbol("") is False


def test_analyze_request_defaults():
    req = AnalyzeRequest(symbol="NVDA")
    assert req.language == "en"
    assert req.mock is False


def test_list_tickers_normalizes_language():
    result = list_tickers(language="es")
    assert result["language"] == "es"
    assert result["tickers"][0]["sector"] == "Semiconductores"

    default = list_tickers(language=None)
    assert default["language"] == "en"


def test_build_crew_degrades_to_mock_without_key(settings_no_key: Settings):
    crew, mock = _build_crew(False, settings_no_key)
    assert mock is True


def test_build_crew_uses_mock_when_requested(settings_no_key: Settings):
    crew, mock = _build_crew(True, settings_no_key)
    assert mock is True


def test_analyze_rejects_unknown_symbol():
    with pytest.raises(HTTPException) as exc_info:
        analyze(AnalyzeRequest(symbol="FAKE", mock=True))
    assert exc_info.value.status_code == 400


def test_analyze_returns_report_for_known_symbol_mock():
    payload = analyze(AnalyzeRequest(symbol="NVDA", mock=True))
    assert payload["ticker"] == "NVDA"
    assert payload["mock"] is True
    assert payload["language"] == "en"
    assert payload["recommendation"]["action"] in {"BUY", "HOLD", "SELL"}
    assert "summary" in payload["recommendation"]


def test_analyze_honors_language():
    payload = analyze(AnalyzeRequest(symbol="AAPL", language="ES", mock=True))
    assert payload["language"] == "es"
