"""Aggregator registry."""
from __future__ import annotations

from .base import Aggregator, QuoteContext
from .kyberswap import KyberSwap
from .oneinch import OneInch
from .openocean import OpenOcean
from .paraswap import Paraswap
from .zerox import ZeroX


def get_all_aggregators() -> list[Aggregator]:
    """Return a fresh list of every aggregator adapter."""
    return [
        OneInch(),
        Paraswap(),
        ZeroX(),
        OpenOcean(),
        KyberSwap(),
    ]


__all__ = [
    "Aggregator",
    "QuoteContext",
    "OneInch",
    "Paraswap",
    "ZeroX",
    "OpenOcean",
    "KyberSwap",
    "get_all_aggregators",
]
