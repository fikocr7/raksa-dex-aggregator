"""Shared Pydantic models for quotes and quote requests."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class TokenInfo(BaseModel):
    symbol: str
    address: str
    decimals: int


class SellLeg(BaseModel):
    symbol: str
    address: str
    decimals: int
    amount: str  # human-readable decimal string, e.g. "100"
    amount_raw: str  # wei, e.g. "100000000"


class BuyLeg(BaseModel):
    symbol: str
    address: str
    decimals: int


class Quote(BaseModel):
    source: str  # "1inch" | "paraswap" | "0x" | "openocean" | "kyberswap" | "okx" | "jupiter"
    amount_out: str  # human-readable, e.g. "0.038210"
    amount_out_raw: str  # wei
    gas: int | None = None
    gas_price_gwei: float | None = None
    price_impact_pct: float | None = None
    route_summary: str | None = None
    raw: dict[str, Any] | None = None  # original API response, for debug
    winner: bool = False  # set by comparison layer


class SwapTx(BaseModel):
    """EVM swap transaction calldata returned by /api/swap."""
    source: str
    chain: str
    to: str  # router/aggregator contract address
    data: str  # 0x-prefixed hex calldata
    value: str  # native token amount in wei (decimal string)
    gas: int | None = None
    gas_price_gwei: float | None = None
    allowance_target: str  # ERC20 spender address (router)
    sell_token: str
    buy_token: str
    amount_in_raw: str
    amount_out_raw: str
    min_amount_out_raw: str


class QuoteError(BaseModel):
    source: str
    error: str
    status: int | None = None


class QuoteResponse(BaseModel):
    chain: str
    sell: SellLeg
    buy: BuyLeg
    quotes: list[Quote] = Field(default_factory=list)
    errors: list[QuoteError] = Field(default_factory=list)
    elapsed_ms: int
    best_source: str | None = None


class QuoteRequest(BaseModel):
    chain: str = Field(..., description="Chain slug: ethereum, arbitrum, optimism, base, polygon, bsc")
    sell: str = Field(..., description="Sell token symbol (USDC) or address (0x...)")
    buy: str = Field(..., description="Buy token symbol or address")
    amount: str = Field(..., description="Human-readable amount to sell, e.g. '100' or '0.5'")
    slippage_pct: float = Field(1.0, ge=0, le=50, description="Max slippage tolerance, percent")
