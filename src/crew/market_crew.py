"""MarketCrew — orchestrates the three agents into a sequential crew."""

from __future__ import annotations

from datetime import UTC, datetime

from src.agents.news_agent import build_news_agent
from src.agents.strategist_agent import (
    build_strategist_agent,
    build_strategy_prompt,
    coerce_recommendation,
    fallback_recommendation,
    strategy_system_prompt,
)
from src.agents.technical_agent import build_technical_agent
from src.config.settings import Settings
from src.models.llm import MockLLM, build_crewai_llm
from src.models.strategy import MarketReport, StrategyRecommendation
from src.tasks.news_task import build_news_task
from src.tasks.strategy_task import build_strategy_task
from src.tasks.technical_task import build_technical_task
from src.tools.market_data import validate_ticker
from src.tools.protocols import MarketDataProvider, NewsProvider
from src.utils.errors import ConfigurationError
from src.utils.indicators import build_technical_analysis
from src.utils.logging import get_logger, new_execution_id
from src.utils.sentiment import build_news_analysis

logger = get_logger()


class MarketCrew:
    """Runs the three-agent pipeline and returns a ``MarketReport``.

    The deterministic stages (news search and indicator computation) always run in
    Python and are the source of truth for the report. Only the strategist decision
    is delegated to the LLM (real mode) or a ``MockLLM`` (mock mode).
    """

    def __init__(self, news_provider: NewsProvider, market_data_provider: MarketDataProvider,
                 settings: Settings | None = None) -> None:
        self._news_provider = news_provider
        self._market_data_provider = market_data_provider
        self._settings = settings or Settings.from_env()

    def run(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
        news_limit: int = 10,
        mock: bool = False,
    ) -> MarketReport:
        symbol = validate_ticker(ticker)
        execution_id = new_execution_id()
        timestamp = datetime.now(UTC)
        model = (
            self._settings.deepseek_model
            if not mock
            else f"{self._settings.deepseek_model} (mock)"
        )

        if not mock and not self._settings.has_deepseek_key:
            raise ConfigurationError(
                "DEEPSEEK_API_KEY is not set. Set it in the environment or .env, "
                "or run with --mock."
            )

        news_analysis, news_search_timestamp = self._gather_news(symbol, news_limit)
        market_data = self._gather_market(symbol, period, interval)
        technical_analysis = build_technical_analysis(market_data) if market_data else None

        if mock:
            recommendation = self._recommend_mock(symbol, news_analysis, technical_analysis)
        else:
            recommendation = self._recommend_real(
                symbol, news_analysis, technical_analysis, period, interval, news_limit
            )

        if technical_analysis is not None:
            recommendation.technical_signal = technical_analysis.signal
        if news_analysis is not None:
            recommendation.news_signal = news_analysis.sentiment

        return MarketReport(
            execution_id=execution_id,
            ticker=symbol,
            timestamp=timestamp,
            model=model,
            market_data_timestamp=market_data.market_data_timestamp if market_data else None,
            news_search_timestamp=news_search_timestamp,
            price=market_data.price if market_data else None,
            high_52w=technical_analysis.high_52w if technical_analysis else None,
            low_52w=technical_analysis.low_52w if technical_analysis else None,
            news_analysis=news_analysis,
            technical_analysis=technical_analysis,
            recommendation=recommendation,
            sources=news_analysis.sources if news_analysis else [],
        )

    def build_crew(self, ticker: str, period: str, interval: str, news_limit: int, llm,
                   news_analysis=None, technical_analysis=None):
        """Build (but do not run) the sequential CrewAI crew for inspection/testing."""
        from crewai import Crew, Process

        symbol = validate_ticker(ticker)
        news_agent = build_news_agent(self._news_provider, llm, news_limit)
        technical_agent = build_technical_agent(self._market_data_provider, llm, period, interval)
        strategist_agent = build_strategist_agent(llm)
        tasks = [
            build_news_task(news_agent, symbol, news_analysis),
            build_technical_task(technical_agent, symbol, technical_analysis),
            build_strategy_task(strategist_agent, symbol, news_analysis, technical_analysis),
        ]
        return Crew(
            agents=[news_agent, technical_agent, strategist_agent],
            tasks=tasks,
            process=Process.sequential,
            verbose=False,
        )

    def _gather_news(self, symbol: str, news_limit: int):
        try:
            items = self._news_provider.search(symbol, news_limit)
            return build_news_analysis(symbol, items), datetime.now(UTC)
        except Exception as exc:
            logger.warning("News unavailable for %s: %s", symbol, exc)
            return None, datetime.now(UTC)

    def _gather_market(self, symbol: str, period: str, interval: str):
        try:
            return self._market_data_provider.get_market_data(symbol, period, interval)
        except Exception as exc:
            logger.warning("Market data unavailable for %s: %s", symbol, exc)
            return None

    def _recommend_mock(self, symbol: str, news_analysis, technical_analysis):
        prompt = build_strategy_prompt(symbol, news_analysis, technical_analysis)
        data = MockLLM().complete_json(strategy_system_prompt(), prompt)
        return coerce_recommendation(data, symbol)

    def _recommend_real(self, symbol: str, news_analysis, technical_analysis,
                        period: str, interval: str, news_limit: int):
        try:
            llm = build_crewai_llm(self._settings)
        except Exception as exc:
            logger.warning("Could not build CrewAI LLM: %s", exc)
            return fallback_recommendation(symbol)
        try:
            crew = self.build_crew(
                symbol, period, interval, news_limit, llm, news_analysis, technical_analysis
            )
            result = crew.kickoff()
            return self._extract_recommendation(result, symbol)
        except Exception as exc:
            logger.warning("Crew execution failed for %s: %s", symbol, exc)
            return fallback_recommendation(symbol)

    @staticmethod
    def _extract_recommendation(result, symbol: str) -> StrategyRecommendation:
        data = None
        try:
            data = result.pydantic
        except Exception:
            data = None
        if data is None:
            for task_output in getattr(result, "tasks_output", []) or []:
                try:
                    candidate = task_output.pydantic
                    if candidate is not None:
                        data = candidate
                        break
                except Exception:
                    continue
        if data is None:
            try:
                data = result.raw
            except Exception:
                data = None
        return coerce_recommendation(data, symbol)
