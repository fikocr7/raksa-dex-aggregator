# API Reference

Base URL: `http://localhost:8787` (default) — override with `RAKSA_API_URL` env.

## `GET /health`

Liveness probe.

```json
{"status": "ok", "version": "0.1.0"}
```

## `GET /api/chains`

List supported chains and their EVM chain IDs.

```json
{
  "ethereum": 1,
  "arbitrum": 42161,
  "optimism": 10,
  "base": 8453,
  "polygon": 137,
  "bsc": 56
}
```

## `GET /api/tokens/{chain}`

List known tokens for a chain.

```bash
curl http://localhost:8787/api/tokens/arbitrum
```

```json
{
  "ETH":  {"address": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", "decimals": 18},
  "WETH": {"address": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", "decimals": 18},
  "USDC": {"address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", "decimals": 6},
  ...
}
```

## `GET /api/quote`

Compare quotes across all aggregators.

| Param          | Type    | Required | Description                                |
|----------------|---------|----------|--------------------------------------------|
| `chain`        | string  | yes      | Chain slug from `/api/chains`              |
| `sell`         | string  | yes      | Sell token symbol or 0x address            |
| `buy`          | string  | yes      | Buy token symbol or 0x address             |
| `amount`       | string  | yes      | Sell amount (human-readable, e.g. `"100"`) |
| `slippage_pct` | float   | no       | Slippage tolerance % (default: `1.0`)      |

### Example

```bash
curl "http://localhost:8787/api/quote?chain=arbitrum&sell=USDC&buy=ETH&amount=100"
```

### Response

```json
{
  "chain": "arbitrum",
  "sell": {
    "symbol": "USDC",
    "address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    "decimals": 6,
    "amount": "100",
    "amount_raw": "100000000"
  },
  "buy": {
    "symbol": "ETH",
    "address": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    "decimals": 18
  },
  "quotes": [
    {
      "source": "kyberswap",
      "amount_out": "0.044417354026048374",
      "amount_out_raw": "44417354026048374",
      "gas": 520385,
      "gas_price_gwei": null,
      "price_impact_pct": null,
      "route_summary": "balancer-v3-eclp",
      "winner": true
    },
    {
      "source": "paraswap",
      "amount_out": "0.044342303367261292",
      "amount_out_raw": "44342303367261292",
      "gas": 270300,
      "route_summary": "MaverickV2",
      "winner": false
    }
  ],
  "errors": [
    {"source": "1inch", "error": "ONEINCH_API_KEY env var not set", "status": null}
  ],
  "elapsed_ms": 1188,
  "best_source": "kyberswap"
}
```

## API Keys

Set as environment variables before starting the server:

```bash
export ONEINCH_API_KEY="<your_1inch_key>"   # https://portal.1inch.dev
export ZEROX_API_KEY="<your_0x_key>"        # https://0x.org
```

Aggregators that don't require keys (Paraswap, OpenOcean, KyberSwap) work out of the box.

## Rate Limits

Each aggregator enforces its own rate limits. Roughly:

- **1inch** — 10 RPS on free tier
- **0x** — 30 RPS on free tier
- **Paraswap** — public endpoint, ~10 RPS soft
- **OpenOcean** — ~5 RPS
- **KyberSwap** — public endpoint, ~10 RPS

Raksa fans out queries in parallel — one request to `/api/quote` = one call per aggregator. Plan accordingly if you're calling Raksa from a high-traffic frontend.

## Error Codes

| Status | Meaning                                            |
|--------|----------------------------------------------------|
| `400`  | Invalid input (bad chain, unknown token, etc.)     |
| `404`  | Unknown chain in `/api/tokens/{chain}`             |
| `500`  | Internal error (rare — most aggregator failures are surfaced in `errors`) |

Note: when an individual aggregator fails, the request still returns `200` — failures are listed in the `errors` array.
