"""OpenOcean v3 API adapter.

Docs: https://docs.openocean.finance/dev/openocean-api-3.0
No auth required for quoting.
"""
from __future__ import annotations

import httpx

from ..models import Quote
from .base import Aggregator, QuoteContext

_CHAIN_SLUG_OPENOCEAN: dict[str, str] = {
    "ethereum": "eth",
    "arbitrum": "arbitrum",
    "optimism": "optimism",
    "base":     "base",
    "polygon":  "polygon",
    "bsc":      "bsc",
}


class OpenOcean(Aggregator):
    name = "openocean"
    supported_chains = frozenset(_CHAIN_SLUG_OPENOCEAN)

    BASE = "https://open-api.openocean.finance/v3"

    async def get_quote(self, ctx: QuoteContext) -> Quote:
        slug = _CHAIN_SLUG_OPENOCEAN[ctx.chain]
        url = f"{self.BASE}/{slug}/quote"
        # OpenOcean expects human-readable `amount` (not wei) + decimals via `inTokenAddress`
        # Docs: amount should be in token units (e.g. "1.5" ETH, not wei).
        params = {
            "inTokenAddress": ctx.sell.address,
            "outTokenAddress": ctx.buy.address,
            "amount": ctx.sell.amount,  # human-readable
            "gasPrice": 1,  # dummy, required by API
            "slippage": ctx.slippage_pct,
        }
        r = await ctx.client.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 200:
            raise RuntimeError(f"openocean error: {data.get('message') or data}")

        payload = data.get("data") or {}
        out_amount = payload.get("outAmount")
        if not out_amount:
            raise RuntimeError(f"no outAmount: {payload}")

        gas = None
        g = payload.get("estimatedGas")
        if g:
            try:
                gas = int(g)
            except (TypeError, ValueError):
                gas = None

        price_impact = None
        pi = payload.get("price_impact") or payload.get("priceImpact")
        if pi is not None:
            try:
                s = str(pi).rstrip("%").strip()
                price_impact = float(s) if s else None
            except ValueError:
                price_impact = None

        return Quote(
            source=self.name,
            amount_out=self._format_amount(out_amount, ctx.buy.decimals),
            amount_out_raw=str(out_amount),
            gas=gas,
            price_impact_pct=price_impact,
        )
