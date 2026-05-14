"""Core quote comparison orchestrator.

Fan out to every supported aggregator in parallel, collect results,
pick the winner, normalize into a ``QuoteResponse``.
"""
from __future__ import annotations

import asyncio
import time
from decimal import Decimal

import httpx

from .aggregators import Aggregator, QuoteContext, get_all_aggregators
from .chains import chain_id, resolve_token
from .models import BuyLeg, Quote, QuoteError, QuoteResponse, SellLeg


async def _safe_call(agg: Aggregator, ctx: QuoteContext) -> tuple[Aggregator, Quote | Exception]:
    try:
        quote = await agg.get_quote(ctx)
        return agg, quote
    except Exception as exc:  # noqa: BLE001 - we want to surface any aggregator failure
        return agg, exc


def _to_human(amount: str, decimals: int) -> str:
    return str((Decimal(amount) * (Decimal(10) ** decimals)).quantize(Decimal(1)))


async def compare_quotes(
    chain: str,
    sell_symbol: str,
    buy_symbol: str,
    amount: str,
    slippage_pct: float = 1.0,
    client: httpx.AsyncClient | None = None,
    aggregators: list[Aggregator] | None = None,
) -> QuoteResponse:
    """Fan out, compare, return normalized response.

    ``amount`` is human-readable (e.g. ``"100"`` for 100 USDC).
    """
    chain = chain.lower()
    # Solana = non-EVM, no chain_id; EVM chains get a real ID
    if chain == "solana":
        cid = 0
    else:
        cid = chain_id(chain)

    sell_addr, sell_dec = resolve_token(chain, sell_symbol)
    buy_addr, buy_dec = resolve_token(chain, buy_symbol)

    # Convert amount → wei (token base units)
    try:
        amount_dec = Decimal(amount)
    except Exception as exc:
        raise ValueError(f"Invalid amount: {amount!r}") from exc
    if amount_dec <= 0:
        raise ValueError(f"Amount must be > 0, got {amount}")
    amount_raw = str(int(amount_dec * (Decimal(10) ** sell_dec)))

    amount_str = format(amount_dec, "f")
    if "." in amount_str:
        amount_str = amount_str.rstrip("0").rstrip(".")

    sell_leg = SellLeg(
        symbol=sell_symbol.upper(),
        address=sell_addr,
        decimals=sell_dec,
        amount=amount_str or "0",
        amount_raw=amount_raw,
    )
    buy_leg = BuyLeg(symbol=buy_symbol.upper(), address=buy_addr, decimals=buy_dec)

    aggs = aggregators or get_all_aggregators()
    aggs_for_chain = [a for a in aggs if a.supports(chain)]

    owns_client = client is None
    if owns_client:
        client = httpx.AsyncClient(
            headers={"User-Agent": "raksa-dex-aggregator/0.1"},
            follow_redirects=True,
        )

    ctx = QuoteContext(
        chain=chain,
        chain_id=cid,
        sell=sell_leg,
        buy=buy_leg,
        slippage_pct=slippage_pct,
        client=client,  # type: ignore[arg-type]
    )

    start = time.perf_counter()
    try:
        results = await asyncio.gather(*(_safe_call(a, ctx) for a in aggs_for_chain))
    finally:
        if owns_client and client is not None:
            await client.aclose()
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    quotes: list[Quote] = []
    errors: list[QuoteError] = []
    for agg, outcome in results:
        if isinstance(outcome, Quote):
            quotes.append(outcome)
        else:
            status = None
            if isinstance(outcome, httpx.HTTPStatusError):
                status = outcome.response.status_code
            errors.append(
                QuoteError(
                    source=agg.name,
                    error=str(outcome)[:300],
                    status=status,
                )
            )

    # Pick winner by max amount_out_raw (ignoring gas for simplicity; can refine later)
    best_source = None
    if quotes:
        winner = max(quotes, key=lambda q: int(q.amount_out_raw))
        winner.winner = True
        best_source = winner.source
        # Sort so winner is first, then by amount desc
        quotes.sort(key=lambda q: (not q.winner, -int(q.amount_out_raw)))

    return QuoteResponse(
        chain=chain,
        sell=sell_leg,
        buy=buy_leg,
        quotes=quotes,
        errors=errors,
        elapsed_ms=elapsed_ms,
        best_source=best_source,
    )
