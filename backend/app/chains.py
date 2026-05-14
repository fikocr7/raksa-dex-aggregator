"""Chain configuration: IDs, RPC URLs, common token addresses."""
from __future__ import annotations

from typing import Final

# Chain ID → canonical slug
# Solana uses sentinel 0 (no EVM chain ID); Jupiter resolves chain implicitly.
CHAIN_IDS: Final[dict[str, int]] = {
    "ethereum": 1,
    "arbitrum": 42161,
    "optimism": 10,
    "base": 8453,
    "polygon": 137,
    "bsc": 56,
    "solana": 0,
}

CHAIN_NAMES: Final[dict[int, str]] = {v: k for k, v in CHAIN_IDS.items() if v}

# Public RPC URLs (unauthenticated, low rate limit — user can override via env)
DEFAULT_RPCS: Final[dict[str, str]] = {
    "ethereum": "https://eth.drpc.org",
    "arbitrum": "https://arbitrum.drpc.org",
    "optimism": "https://optimism.drpc.org",
    "base":     "https://base.drpc.org",
    "polygon":  "https://polygon.drpc.org",
    "bsc":      "https://bsc.drpc.org",
    "solana":   "https://api.mainnet-beta.solana.com",
}

# Native token sentinel (used by 1inch/0x/paraswap for ETH/BNB/MATIC)
NATIVE_TOKEN: Final[str] = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
ZERO_TOKEN:   Final[str] = "0x0000000000000000000000000000000000000000"

# Per-chain canonical token list — symbol → (address, decimals)
TOKENS: Final[dict[str, dict[str, tuple[str, int]]]] = {
    "ethereum": {
        "ETH":   (NATIVE_TOKEN, 18),
        "WETH":  ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 18),
        "USDC":  ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
        "USDT":  ("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
        "DAI":   ("0x6B175474E89094C44Da98b954EedeAC495271d0F", 18),
        "WBTC":  ("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", 8),
    },
    "arbitrum": {
        "ETH":   (NATIVE_TOKEN, 18),
        "WETH":  ("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", 18),
        "USDC":  ("0xaf88d065e77c8cC2239327C5EDb3A432268e5831", 6),
        "USDC.e":("0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8", 6),
        "USDT":  ("0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", 6),
        "DAI":   ("0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1", 18),
        "WBTC":  ("0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f", 8),
        "ARB":   ("0x912CE59144191C1204E64559FE8253a0e49E6548", 18),
    },
    "optimism": {
        "ETH":   (NATIVE_TOKEN, 18),
        "WETH":  ("0x4200000000000000000000000000000000000006", 18),
        "USDC":  ("0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85", 6),
        "USDT":  ("0x94b008aA00579c1307B0EF2c499aD98a8ce58e58", 6),
        "DAI":   ("0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1", 18),
        "OP":    ("0x4200000000000000000000000000000000000042", 18),
    },
    "base": {
        "ETH":   (NATIVE_TOKEN, 18),
        "WETH":  ("0x4200000000000000000000000000000000000006", 18),
        "USDC":  ("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", 6),
        "USDbC": ("0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA", 6),
        "DAI":   ("0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb", 18),
        "cbETH": ("0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22", 18),
    },
    "polygon": {
        "MATIC": (NATIVE_TOKEN, 18),
        "WMATIC":("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270", 18),
        "USDC":  ("0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359", 6),
        "USDC.e":("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", 6),
        "USDT":  ("0xc2132D05D31c914a87C6611C10748AEb04B58e8F", 6),
        "DAI":   ("0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063", 18),
        "WETH":  ("0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", 18),
    },
    "bsc": {
        "BNB":   (NATIVE_TOKEN, 18),
        "WBNB":  ("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c", 18),
        "USDC":  ("0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", 18),
        "USDT":  ("0x55d398326f99059fF775485246999027B3197955", 18),
        "BUSD":  ("0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56", 18),
        "WETH":  ("0x2170Ed0880ac9A755fd29B2688956BD959F933F8", 18),
    },
    # Solana — mint addresses (base58, not 0x-hex)
    "solana": {
        "SOL":   ("So11111111111111111111111111111111111111112", 9),     # wrapped SOL
        "USDC":  ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 6),
        "USDT":  ("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", 6),
        "JUP":   ("JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN", 6),
        "BONK":  ("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", 5),
        "WIF":   ("EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", 6),
        "RAY":   ("4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R", 6),
        "JTO":   ("jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL", 9),
    },
}


def resolve_token(chain: str, symbol: str) -> tuple[str, int]:
    """Look up (address, decimals) for a symbol on a chain. Case-insensitive."""
    chain = chain.lower()
    symbol_upper = symbol.upper()
    if chain not in TOKENS:
        raise ValueError(f"Unknown chain: {chain!r}. Supported: {list(TOKENS)}")
    tokens = TOKENS[chain]
    # case-insensitive lookup
    for sym, data in tokens.items():
        if sym.upper() == symbol_upper:
            return data
    # maybe user passed a raw address — EVM hex or Solana base58
    if chain == "solana":
        # Solana mint addresses: base58, typically 32-44 chars
        if 32 <= len(symbol) <= 44 and symbol.isalnum():
            return symbol, 9  # default decimals, caller should pass real decimals
    elif symbol.startswith("0x") and len(symbol) == 42:
        return symbol, 18  # default decimals, caller can override
    raise ValueError(f"Unknown token {symbol!r} on {chain!r}. Known: {list(tokens)}")


def chain_id(chain: str) -> int:
    chain = chain.lower()
    if chain not in CHAIN_IDS:
        raise ValueError(f"Unknown chain: {chain!r}. Supported: {list(CHAIN_IDS)}")
    cid = CHAIN_IDS[chain]
    if cid == 0:
        # Solana / non-EVM — caller should not need an EVM chain ID
        raise ValueError(f"{chain!r} is non-EVM; no chain_id available")
    return cid
