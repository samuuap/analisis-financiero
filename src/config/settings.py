"""Application configuration loaded from the environment."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic import BaseModel


class Settings(BaseModel):
    """Runtime settings.

    All DeepSeek values are read from environment variables and never
    hardcoded. The model must remain switchable between the flash and pro
    variants via ``DEEPSEEK_MODEL``.
    """

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_base_url: str = "https://api.deepseek.com"
    news_ttl_seconds: int = 900
    request_timeout_seconds: int = 30

    @classmethod
    def from_env(cls) -> Settings:
        """Load a Settings instance from process environment / ``.env``."""
        load_dotenv()
        return cls(
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            news_ttl_seconds=int(os.getenv("NEWS_TTL_SECONDS", "900")),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
        )

    @property
    def has_deepseek_key(self) -> bool:
        return bool(self.deepseek_api_key.strip())
