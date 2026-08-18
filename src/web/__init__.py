"""Web layer for ``market-ai-agents`` (FastAPI backend + static frontend)."""

from src.web.catalog import get_catalog, is_known_symbol

__all__ = ["get_catalog", "is_known_symbol"]
