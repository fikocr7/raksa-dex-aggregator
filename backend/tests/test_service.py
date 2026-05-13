"""Tests for the service orchestrator using mocked aggregators."""
from __future__ import annotations

import pytest

from app.aggregators.base import Aggregator, QuoteContext
from app.models import Quote
from app.service import compare_quotes


class _MockAgg(Aggregator):
    name = "mock"
    supported_chains = frozenset({"ethereum", "arbitrum"})

    def __init__(self, name: str, out_raw: str, gas: int = 200_000, fail: bool = False) -> None:
        self.name = name
        self._out = out_raw
        self._gas = gas
        self._fail = fail

    async def get_quote(self, ctx: QuoteContext) -> Quote:
        if self._fail:
            raise RuntimeError("synthetic failure")
        return Quote(
            source=self.name,
            amount_out=self._format_amount(self._out, ctx.buy.decimals),
            amount_out_raw=self._out,
            gas=self._gas,
        )


@pytest.mark.asyncio
async def test_compare_picks_highest_amount_out() -> None:
    aggs = [
        _MockAgg("alpha", out_raw="38000000000000000"),  # 0.038 ETH
        _MockAgg("bravo", out_raw="38200000000000000"),  # 0.0382 ETH (winner)
        _MockAgg("charlie", out_raw="37900000000000000"),
    ]
    result = await compare_quotes(
        chain="arbitrum",
        sell_symbol="USDC",
        buy_symbol="ETH",
        amount="100",
        aggregators=aggs,
    )
    assert result.best_source == "bravo"
    assert result.quotes[0].source == "bravo"
    assert result.quotes[0].winner is True
    # amount_out is decimal-formatted
    assert result.quotes[0].amount_out.startswith("0.0382")


@pytest.mark.asyncio
async def test_compare_collects_errors() -> None:
    aggs = [
        _MockAgg("ok", out_raw="100000000"),
        _MockAgg("dead", out_raw="0", fail=True),
    ]
    result = await compare_quotes(
        chain="ethereum",
        sell_symbol="USDC",
        buy_symbol="USDT",
        amount="100",
        aggregators=aggs,
    )
    assert len(result.quotes) == 1
    assert len(result.errors) == 1
    assert result.errors[0].source == "dead"
    assert result.best_source == "ok"


@pytest.mark.asyncio
async def test_empty_when_no_aggregators_support_chain() -> None:
    aggs = [_MockAgg("mock", out_raw="1")]  # only supports ethereum/arbitrum
    # But request optimism
    result = await compare_quotes(
        chain="optimism",
        sell_symbol="USDC",
        buy_symbol="DAI",
        amount="1",
        aggregators=aggs,
    )
    assert result.quotes == []
    assert result.errors == []
    assert result.best_source is None


@pytest.mark.asyncio
async def test_invalid_amount_rejected() -> None:
    with pytest.raises(ValueError):
        await compare_quotes(
            chain="ethereum",
            sell_symbol="USDC",
            buy_symbol="ETH",
            amount="-1",
            aggregators=[],
        )
