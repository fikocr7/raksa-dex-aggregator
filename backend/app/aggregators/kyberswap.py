"""KyberSwap Aggregator v1 API adapter.

Docs: https://docs.kyberswap.com/kyberswap-solutions/kyberswap-aggregator/aggregator-api-specification/evm-swaps
No auth required.
"""
from __future__ import annotations

import httpx

from ..models import Quote
from .base import Aggregator, QuoteContext

_CHAIN_SLUG_KYBER: dict[str, str] = {
    "ethereum": "ethereum",
    "arbitrum": "arbitrum",
    "optimism": "optimism",
    "base":     "base",
    "polygon":  "polygon",
    "bsc":      "bsc",
}


class KyberSwap(Aggregator):
    name = "kyberswap"
    supported_chains = frozenset(_CHAIN_SLUG_KYBER)

    BASE = "https://aggregator-api.kyberswap.com"

    async def get_quote(self, ctx: QuoteContext) -> Quote:
        slug = _CHAIN_SLUG_KYBER[ctx.chain]
        url = f"{self.BASE}/{slug}/api/v1/routes"
        params = {
            "tokenIn": ctx.sell.address,
            "tokenOut": ctx.buy.address,
            "amountIn": ctx.sell.amount_raw,
            "gasInclude": "true",
        }
        headers = {
            "x-client-id": "raksa-dex-aggregator",
            "Accept": "application/json",
        }
        r = await ctx.client.get(url, params=params, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()

        if data.get("code") != 0:
            raise RuntimeError(f"kyber error: {data.get('message') or data}")

        payload = data.get("data") or {}
        route = payload.get("routeSummary") or {}
        amount_out = route.get("amountOut")
        if not amount_out:
            raise RuntimeError(f"no amountOut: {payload}")

        gas = None
        g = route.get("gas")
        if g:
            try:
                gas = int(g)
            except (TypeError, ValueError):
                gas = None

        # gasPrice comes in wei as a string
        gas_price_gwei = None
        gp = route.get("gasPrice")
        if gp:
            try:
                gas_price_gwei = int(gp) / 1e9
            except (TypeError, ValueError):
                gas_price_gwei = None

        # route summary: list of pool labels from first leg
        route_names: list[str] = []
        legs = route.get("route") or []
        for hop in legs[:1]:
            for step in (hop or [])[:3]:
                ex = step.get("exchange")
                if ex and ex not in route_names:
                    route_names.append(ex)
        summary = " + ".join(route_names) if route_names else None

        return Quote(
            source=self.name,
            amount_out=self._format_amount(amount_out, ctx.buy.decimals),
            amount_out_raw=str(amount_out),
            gas=gas,
            gas_price_gwei=gas_price_gwei,
            route_summary=summary,
        )
