"""TechnicalAnalysisAgent — CrewAI agent that interprets pre-computed indicators."""

from __future__ import annotations

from src.models.llm import INJECTION_GUARD
from src.tools.protocols import MarketDataProvider


def build_technical_agent(
    market_data_provider: MarketDataProvider, llm=None, period: str = "1y", interval: str = "1d"
):
    """Build a CrewAI ``Agent`` that interprets already-computed indicators."""
    from crewai import Agent
    from crewai.tools.base_tool import Tool

    def _compute_technical(ticker: str) -> str:
        from src.utils.indicators import build_technical_analysis

        data = market_data_provider.get_market_data(ticker, period, interval)
        return build_technical_analysis(data).model_dump_json()

    technical_tool = Tool(
        name="compute_technical_indicators",
        description=(
            "Compute and return technical indicators (SMA, EMA, RSI, MACD, ATR, volatility, "
            "52-week range, volume ratio) for a ticker as JSON."
        ),
        func=_compute_technical,
    )

    return Agent(
        role="Technical Analysis Interpreter",
        goal=(
            "Interpret already-computed technical indicators to assess trend, momentum, and "
            "volatility for a ticker."
        ),
        backstory=(
            "You are a technical analyst. You interpret indicator values (SMA, EMA, RSI, MACD, "
            "ATR, volatility, 52-week range, volume ratio) that have already been computed by "
            "Python. You do NOT recompute them and you do not invent values. " + INJECTION_GUARD
        ),
        tools=[technical_tool],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
