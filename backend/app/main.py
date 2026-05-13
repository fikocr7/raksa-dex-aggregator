"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .chains import CHAIN_IDS, TOKENS
from .models import QuoteResponse
from .service import compare_quotes

__version__ = "0.1.0"

app = FastAPI(
    title="Raksa DEX Aggregator",
    description="Compare swap rates across 1inch, Paraswap, 0x, OpenOcean, KyberSwap.",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/api/chains")
def list_chains() -> dict[str, int]:
    return CHAIN_IDS


@app.get("/api/tokens/{chain}")
def list_tokens(chain: str) -> dict[str, dict[str, object]]:
    chain = chain.lower()
    if chain not in TOKENS:
        raise HTTPException(status_code=404, detail=f"Unknown chain: {chain}")
    return {
        sym: {"address": addr, "decimals": dec}
        for sym, (addr, dec) in TOKENS[chain].items()
    }


@app.get("/api/quote", response_model=QuoteResponse)
async def quote(
    chain: str = Query(..., description="Chain slug: ethereum | arbitrum | ..."),
    sell: str = Query(..., description="Sell token symbol or address"),
    buy: str = Query(..., description="Buy token symbol or address"),
    amount: str = Query(..., description="Human-readable sell amount, e.g. '100' or '0.5'"),
    slippage_pct: float = Query(1.0, ge=0, le=50),
) -> QuoteResponse:
    try:
        return await compare_quotes(
            chain=chain,
            sell_symbol=sell,
            buy_symbol=buy,
            amount=amount,
            slippage_pct=slippage_pct,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
