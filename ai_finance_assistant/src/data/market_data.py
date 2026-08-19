from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float
    change_percent: float
    as_of: str


class MarketDataProvider(Protocol):
    """Abstraction for live or cached market quote providers."""

    def quote(self, symbol: str) -> Quote | None:
        """Return a quote for a symbol, or None when data is unavailable."""


class InMemoryMarketDataProvider:
    """Deterministic quote provider for local development and tests."""

    def __init__(self, quotes: dict[str, Quote] | None = None) -> None:
        self._quotes = {
            key.upper(): value for key, value in (quotes or self.sample_quotes()).items()
        }

    @staticmethod
    def sample_quotes() -> dict[str, Quote]:
        return {
            "VOO": Quote("VOO", 510.25, 0.42, "sample close"),
            "BND": Quote("BND", 72.10, -0.08, "sample close"),
            "AAPL": Quote("AAPL", 225.00, 1.15, "sample close"),
        }

    def quote(self, symbol: str) -> Quote | None:
        if not symbol or not symbol.strip():
            return None
        return self._quotes.get(symbol.upper())
