"""Logging setup and execution-id generation."""

from __future__ import annotations

import logging
import uuid

_LOGGER_NAME = "market-ai-agents"


def new_execution_id() -> str:
    """Return a unique traceability id for one analysis run."""
    return uuid.uuid4().hex


def get_logger(name: str = _LOGGER_NAME) -> logging.Logger:
    """Return a configured logger, attaching a handler only once."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
