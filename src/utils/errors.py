"""Domain-specific exception hierarchy."""


class MarketAIAgentsError(Exception):
    """Base class for all project-specific errors."""


class ConfigurationError(MarketAIAgentsError):
    """Raised when configuration is missing or invalid."""


class InvalidTickerError(MarketAIAgentsError):
    """Raised when a ticker symbol is missing or malformed."""


class MarketDataError(MarketAIAgentsError):
    """Raised when market data cannot be fetched or is invalid/empty."""


class NewsError(MarketAIAgentsError):
    """Raised when news cannot be fetched or no items are found."""


class LLMError(MarketAIAgentsError):
    """Raised when the LLM request fails or returns unparseable output."""


class InsufficientDataError(MarketAIAgentsError):
    """Raised when there is not enough data to produce a confident signal."""
