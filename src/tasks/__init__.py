"""CrewAI task builders."""

from src.tasks.news_task import build_news_task
from src.tasks.strategy_task import build_strategy_task
from src.tasks.technical_task import build_technical_task

__all__ = [
    "build_news_task",
    "build_technical_task",
    "build_strategy_task",
]
