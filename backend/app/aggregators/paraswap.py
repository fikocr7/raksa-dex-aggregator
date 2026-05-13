"""Paraswap v6.2 API adapter.

Docs: https://developers.paraswap.network/api/get-rate-for-a-token-pair
No auth key required for public quoting.
"""
from __future__ import annotations

import httpx

from ..models import Quote
from .base import Aggregator, QuoteContext

_CHAIN_TO_PARASWAP: dict[str, int] = {
    "ethereum": 1,
    "arbitrum": 42161,
    "optimism": 10,
    "base": 8453,
    "polygon": 137,
    "bsc": 56,
}


class Paraswap(Aggregator):
    name = "paraswap"
    supported_chains = frozenset(_CHAIN_TO_PARASWAP)

    API = "https://apiv5.paraswap.io/prices"

    async def get_quote(self, ctx: QuoteContext) -> Quote:
        params = {
            "srcToken": ctx.sell.address,
            "destToken": ctx.buy.address,
            "srcDecimals": ctx.sell.decimals,
            "destDecimals": ctx.buy.decimals,
            "amount": ctx.sell.amount_raw,
            "network": _CHAIN_TO_PARASWAP[ctx.chain],
            "side": "SELL",
            "version": "6.2",
        }
        r = await ctx.client.get(self.API, params=params, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        route = data.get("priceRoute") or {}
        dest_amount = route.get("destAmount")
        if not dest_amount:
            raise RuntimeError(f"no priceRoute: {data}")

        # summarize route: e.g. "UniswapV3 → Curve"
        route_names: list[str] = []
        for swap in route.get("bestRoute", [])[:1]:
            for path in swap.get("swaps", [])[:1]:
                for exchange in path.get("swapExchanges", [])[:2]:
                    ex = exchange.get("exchange")
                    if ex and ex not in route_names:
                        route_names.append(ex)
        summary = " + ".join(route_names) if route_names else None

        gas = None
        gas_cost = route.get("gasCost")
        if gas_cost:
            try:
                gas = int(gas_cost)
            except (TypeError, ValueError):
                gas = None

        return Quote(
            source=self.name,
            amount_out=self._format_amount(dest_amount, ctx.buy.decimals),
            amount_out_raw=str(dest_amount),
            gas=gas,
            route_summary=summary,
            raw=None,  # set to `data` for debug, but heavy
        )
