"""StrategyTask builder."""

from __future__ import annotations


def build_strategy_task(agent, ticker: str, news_analysis, technical_analysis):
    """Build the CrewAI strategist ``Task`` with a structured ``StrategyRecommendation`` output."""
    from crewai import Task

    from src.agents.strategist_agent import build_strategy_prompt
    from src.models.strategy import StrategyRecommendation

    return Task(
        description=build_strategy_prompt(ticker, news_analysis, technical_analysis),
        expected_output="A JSON object with action, confidence, summary, and factor lists.",
        agent=agent,
        output_pydantic=StrategyRecommendation,
    )
