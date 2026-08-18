"""StrategistAgent — the single decision-making LLM agent."""

from __future__ import annotations

import json
from typing import Any

from src.models.enums import Action
from src.models.llm import INJECTION_GUARD, _extract_json
from src.models.strategy import StrategyRecommendation
from src.utils.i18n import strategy_language_directive
from src.utils.logging import get_logger

logger = get_logger()

SYSTEM_PROMPT = (
    "Eres un analista de inversión sénior. Tu labor es unificar el resumen de noticias y "
    "el análisis técnico para emitir una recomendación estratégica de compra, venta o "
    "mantenimiento—debes evitar frases hechas y ser asertivo."
)

STRATEGY_RULES = (
    " Usa únicamente la información proporcionada. No inventes datos ni cifras. Emite "
    "exactamente una acción entre BUY, HOLD o SELL. La confianza (confidence) debe ser un "
    "número entre 0 y 1. Identifica factores alcistas (bullish_factors), factores bajistas "
    "(bearish_factors), riesgos (risk_factors) y condiciones que invalidarían la tesis "
    "(invalidating_conditions). Si la evidencia es contradictoria o insuficiente, elige HOLD. "
    + INJECTION_GUARD
)


def strategy_system_prompt() -> str:
    """The complete strategist system prompt (exact persona phrase plus rules)."""
    return SYSTEM_PROMPT + STRATEGY_RULES


def build_strategist_agent(llm=None):
    """Build the senior strategist CrewAI ``Agent``."""
    from crewai import Agent

    return Agent(
        role="Senior Investment Strategist",
        goal=(
            "Unify the news summary and the technical analysis into a single, assertive "
            "BUY, HOLD, or SELL decision."
        ),
        backstory=strategy_system_prompt(),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def build_strategy_prompt(
    ticker: str, news_analysis, technical_analysis, language: str = "en", depth: str = "standard"
) -> str:
    """Render the deterministic inputs into the strategist's user prompt."""
    news = news_analysis.model_dump(mode="json") if news_analysis is not None else {}
    tech = technical_analysis.model_dump(mode="json") if technical_analysis is not None else {}
    deep_directive = ""
    if depth == "deep":
        deep_directive = (
            "\n\nANÁLISIS PROFUNDO: realiza un análisis exhaustivo y de mayor calado. "
            "Amplía los factores alcistas y bajistas, los riesgos y las condiciones de "
            "invalidación con mayor granularidad. Desarrolla la tesis en profundidad y "
            "evita respuestas superficiales o genéricas."
        )
    return (
        f"Ticker: {ticker}\n\n"
        "Analiza la siguiente información y devuelve ÚNICAMENTE un objeto JSON con las claves: "
        "action, confidence, summary, bullish_factors, bearish_factors, risk_factors, "
        "invalidating_conditions.\n\n"
        f"Análisis de noticias (JSON):\n{json.dumps(news, ensure_ascii=False)}\n\n"
        f"Análisis técnico (JSON):\n{json.dumps(tech, ensure_ascii=False)}\n"
        f"{deep_directive}\n"
        f"{strategy_language_directive(language)}\n"
    )


def fallback_recommendation(ticker: str, reason: str = "") -> StrategyRecommendation:
    """A safe HOLD recommendation used whenever the LLM cannot produce a signal."""
    return StrategyRecommendation(
        ticker=ticker,
        action=Action.HOLD,
        confidence=0.0,
        summary=f"Falling back to HOLD with low confidence. {reason}".strip(),
        bullish_factors=[],
        bearish_factors=[],
        risk_factors=["Insufficient or unavailable data to produce a confident signal."],
        invalidating_conditions=[],
    )


def coerce_recommendation(data: Any, ticker: str) -> StrategyRecommendation:
    """Validate an LLM result into a ``StrategyRecommendation``, falling back to HOLD."""
    if isinstance(data, StrategyRecommendation):
        return data
    if isinstance(data, str):
        try:
            data = _extract_json(data)
        except Exception as exc:
            logger.warning("Could not parse strategy JSON: %s", exc)
            return fallback_recommendation(ticker)
    if isinstance(data, dict):
        try:
            payload = dict(data)
            action = str(payload.get("action", "HOLD")).upper()
            if action not in {a.value for a in Action}:
                action = Action.HOLD.value
            payload["action"] = action
            try:
                confidence = float(payload.get("confidence", 0.0))
            except (TypeError, ValueError):
                confidence = 0.0
            payload["confidence"] = max(0.0, min(1.0, confidence))
            payload["ticker"] = ticker
            for field in (
                "bullish_factors",
                "bearish_factors",
                "risk_factors",
                "invalidating_conditions",
            ):
                value = payload.get(field, [])
                if not isinstance(value, list):
                    value = [value] if value else []
                payload[field] = [str(v) for v in value]
            payload.setdefault("summary", str(payload.get("summary", "")))
            return StrategyRecommendation.model_validate(payload)
        except Exception as exc:
            logger.warning("Could not coerce strategy payload: %s", exc)
            return fallback_recommendation(ticker)
    return fallback_recommendation(ticker)
