"""OKX DEX Aggregator API adapter.

Docs: https://www.okx.com/web3/build/docs/waas/dex-swap
Requires API credentials:
  OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE, OKX_PROJECT_ID

Skips gracefully if credentials are missing.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timezone

import httpx

from ..models import Quote
from .base import Aggregator, QuoteContext

_CHAIN_TO_OKX: dict[str, str] = {
    "ethereum": "1",
    "arbitrum": "42161",
    "optimism": "10",
    "base":     "8453",
    "polygon":  "137",
    "bsc":      "56",
}


class OKX(Aggregator):
    name = "okx"
    supported_chains = frozenset(_CHAIN_TO_OKX)

    BASE = "https://www.okx.com"

    @property
    def credentials(self) -> tuple[str, str, str, str] | None:
        key = os.getenv("OKX_API_KEY")
        secret = os.getenv("OKX_API_SECRET")
        passphrase = os.getenv("OKX_API_PASSPHRASE")
        project_id = os.getenv("OKX_PROJECT_ID", "")
        if not (key and secret and passphrase):
            return None
        return key, secret, passphrase, project_id

    @staticmethod
    def _sign(secret: str, ts: str, method: str, path: str, query: str = "") -> str:
        msg = f"{ts}{method}{path}{('?' + query) if query else ''}"
        digest = hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest()
        return base64.b64encode(digest).decode()

    async def get_quote(self, ctx: QuoteContext) -> Quote:
        creds = self.credentials
        if not creds:
            raise RuntimeError("OKX_API_KEY/SECRET/PASSPHRASE env not set — skipping OKX")
        key, secret, passphrase, project_id = creds

        chain_id = _CHAIN_TO_OKX[ctx.chain]
        path = "/api/v5/dex/aggregator/quote"
        params = {
            "chainId": chain_id,
            "fromTokenAddress": ctx.sell.address,
            "toTokenAddress": ctx.buy.address,
            "amount": ctx.sell.amount_raw,
        }
        # Build canonical query string (alpha-sorted, OKX-style)
        qs = "&".join(f"{k}={params[k]}" for k in sorted(params))

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
             f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
        sig = self._sign(secret, ts, "GET", path, qs)

        headers = {
            "OK-ACCESS-KEY": key,
            "OK-ACCESS-SIGN": sig,
            "OK-ACCESS-TIMESTAMP": ts,
            "OK-ACCESS-PASSPHRASE": passphrase,
            "Accept": "application/json",
        }
        if project_id:
            headers["OK-ACCESS-PROJECT"] = project_id

        url = f"{self.BASE}{path}"
        r = await ctx.client.get(url, params=params, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        body = r.json()

        if str(body.get("code")) != "0":
            raise RuntimeError(f"okx error: {body.get('msg') or body}")

        data = body.get("data") or []
        if not data:
            raise RuntimeError(f"okx: empty data {body}")
        first = data[0]

        amount_out = first.get("toTokenAmount") or first.get("toAmount")
        if not amount_out:
            raise RuntimeError(f"okx: no toTokenAmount {first}")

        gas = None
        g = first.get("estimateGasFee") or first.get("estimatedGas")
        if g:
            try:
                gas = int(g)
            except (TypeError, ValueError):
                gas = None

        # Route summary from dexRouterList[0].subRouterList
        route_names: list[str] = []
        for router in (first.get("dexRouterList") or [])[:1]:
            for sub in (router.get("subRouterList") or [])[:1]:
                for proto in (sub.get("dexProtocol") or [])[:3]:
                    nm = proto.get("dexName")
                    if nm and nm not in route_names:
                        route_names.append(nm)
        summary = " + ".join(route_names) if route_names else None

        return Quote(
            source=self.name,
            amount_out=self._format_amount(amount_out, ctx.buy.decimals),
            amount_out_raw=str(amount_out),
            gas=gas,
            route_summary=summary,
        )
