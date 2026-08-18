"""FastAPI backend for the ``market-ai-agents`` web UI.

Exposes a curated company catalog (so users never need to know ticker symbols),
a language toggle (EN/ES), and an analysis endpoint that returns the full
``MarketReport``. Analysis only — never order execution, never a broker.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config.settings import Settings
from src.crew.market_crew import MarketCrew
from src.tools.market_data import MockMarketDataProvider, YahooMarketDataProvider
from src.tools.news import DuckDuckGoNewsProvider, MockNewsProvider
from src.utils.errors import ConfigurationError, InvalidTickerError, MarketAIAgentsError
from src.utils.i18n import normalize_language
from src.web.catalog import get_catalog, is_known_symbol

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Market AI Agents",
    description=(
        "Multi-agent stock analysis: pick a company, choose a language, and receive "
        "a BUY/HOLD/SELL report. Analysis only — no order execution, no broker."
    ),
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AnalyzeRequest(BaseModel):
    """Request body for ``POST /api/analyze``."""

    symbol: str
    language: str = "en"
    mock: bool = False
    depth: str = "standard"


@app.get("/")
def index() -> FileResponse:
    """Serve the single-page frontend."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/tickers")
def list_tickers(language: str | None = Query(default=None)) -> dict:
    """Return the curated company catalog, localized for ``language``."""
    return {"language": normalize_language(language), "tickers": get_catalog(language)}


def _build_crew(mock: bool, settings: Settings) -> tuple[MarketCrew, bool]:
    """Construct the crew for real or mock mode.

    When no DeepSeek key is configured, the app silently degrades to mock mode so
    the UI still works end-to-end offline. Returns ``(crew, effective_mock)``.
    """
    if mock or not settings.has_deepseek_key:
        crew = MarketCrew(
            news_provider=MockNewsProvider(),
            market_data_provider=MockMarketDataProvider(),
            settings=settings,
        )
        return crew, True
    crew = MarketCrew(
        news_provider=DuckDuckGoNewsProvider(ttl_seconds=settings.news_ttl_seconds),
        market_data_provider=YahooMarketDataProvider(),
        settings=settings,
    )
    return crew, False


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    """Run the full pipeline for ``symbol`` and return the ``MarketReport``."""
    language = normalize_language(request.language)
    depth = "deep" if request.depth == "deep" else "standard"
    symbol = (request.symbol or "").strip().upper()
    if not is_known_symbol(symbol):
        raise HTTPException(
            status_code=400,
            detail="Unknown ticker. Please select a company from the catalog.",
        )

    settings = Settings.from_env()
    crew, mock = _build_crew(request.mock, settings)
    try:
        report = crew.run(ticker=symbol, mock=mock, language=language, depth=depth)
    except InvalidTickerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except MarketAIAgentsError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    payload = report.model_dump(mode="json")
    payload["language"] = language
    payload["mock"] = mock
    return payload
