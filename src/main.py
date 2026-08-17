"""Command-line interface for ``market-ai-agents``.

Usage::

    python -m src.main --ticker NVDA
    python -m src.main --ticker NVDA --mock
    python -m src.main --ticker NVDA --json
"""

from __future__ import annotations

import argparse
import sys

from src.config.settings import Settings
from src.crew.market_crew import MarketCrew
from src.models.strategy import MarketReport
from src.tools.market_data import MockMarketDataProvider, YahooMarketDataProvider
from src.tools.news import DuckDuckGoNewsProvider, MockNewsProvider
from src.utils.errors import MarketAIAgentsError
from src.utils.logging import get_logger

logger = get_logger()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="market-ai-agents",
        description=(
            "Multi-agent stock analysis MVP: given a ticker, produce a BUY/HOLD/SELL "
            "MarketReport backed by news sentiment and technical indicators. This tool "
            "only generates analysis; it never executes orders or connects to a broker."
        ),
    )
    parser.add_argument("--ticker", required=True, help="Ticker symbol to analyze (e.g. NVDA).")
    parser.add_argument("--period", default="1y", help="Price-history period (default: 1y).")
    parser.add_argument("--interval", default="1d", help="Price-history interval (default: 1d).")
    parser.add_argument(
        "--news-limit", type=int, default=10, help="Maximum news items to fetch (default: 10)."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the full MarketReport as JSON instead of the human-readable view.",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run offline with deterministic mock data (no network, no API keys).",
    )
    return parser


def _format_report(report: MarketReport) -> str:
    rec = report.recommendation
    lines: list[str] = []
    lines.append("=" * 68)
    lines.append(f"Market Report — {report.ticker}")
    lines.append("=" * 68)
    lines.append(f"Execution id   : {report.execution_id}")
    lines.append(f"Timestamp      : {report.timestamp.isoformat()}")
    lines.append(f"Model          : {report.model}")
    if report.price is not None:
        lines.append(f"Price          : {report.price:.2f}")
    else:
        lines.append("Price: n/a")
    if report.high_52w is not None and report.low_52w is not None:
        lines.append(f"52-week range  : {report.low_52w:.2f} — {report.high_52w:.2f}")
    lines.append("")
    lines.append(f"Recommendation : {rec.action.value}")
    lines.append(f"Confidence     : {rec.confidence:.2f}")
    if report.technical_analysis is not None:
        lines.append(f"Technical      : {report.technical_analysis.summary}")
    if report.news_analysis is not None:
        lines.append(f"News           : {report.news_analysis.summary}")
    lines.append(f"Summary        : {rec.summary}")
    lines.append("")
    if rec.bullish_factors:
        lines.append("Bullish factors:")
        lines.extend(f"  - {f}" for f in rec.bullish_factors)
    if rec.bearish_factors:
        lines.append("Bearish factors:")
        lines.extend(f"  - {f}" for f in rec.bearish_factors)
    if rec.risk_factors:
        lines.append("Risks:")
        lines.extend(f"  - {f}" for f in rec.risk_factors)
    if rec.invalidating_conditions:
        lines.append("Invalidating conditions:")
        lines.extend(f"  - {f}" for f in rec.invalidating_conditions)
    if report.sources:
        lines.append("")
        lines.append("Sources:")
        lines.extend(f"  - {s}" for s in report.sources)
    lines.append("")
    lines.append(report.disclaimer)
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    settings = Settings.from_env()

    if args.mock:
        news_provider = MockNewsProvider()
        market_data_provider = MockMarketDataProvider()
    else:
        news_provider = DuckDuckGoNewsProvider(ttl_seconds=settings.news_ttl_seconds)
        market_data_provider = YahooMarketDataProvider()

    crew = MarketCrew(
        news_provider=news_provider,
        market_data_provider=market_data_provider,
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
        print(report.model_dump_json(indent=2))
    else:
        print(_format_report(report))
    return 0


def _configure_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def main(argv: list[str] | None = None) -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except MarketAIAgentsError as exc:
        logger.error("%s", exc)
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001 - top-level guard so the CLI always exits cleanly
        logger.exception("Unexpected error")
        print(f"error: unexpected failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
