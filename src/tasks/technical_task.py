"""TechnicalTask builder."""

from __future__ import annotations


def build_technical_task(agent, ticker: str, technical_analysis):
    """Build the CrewAI technical-interpretation ``Task``."""
    from crewai import Task

    context = (
        technical_analysis.model_dump_json()
        if technical_analysis is not None
        else "No technical data available."
    )
    return Task(
        description=(
            f"Interpret the following pre-computed technical indicators for {ticker}. Do not "
            f"recompute them. State the trend, momentum, and volatility.\n\n"
            f"Technical analysis (JSON):\n{context}"
        ),
        expected_output="A short technical read summarizing trend, momentum, and volatility.",
        agent=agent,
    )
