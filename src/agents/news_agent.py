"""MarketNewsAgent — CrewAI agent that gathers and classifies market news."""

from __future__ import annotations

from src.models.llm import INJECTION_GUARD
from src.tools.protocols import NewsProvider


def build_news_agent(news_provider: NewsProvider, llm=None, news_limit: int = 10):
    """Build a CrewAI ``Agent`` backed by a ``NewsProvider``."""
    from crewai import Agent
    from crewai.tools.base_tool import Tool

    def _search_news(ticker: str) -> str:
        from src.utils.sentiment import build_news_analysis

        items = news_provider.search(ticker, news_limit)
        return build_news_analysis(ticker.upper(), items).model_dump_json()

    news_tool = Tool(
        name="search_market_news",
        description=(
            "Search recent news for a ticker symbol and return the sentiment-classified "
            "analysis (BULLISH/NEUTRAL/BEARISH) as JSON."
        ),
        func=_search_news,
    )

    return Agent(
        role="Market News Analyst",
        goal=(
            "Retrieve the latest news for a ticker and classify the overall sentiment as "
            "BULLISH, NEUTRAL, or BEARISH without inventing any headline."
        ),
        backstory=(
            "You are a meticulous news analyst. You only report articles that were actually "
            "retrieved through your search tool, preserving title, source, publication date, "
            "and snippet. " + INJECTION_GUARD
        ),
        tools=[news_tool],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
