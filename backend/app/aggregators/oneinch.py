"""1inch v6 API adapter.

Docs: https://portal.1inch.dev/documentation/apis/swap/classic-swap/introduction
Requires `ONEINCH_API_KEY` env var. Free tier available.
"""
from __future__ import annotations

import os

import httpx

from ..models import Quote
from .base import Aggregator, QuoteContext

_CHAIN_TO_1INCH: dict[str, int] = {
    "ethereum": 1,
    "arbitrum": 42161,
    "optimism": 10,
    "base": 8453,
    "polygon": 137,
    "bsc": 56,
}


class OneInch(Aggregator):
    name = "1inch"
    supported_chains = frozenset(_CHAIN_TO_1INCH)

    BASE = "https://api.1inch.dev/swap/v6.0"

    @property
    def api_key(self) -> str | None:
        return os.getenv("ONEINCH_API_KEY") or None

    async def get_quote(self, ctx: QuoteContext) -> Quote:
        key = self.api_key
        if not key:
            raise RuntimeError("ONEINCH_API_KEY env var not set — skipping 1inch")

        chain_id = _CHAIN_TO_1INCH[ctx.chain]
        url = f"{self.BASE}/{chain_id}/quote"
        params = {
            "src": ctx.sell.address,
            "dst": ctx.buy.address,
            "amount": ctx.sell.amount_raw,
            "includeGas": "true",
            "includeProtocols": "true",
        }
        headers = {
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        }
        r = await ctx.client.get(url, params=params, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()

        dst_amount = data.get("dstAmount") or data.get("toAmount")
        if not dst_amount:
            raise RuntimeError(f"no dstAmount: {data}")

        gas = None
        g = data.get("gas")
        if g:
            try:
                gas = int(g)
            except (TypeError, ValueError):
                gas = None

        # protocol path summary
        route_names: list[str] = []
        protocols = data.get("protocols") or []
        if protocols and isinstance(protocols[0], list):
            for leg in protocols[0][:1]:
                for step in leg[:3]:
                    nm = step.get("name")
                    if nm and nm not in route_names:
                        route_names.append(nm)
        summary = " + ".join(route_names) if route_names else None

        return Quote(
            source=self.name,
            amount_out=self._format_amount(dst_amount, ctx.buy.decimals),
            amount_out_raw=str(dst_amount),
            gas=gas,
            route_summary=summary,
        )
