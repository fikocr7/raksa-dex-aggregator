"""Tests for chain + token resolution."""
from __future__ import annotations

import pytest

from app.chains import chain_id, resolve_token


def test_resolve_usdc_on_arbitrum() -> None:
    addr, dec = resolve_token("arbitrum", "USDC")
    assert addr.lower() == "0xaf88d065e77c8cc2239327c5edb3a432268e5831"
    assert dec == 6


def test_resolve_eth_native_sentinel() -> None:
    addr, dec = resolve_token("ethereum", "ETH")
    assert addr.lower() == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    assert dec == 18


def test_case_insensitive_symbols() -> None:
    a1, _ = resolve_token("base", "usdc")
    a2, _ = resolve_token("BASE", "USDC")
    assert a1 == a2


def test_raw_address_accepted() -> None:
    raw = "0x1234567890123456789012345678901234567890"
    addr, dec = resolve_token("ethereum", raw)
    assert addr == raw
    assert dec == 18


def test_unknown_token_raises() -> None:
    with pytest.raises(ValueError):
        resolve_token("ethereum", "DOGECOINPOG")


def test_unknown_chain_raises() -> None:
    with pytest.raises(ValueError):
        resolve_token("solana", "USDC")
    with pytest.raises(ValueError):
        chain_id("solana")


def test_chain_ids_correct() -> None:
    assert chain_id("ethereum") == 1
    assert chain_id("arbitrum") == 42161
    assert chain_id("BASE") == 8453
