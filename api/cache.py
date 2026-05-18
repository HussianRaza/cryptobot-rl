"""Simple in-memory cache for backtest results.

Backtests are deterministic — no invalidation needed.
Key: (endpoint, asset, agent)
"""
from typing import Any

_store: dict[tuple, Any] = {}


def get(key: tuple) -> Any | None:
    return _store.get(key)


def set(key: tuple, value: Any) -> None:
    _store[key] = value


def clear() -> None:
    _store.clear()
