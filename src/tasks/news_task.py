"""NewsTask builder."""

from __future__ import annotations


def build_news_task(agent, ticker: str, news_analysis):
    """Build the CrewAI news-summarization ``Task``."""
    from crewai import Task

    context = (
        news_analysis.model_dump_json() if news_analysis is not None else "No news available."
    )
    return Task(
        description=(
            f"Summarize the following news analysis for {ticker} and state whether the "
            f"overall sentiment is BULLISH, NEUTRAL, or BEARISH. Do not invent headlines.\n\n"
            f"News analysis (JSON):\n{context}"
        ),
        expected_output="A short news summary with the overall sentiment classification.",
        agent=agent,
    )
