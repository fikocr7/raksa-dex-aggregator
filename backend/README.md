# Raksa Backend

FastAPI service that aggregates EVM + Solana DEX quotes across 7 sources (1inch, Paraswap, 0x, OpenOcean, KyberSwap, OKX, Jupiter).

See the [main project README](https://github.com/fikocr7/raksa-dex-aggregator) for full docs.

## Quickstart

```bash
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

OpenAPI docs at `http://localhost:8000/docs`.

## Endpoints

- `GET /health`
- `GET /api/chains`
- `GET /api/tokens/{chain}`
- `GET /api/quote?chain=&sell=&buy=&amount=&slippage_pct=`
- `GET /api/swap?source=&chain=&sell=&buy=&amount=&sender=&slippage_pct=`

## Deploy

This service ships with a Dockerfile that respects `$PORT`, so it works out of the box on Railway, Render, Fly.io, and any Docker host.
