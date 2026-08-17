"""Unit tests for agent builders and strategist helpers."""

from __future__ import annotations

from src.agents import news_agent, strategist_agent, technical_agent
from src.models.enums import Action
from src.models.llm import INJECTION_GUARD
from src.models.strategy import StrategyRecommendation


def test_system_prompt_contains_persona_and_guard():
    prompt = strategist_agent.strategy_system_prompt()
    assert "analista de inversión sénior" in prompt
    assert "evitar frases hechas" in prompt
    assert INJECTION_GUARD in prompt


def test_fallback_recommendation_is_hold_low_confidence():
    rec = strategist_agent.fallback_recommendation("NVDA")
    assert rec.action is Action.HOLD
    assert rec.confidence == 0.0
    assert rec.ticker == "NVDA"


def test_coerce_recommendation_from_dict():
    data = {
        "action": "BUY",
        "confidence": 0.8,
        "summary": "Strong momentum.",
        "bullish_factors": ["momentum"],
        "bearish_factors": [],
        "risk_factors": ["volatility"],
        "invalidating_conditions": [],
    }
    rec = strategist_agent.coerce_recommendation(data, "NVDA")
    assert rec.action is Action.BUY
    assert rec.confidence == 0.8
    assert rec.ticker == "NVDA"


def test_coerce_recommendation_clamps_confidence():
    rec = strategist_agent.coerce_recommendation({"action": "SELL", "confidence": 2.0}, "NVDA")
    assert rec.confidence == 1.0


def test_coerce_recommendation_invalid_action_falls_back_to_hold():
    rec = strategist_agent.coerce_recommendation({"action": "MOON", "confidence": 0.5}, "NVDA")
    assert rec.action is Action.HOLD


def test_coerce_recommendation_garbage_returns_fallback():
    rec = strategist_agent.coerce_recommendation("not json at all", "NVDA")
    assert rec.action is Action.HOLD
    assert rec.confidence == 0.0


def test_coerce_recommendation_passthrough():
    existing = StrategyRecommendation(ticker="NVDA", action=Action.SELL, confidence=0.7)
    assert strategist_agent.coerce_recommendation(existing, "NVDA") is existing


def test_build_strategy_prompt_includes_ticker():
    prompt = strategist_agent.build_strategy_prompt("NVDA", None, None)
    assert "NVDA" in prompt


def test_build_news_agent(mock_news_provider):
    agent = news_agent.build_news_agent(mock_news_provider, llm=None, news_limit=5)
    assert agent.role == "Market News Analyst"
    assert len(agent.tools) == 1


def test_build_technical_agent(mock_market_provider):
    agent = technical_agent.build_technical_agent(mock_market_provider, llm=None)
    assert agent.role == "Technical Analysis Interpreter"
    assert len(agent.tools) == 1


def test_build_strategist_agent():
    agent = strategist_agent.build_strategist_agent(llm=None)
    assert agent.role == "Senior Investment Strategist"
