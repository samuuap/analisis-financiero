"""StrategyTask builder."""

from __future__ import annotations


def build_strategy_task(
    agent, ticker: str, news_analysis, technical_analysis, language: str = "en",
    depth: str = "standard",
):
    """Build the CrewAI strategist ``Task`` (emits plain JSON text, no structured output).

    ``output_pydantic`` is intentionally omitted: DeepSeek does not implement OpenAI's
    ``beta.chat.completions.parse`` structured-outputs API, so a Pydantic output would make
    CrewAI send an unsupported ``response_format`` and fail with HTTP 400. The strategist's
    JSON text is parsed downstream by ``coerce_recommendation`` instead.
    """
    from crewai import Task

    from src.agents.strategist_agent import build_strategy_prompt

    return Task(
        description=build_strategy_prompt(
            ticker, news_analysis, technical_analysis, language, depth
        ),
        expected_output=(
            "A single JSON object with the keys action, confidence, summary, bullish_factors, "
            "bearish_factors, risk_factors, and invalidating_conditions. Do not add prose."
        ),
        agent=agent,
    )
