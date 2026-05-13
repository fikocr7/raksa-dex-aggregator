# 🔥 Raksa DEX Aggregator

[![CI](https://github.com/fikocr7/kiro/actions/workflows/ci.yml/badge.svg)](https://github.com/fikocr7/kiro/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

**Find the best swap rate across every major DEX aggregator — in one place.**

Raksa queries 1inch, Paraswap, 0x, OpenOcean, and KyberSwap in parallel, compares the output, and tells you who's giving you the best deal. Ships as a **FastAPI backend** + **Next.js web UI** + **CLI** so you can use it however you want.

---

## 🇺🇸 English

### Features

- 🔎 **Multi-source quotes** — parallel fetch from 1inch, Paraswap, 0x, OpenOcean, KyberSwap
- ⚡ **Fast** — ~1-2s full comparison thanks to async httpx
- 🌐 **6 chains** — Ethereum, Arbitrum, Optimism, Base, Polygon, BSC
- 💻 **Three surfaces** — REST API, Web UI, CLI
- 📊 **Breakdown per aggregator** — price impact, gas estimate, estimated output
- 🎯 **Best route highlighted** — winner based on actual amount out (after gas)
- 🌙 **Dark-mode native** — because we're not monsters

### Quick Start

#### Backend (Python 3.11+)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8787
```

#### Frontend (Node 20+)

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

#### CLI

```bash
cd backend
raksa quote --from USDC --to ETH --amount 100 --chain arbitrum
```

### API Example

```bash
curl "http://localhost:8787/api/quote?chain=arbitrum&sell=USDC&buy=ETH&amount=100"
```

```json
{
  "chain": "arbitrum",
  "sell": {"symbol": "USDC", "amount": "100"},
  "buy": {"symbol": "ETH"},
  "quotes": [
    {"source": "1inch",     "amount_out": "0.038210", "gas": 210000, "winner": true},
    {"source": "paraswap",  "amount_out": "0.038187", "gas": 225000},
    {"source": "0x",        "amount_out": "0.038175", "gas": 218000},
    {"source": "openocean", "amount_out": "0.038142", "gas": 240000},
    {"source": "kyberswap", "amount_out": "0.038098", "gas": 235000}
  ],
  "elapsed_ms": 842
}
```

### Architecture

```
┌─────────────────┐     ┌────────────────────┐
│  Next.js 14 UI  │────▶│  FastAPI backend   │
│  (wagmi/viem)   │     │  (async httpx)     │
└─────────────────┘     └─────────┬──────────┘
                                  │
         ┌────────┬────────┬──────┼──────┬──────────┐
         ▼        ▼        ▼      ▼      ▼          ▼
      1inch   Paraswap    0x  OpenOcean KyberSwap
```

Each aggregator adapter lives in `backend/app/aggregators/` and implements a common interface (`get_quote(sell, buy, amount, chain) -> Quote`). Easy to add more.

### Extending

Drop a new file in `backend/app/aggregators/`:

```python
from .base import Aggregator, Quote

class Matcha(Aggregator):
    name = "matcha"
    async def get_quote(self, ctx): ...
```

Register it in `backend/app/aggregators/__init__.py` and it'll light up in the UI automatically.

### Deploying

- **Backend** → Railway / Fly.io / Render free tier — `Dockerfile` in `backend/`
- **Frontend** → Vercel — one-click from GitHub
- Set `NEXT_PUBLIC_API_URL` in frontend env to your backend URL

---

## 🇮🇩 Bahasa Indonesia

### Apa itu Raksa?

Raksa itu DEX aggregator yang nge-cek harga swap di 5 aggregator sekaligus (1inch, Paraswap, 0x, OpenOcean, KyberSwap) terus kasih tau lu mana yg terbaik. Bisa dipake dari web, CLI, atau pake API langsung.

### Fitur

- 🔎 Quote dari 5 source sekaligus, paralel
- ⚡ ~1-2 detik full comparison
- 🌐 6 chain: ETH, Arbitrum, Optimism, Base, Polygon, BSC
- 💻 3 cara pake: REST API, Web UI, CLI
- 📊 Breakdown per aggregator: amount out, gas, price impact
- 🎯 Winner auto-highlight
- 🌙 Dark mode default

### Cepat Mulai

#### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8787
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Buka `http://localhost:3000`.

#### CLI

```bash
raksa quote --from USDC --to ETH --amount 100 --chain arbitrum
```

### Kenapa Bikin Ini?

Setiap aggregator ngaku "best rates". Kenyataannya? Beda route = beda hasil, kadang beda $5-50 per swap besar. Raksa bandingin semua sekaligus biar lu gak ketipu marketing masing-masing aggregator.

### Dokumentasi Lengkap

Lihat [`docs/`](./docs/) untuk API reference, arsitektur, dan cara nambahin aggregator baru.

---

## License

MIT © 2026

## Contributing

PRs welcome. See [CONTRIBUTING.md](./docs/CONTRIBUTING.md).

## Disclaimer

This tool returns public quote data from third-party aggregator APIs. It does NOT execute swaps automatically — swap execution requires connecting your wallet via the web UI. Use at your own risk. Always verify output amounts before confirming transactions.
