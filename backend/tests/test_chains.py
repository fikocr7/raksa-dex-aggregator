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
        resolve_token("aptos", "USDC")
    with pytest.raises(ValueError):
        chain_id("aptos")


def test_chain_ids_correct() -> None:
    assert chain_id("ethereum") == 1
    assert chain_id("arbitrum") == 42161
    assert chain_id("BASE") == 8453


def test_solana_chain_id_raises() -> None:
    """Solana is non-EVM and has no usable EVM chain_id."""
    with pytest.raises(ValueError, match="non-EVM"):
        chain_id("solana")


def test_solana_resolves_known_token() -> None:
    addr, dec = resolve_token("solana", "USDC")
    assert addr == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    assert dec == 6


def test_solana_raw_mint_accepted() -> None:
    mint = "So11111111111111111111111111111111111111112"
    addr, dec = resolve_token("solana", mint)
    assert addr == mint
