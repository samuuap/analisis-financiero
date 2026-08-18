"""Run the web app: ``python -m src.web`` or the ``market-ai-agents-web`` script."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.getenv("MARKET_WEB_HOST", "127.0.0.1")
    port = int(os.getenv("MARKET_WEB_PORT", "8000"))
    reload = os.getenv("MARKET_WEB_RELOAD", "").lower() in {"1", "true", "yes"}
    uvicorn.run("src.web.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
