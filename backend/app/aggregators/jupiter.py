"""Jupiter aggregator (Solana).

Docs: https://station.jup.ag/docs/apis/swap-api
Public quote endpoint, no auth required.
"""
from __future__ import annotations

import httpx

from ..models import Quote
from .base import Aggregator, QuoteContext


class Jupiter(Aggregator):
    name = "jupiter"
    # Solana-only; non-EVM
    supported_chains = frozenset({"solana"})

    BASE = "https://lite-api.jup.ag/swap/v1"

    async def get_quote(self, ctx: QuoteContext) -> Quote:
        # Jupiter expects mint addresses (base58) as inputMint/outputMint
        params = {
            "inputMint":  ctx.sell.address,
            "outputMint": ctx.buy.address,
            "amount":     ctx.sell.amount_raw,
            "slippageBps": str(int(ctx.slippage_pct * 100)),
            "swapMode":   "ExactIn",
            "onlyDirectRoutes": "false",
        }
        r = await ctx.client.get(
            f"{self.BASE}/quote",
            params=params,
            timeout=self.timeout,
            headers={"Accept": "application/json"},
        )
        r.raise_for_status()
        data = r.json()

        if "error" in data:
            raise RuntimeError(f"jupiter error: {data['error']}")

        amount_out = data.get("outAmount")
        if not amount_out:
            raise RuntimeError(f"jupiter: no outAmount {data}")

        # Price impact (Jupiter returns as decimal e.g. "0.0012" = 0.12%)
        price_impact = None
        pi = data.get("priceImpactPct")
        if pi is not None:
            try:
                price_impact = float(pi) * 100
            except (TypeError, ValueError):
                price_impact = None

        # Route summary: list of unique AMM labels
        route_names: list[str] = []
        for plan in (data.get("routePlan") or [])[:3]:
            info = plan.get("swapInfo") or {}
            label = info.get("label")
            if label and label not in route_names:
                route_names.append(label)
        summary = " → ".join(route_names) if route_names else None

        return Quote(
            source=self.name,
            amount_out=self._format_amount(amount_out, ctx.buy.decimals),
            amount_out_raw=str(amount_out),
            price_impact_pct=price_impact,
            route_summary=summary,
        )
