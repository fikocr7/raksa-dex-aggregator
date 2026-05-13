"""Aggregator base class and shared context."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

import httpx

from ..models import BuyLeg, Quote, SellLeg


@dataclass(slots=True, frozen=True)
class QuoteContext:
    """Normalized context passed to every aggregator adapter."""
    chain: str          # slug
    chain_id: int
    sell: SellLeg
    buy: BuyLeg
    slippage_pct: float  # 0-50
    client: httpx.AsyncClient  # shared httpx session


class Aggregator(ABC):
    """Each aggregator adapter implements ``get_quote``."""

    name: str = "unknown"
    #: chains this aggregator supports (subset of chains.CHAIN_IDS)
    supported_chains: frozenset[str] = frozenset()
    #: seconds before we give up waiting
    timeout: float = 8.0

    def supports(self, chain: str) -> bool:
        return chain in self.supported_chains

    @abstractmethod
    async def get_quote(self, ctx: QuoteContext) -> Quote:
        """Return a ``Quote`` or raise."""
        raise NotImplementedError

    # Convenience helpers available to subclasses

    @staticmethod
    def _format_amount(raw: str | int, decimals: int) -> str:
        """Convert wei integer to human decimal string with the token's decimals."""
        raw_int = int(raw)
        if decimals == 0:
            return str(raw_int)
        q = Decimal(raw_int) / (Decimal(10) ** decimals)
        # Keep up to 18 significant digits, strip trailing zeros
        return format(q.normalize(), "f")
