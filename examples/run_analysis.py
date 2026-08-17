"""Runnable example: analyze a ticker with ``market-ai-agents``.

Usage::

    python examples/run_analysis.py NVDA --mock
    python examples/run_analysis.py NVDA --period 6mo --json

The ``--mock`` flag runs offline with deterministic data and no API keys.
"""

from __future__ import annotations

import argparse
import json
import sys

from src.config.settings import Settings
from src.crew.market_crew import MarketCrew
from src.models.strategy import MarketReport
from src.tools.market_data import MockMarketDataProvider, YahooMarketDataProvider
from src.tools.news import DuckDuckGoNewsProvider, MockNewsProvider


def _render(report: MarketReport) -> str:
    rec = report.recommendation
    return (
        f"Ticker         : {report.ticker}\n"
        f"Execution id   : {report.execution_id}\n"
        f"Model          : {report.model}\n"
        f"Recommendation : {rec.action.value} (confidence {rec.confidence:.2f})\n"
        f"Summary        : {rec.summary}\n"
        f"Sources        : {len(report.sources)}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze a ticker with market-ai-agents.")
    parser.add_argument("ticker", help="Ticker symbol (e.g. NVDA).")
    parser.add_argument("--period", default="1y", help="Price-history period (default 1y).")
    parser.add_argument("--interval", default="1d", help="Price-history interval (default 1d).")
    parser.add_argument("--news-limit", type=int, default=10, help="Max news items (default 10).")
    parser.add_argument("--mock", action="store_true", help="Run offline with mock data.")
    parser.add_argument("--json", action="store_true", help="Print the full report as JSON.")
    args = parser.parse_args(argv)

    settings = Settings.from_env()

    if args.mock:
        news_provider = MockNewsProvider()
        market_provider = MockMarketDataProvider()
    else:
        news_provider = DuckDuckGoNewsProvider(ttl_seconds=settings.news_ttl_seconds)
        market_provider = YahooMarketDataProvider()

    crew = MarketCrew(
        news_provider=news_provider,
        market_data_provider=market_provider,
        settings=settings,
    )
    report = crew.run(
        ticker=args.ticker,
        period=args.period,
        interval=args.interval,
        news_limit=args.news_limit,
        mock=args.mock,
    )

    if args.json:
        print(json.dumps(json.loads(report.model_dump_json()), indent=2))
    else:
        print(_render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
