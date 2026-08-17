"""A tiny time-to-live cache for news searches."""

from __future__ import annotations

import time
from typing import Any


class TTLCache:
    """In-memory cache that expires entries after ``ttl_seconds``."""

    def __init__(self, ttl_seconds: int) -> None:
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds must be non-negative")
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        timestamp, value = entry
        if time.time() - timestamp > self._ttl:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time(), value)

    def purge(self) -> None:
        now = time.time()
        expired = [k for k, (ts, _) in self._store.items() if now - ts > self._ttl]
        for key in expired:
            self._store.pop(key, None)

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None
