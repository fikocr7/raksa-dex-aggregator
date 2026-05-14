"""Build executable swap transaction calldata.

Currently supports KyberSwap and Paraswap (no API key required).
0x and 1inch require keys; can be added later when keys are configured.
"""
from __future__ import annotations

from decimal import Decimal

import httpx

from .chains import resolve_token
from .models import SwapTx


_KYBER_CHAIN_SLUG: dict[str, str] = {
    "ethereum": "ethereum",
    "arbitrum": "arbitrum",
    "optimism": "optimism",
    "base":     "base",
    "polygon":  "polygon",
    "bsc":      "bsc",
}

_PARASWAP_CHAIN_ID: dict[str, int] = {
    "ethereum": 1,
    "arbitrum": 42161,
    "optimism": 10,
    "base":     8453,
    "polygon":  137,
    "bsc":      56,
}


async def build_kyber_swap(
    *,
    chain: str,
    sell_symbol: str,
    buy_symbol: str,
    amount: str,
    sender: str,
    recipient: str | None = None,
    slippage_pct: float = 1.0,
) -> SwapTx:
    """Build KyberSwap aggregator swap calldata.

    Two-step flow:
    1. GET /routes  → routeSummary
    2. POST /route/build with that routeSummary + sender → calldata
    """
    chain = chain.lower()
    if chain not in _KYBER_CHAIN_SLUG:
        raise ValueError(f"KyberSwap doesn't support chain {chain!r}")
    slug = _KYBER_CHAIN_SLUG[chain]

    sell_addr, sell_dec = resolve_token(chain, sell_symbol)
    buy_addr, buy_dec = resolve_token(chain, buy_symbol)
    amount_raw = str(int(Decimal(amount) * (Decimal(10) ** sell_dec)))

    base = f"https://aggregator-api.kyberswap.com/{slug}/api/v1"
    headers = {"x-client-id": "raksa-dex-aggregator", "Accept": "application/json"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1 — get route summary
        r1 = await client.get(
            f"{base}/routes",
            params={
                "tokenIn": sell_addr,
                "tokenOut": buy_addr,
                "amountIn": amount_raw,
                "gasInclude": "true",
            },
            headers=headers,
        )
        r1.raise_for_status()
        route_data = r1.json()
        if route_data.get("code") != 0:
            raise RuntimeError(f"kyber routes: {route_data.get('message')}")
        route_summary = (route_data.get("data") or {}).get("routeSummary")
        if not route_summary:
            raise RuntimeError("kyber: missing routeSummary")
        amount_out_raw = route_summary["amountOut"]

        # Step 2 — build calldata
        slippage_bps = int(slippage_pct * 100)  # 1% = 100 bps
        recipient = recipient or sender
        r2 = await client.post(
            f"{base}/route/build",
            json={
                "routeSummary": route_summary,
                "sender": sender,
                "recipient": recipient,
                "slippageTolerance": slippage_bps,
                "deadline": 0,
                "source": "raksa",
            },
            headers={**headers, "Content-Type": "application/json"},
        )
        r2.raise_for_status()
        build_data = r2.json()
        if build_data.get("code") != 0:
            raise RuntimeError(f"kyber build: {build_data.get('message')}")
        d = build_data["data"]

    # Native ETH input means msg.value = amountIn
    is_native_in = sell_addr.lower() == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    value = amount_raw if is_native_in else "0"

    # Apply slippage to min out
    min_out = int(Decimal(amount_out_raw) * (Decimal(1) - Decimal(slippage_pct) / Decimal(100)))

    return SwapTx(
        source="kyberswap",
        chain=chain,
        to=d["routerAddress"],
        data=d["data"],
        value=value,
        gas=int(d.get("gas")) if d.get("gas") else None,
        gas_price_gwei=(int(d["gasPrice"]) / 1e9) if d.get("gasPrice") else None,
        allowance_target=d["routerAddress"],
        sell_token=sell_addr,
        buy_token=buy_addr,
        amount_in_raw=amount_raw,
        amount_out_raw=str(amount_out_raw),
        min_amount_out_raw=str(min_out),
    )


async def build_paraswap_swap(
    *,
    chain: str,
    sell_symbol: str,
    buy_symbol: str,
    amount: str,
    sender: str,
    recipient: str | None = None,
    slippage_pct: float = 1.0,
) -> SwapTx:
    """Build Paraswap v6.2 swap calldata.

    Two-step flow:
    1. GET /prices → priceRoute
    2. POST /transactions/{chainId} with that priceRoute → calldata
    """
    chain = chain.lower()
    if chain not in _PARASWAP_CHAIN_ID:
        raise ValueError(f"Paraswap doesn't support chain {chain!r}")
    cid = _PARASWAP_CHAIN_ID[chain]

    sell_addr, sell_dec = resolve_token(chain, sell_symbol)
    buy_addr, buy_dec = resolve_token(chain, buy_symbol)
    amount_raw = str(int(Decimal(amount) * (Decimal(10) ** sell_dec)))
    recipient = recipient or sender

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1 — get price route
        r1 = await client.get(
            "https://api.paraswap.io/prices",
            params={
                "srcToken": sell_addr,
                "destToken": buy_addr,
                "amount": amount_raw,
                "srcDecimals": sell_dec,
                "destDecimals": buy_dec,
                "side": "SELL",
                "network": cid,
                "version": "6.2",
            },
            headers={"Accept": "application/json"},
        )
        r1.raise_for_status()
        prices = r1.json()
        price_route = prices.get("priceRoute")
        if not price_route:
            raise RuntimeError(f"paraswap prices: {prices.get('error') or prices}")

        amount_out_raw = price_route["destAmount"]
        min_out = int(Decimal(amount_out_raw) * (Decimal(1) - Decimal(slippage_pct) / Decimal(100)))

        # Step 2 — build tx
        # Paraswap doesn't allow both `slippage` and `destAmount`; we pass `destAmount`
        # as the slippage-adjusted minimum, which is the safer of the two.
        r2 = await client.post(
            f"https://api.paraswap.io/transactions/{cid}",
            params={"ignoreChecks": "true"},
            json={
                "srcToken":     sell_addr,
                "destToken":    buy_addr,
                "srcAmount":    amount_raw,
                "destAmount":   str(min_out),
                "priceRoute":   price_route,
                "userAddress":  sender,
                "receiver":     recipient,
                "srcDecimals":  sell_dec,
                "destDecimals": buy_dec,
            },
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        if r2.status_code != 200:
            try:
                err = r2.json()
            except Exception:
                err = r2.text[:300]
            raise RuntimeError(f"paraswap build {r2.status_code}: {err}")
        tx = r2.json()
        if "to" not in tx:
            raise RuntimeError(f"paraswap build: {tx.get('error') or tx}")

    # Paraswap returns gasPrice as wei string
    gas_price_gwei = None
    if tx.get("gasPrice"):
        try:
            gas_price_gwei = int(tx["gasPrice"]) / 1e9
        except (TypeError, ValueError):
            gas_price_gwei = None

    gas = None
    if tx.get("gas"):
        try:
            gas = int(tx["gas"])
        except (TypeError, ValueError):
            gas = None

    return SwapTx(
        source="paraswap",
        chain=chain,
        to=tx["to"],
        data=tx["data"],
        value=str(tx.get("value", "0")),
        gas=gas,
        gas_price_gwei=gas_price_gwei,
        allowance_target=price_route.get("tokenTransferProxy") or tx["to"],
        sell_token=sell_addr,
        buy_token=buy_addr,
        amount_in_raw=amount_raw,
        amount_out_raw=str(amount_out_raw),
        min_amount_out_raw=str(min_out),
    )


async def build_swap(
    *,
    source: str,
    chain: str,
    sell_symbol: str,
    buy_symbol: str,
    amount: str,
    sender: str,
    recipient: str | None = None,
    slippage_pct: float = 1.0,
) -> SwapTx:
    """Dispatch to the right adapter."""
    src = source.lower()
    kwargs = dict(
        chain=chain,
        sell_symbol=sell_symbol,
        buy_symbol=buy_symbol,
        amount=amount,
        sender=sender,
        recipient=recipient,
        slippage_pct=slippage_pct,
    )
    if src == "kyberswap":
        return await build_kyber_swap(**kwargs)  # type: ignore[arg-type]
    if src == "paraswap":
        return await build_paraswap_swap(**kwargs)  # type: ignore[arg-type]
    raise ValueError(
        f"Swap building not yet implemented for {source!r}. "
        f"Currently supported: kyberswap, paraswap."
    )
