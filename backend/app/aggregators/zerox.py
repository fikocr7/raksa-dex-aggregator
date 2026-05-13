"""0x Swap API v2 adapter.

Docs: https://0x.org/docs/api
Requires `ZEROX_API_KEY` env var. Free tier available.
Falls back gracefully if key missing (raises informative error).
"""
from __future__ import annotations

import os

import httpx

from ..models import Quote
from .base import Aggregator, QuoteContext

_CHAIN_TO_ZEROX_BASE: dict[str, str] = {
    "ethereum": "https://api.0x.org",
    "arbitrum": "https://arbitrum.api.0x.org",
    "optimism": "https://optimism.api.0x.org",
    "base":     "https://base.api.0x.org",
    "polygon":  "https://polygon.api.0x.org",
    "bsc":      "https://bsc.api.0x.org",
}


class ZeroX(Aggregator):
    name = "0x"
    supported_chains = frozenset(_CHAIN_TO_ZEROX_BASE)

    @property
    def api_key(self) -> str | None:
        return os.getenv("ZEROX_API_KEY") or None

    async def get_quote(self, ctx: QuoteContext) -> Quote:
        key = self.api_key
        if not key:
            raise RuntimeError("ZEROX_API_KEY env var not set — skipping 0x")

        base = _CHAIN_TO_ZEROX_BASE[ctx.chain]
        params = {
            "sellToken": ctx.sell.address,
            "buyToken": ctx.buy.address,
            "sellAmount": ctx.sell.amount_raw,
            "slippageBps": int(ctx.slippage_pct * 100),
        }
        headers = {"0x-api-key": key, "0x-version": "v2"}
        r = await ctx.client.get(
            f"{base}/swap/permit2/price",
            params=params,
            headers=headers,
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        buy_amount = data.get("buyAmount")
        if not buy_amount:
            raise RuntimeError(f"no buyAmount in response: {data}")

        gas = None
        g = data.get("gas")
        if g:
            try:
                gas = int(g)
            except (TypeError, ValueError):
                gas = None

        # route summary from fills
        route_names: list[str] = []
        for fill in (data.get("route") or {}).get("fills", [])[:3]:
            src = fill.get("source")
            if src and src not in route_names:
                route_names.append(src)
        summary = " + ".join(route_names) if route_names else None

        return Quote(
            source=self.name,
            amount_out=self._format_amount(buy_amount, ctx.buy.decimals),
            amount_out_raw=str(buy_amount),
            gas=gas,
            route_summary=summary,
        )
