# 🔥 Raksa DEX Aggregator

[![CI](https://github.com/fikocr7/kiro/actions/workflows/ci.yml/badge.svg)](https://github.com/fikocr7/kiro/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

> **The best swap rate. Every time.** Multi-DEX aggregator that queries 1inch, Paraswap, 0x, OpenOcean, KyberSwap, OKX, and Jupiter (Solana) in parallel and surfaces the winner — with one-click execution via WalletConnect.

---

## ✨ Features

- **7 aggregators in parallel** — 1inch, Paraswap, 0x, OpenOcean, KyberSwap, OKX (EVM), Jupiter (Solana)
- **6 EVM chains + Solana** — Ethereum, Arbitrum, Optimism, Base, Polygon, BSC, Solana
- **CLI + Web UI** — pick whichever vibe matches your workflow
- **WalletConnect / RainbowKit** — connect MetaMask, Rabby, WalletConnect-compatible wallet, sign + execute swaps from the UI
- **ERC20 approve + swap flow** — automated approval check, slippage-protected `minAmountOut`
- **No tracking, no analytics** — runs locally, your wallet your keys
- **Async-first backend** — every aggregator queried concurrently via `httpx.AsyncClient`
- **Type-safe end to end** — Pydantic on the backend, TypeScript on the frontend

---

## 🚀 Quick Start

### CLI

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

raksa quote --from USDC --to ETH --amount 100 --chain arbitrum
```

### Web UI

```bash
# Terminal 1 — backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8787

# Terminal 2 — frontend
cd frontend
npm install
npm run dev   # opens http://localhost:3000
```

---

## 🔑 API Keys (optional)

The free aggregators (Paraswap, OpenOcean, KyberSwap, Jupiter) work out of the box.

To enable the others, set environment variables:

```bash
export ONEINCH_API_KEY="<key>"        # https://portal.1inch.dev
export ZEROX_API_KEY="<key>"          # https://0x.org
export OKX_API_KEY="<key>"            # https://www.okx.com/web3/build/dev-portal
export OKX_API_SECRET="<secret>"
export OKX_API_PASSPHRASE="<phrase>"
```

For WalletConnect Project ID (frontend):

```bash
# In frontend/.env.local
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID="your_walletconnect_project_id"
```

Get one for free at https://cloud.walletconnect.com.

---

## 📋 Live API Sample

```bash
$ curl "http://localhost:8787/api/quote?chain=arbitrum&sell=USDC&buy=ETH&amount=100"
```

```json
{
  "chain": "arbitrum",
  "best_source": "kyberswap",
  "elapsed_ms": 1188,
  "quotes": [
    {"source": "kyberswap", "amount_out": "0.044417354026048374", "winner": true},
    {"source": "paraswap",  "amount_out": "0.044342303367261292", "winner": false},
    {"source": "openocean", "amount_out": "0.044331495626232815", "winner": false}
  ]
}
```

Full reference: [docs/API.md](docs/API.md)

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  Next.js Web UI │────▶│  Python FastAPI │
│ (wagmi + viem)  │     │   (aggregator)  │
└─────────────────┘     └──────┬──────────┘
                               │ asyncio.gather
       ┌──────┬──────┬─────────┼─────────┬──────┬──────┐
       ▼      ▼      ▼         ▼         ▼      ▼      ▼
    1inch  Paraswap  0x   OpenOcean  KyberSwap OKX   Jupiter
                                                     (Solana)
```

Each aggregator is an `Aggregator` subclass with `get_quote(ctx) -> Quote`. Adding a new one is two files: the adapter + a registry line. See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

---

## 🇮🇩 Bahasa Indonesia

**Raksa** adalah DEX aggregator open-source yang membandingkan harga swap dari 7 aggregator (1inch, Paraswap, 0x, OpenOcean, KyberSwap, OKX, Jupiter) di 6 EVM chain + Solana, secara paralel. Dapet harga terbaik tanpa harus buka satu-satu.

### Instalasi cepat

```bash
# Backend (CLI)
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -e .
raksa quote --from USDC --to ETH --amount 100 --chain arbitrum

# Frontend (Web UI)
cd frontend && npm install && npm run dev
```

### Fitur utama

- 7 aggregator paralel (3-7 detik response)
- Connect wallet (MetaMask / Rabby / WalletConnect) langsung di UI
- Auto approve + swap flow dengan slippage protection
- Dukungan native ETH / BNB / MATIC + ERC20 + token Solana
- API publik gratis tanpa registrasi (untuk Paraswap, OpenOcean, KyberSwap, Jupiter)

### Kontribusi

Semua aggregator pakai pola yang sama — tinggal subclass `Aggregator`, implementasi `get_quote()`, daftarin di registry. Detail di [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

---

## 🗺️ Roadmap

- [x] CLI + REST API
- [x] Web UI dark-mode
- [x] 5 EVM aggregators
- [x] OKX aggregator
- [x] Jupiter (Solana) integration
- [x] WalletConnect + execute swap
- [ ] Solana wallet adapter (Phantom)
- [ ] Cross-chain bridge quotes (LiFi / Squid)
- [ ] Limit orders
- [ ] Historical price chart
- [ ] Self-hosted Docker compose

---

## 🤝 Contributing

PRs welcome. See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for development setup, code style, and how to add a new aggregator.

## 📜 License

[MIT](LICENSE) — do whatever you want, just don't blame us.

---

## ⚠ Disclaimer

Raksa is **not** a custodian. It does not hold funds, store private keys, or have access to your wallet. All swap calldata is built directly from public DEX aggregator APIs and signed locally by your wallet. Always verify the destination address, sell amount, and minimum receive in your wallet's confirmation prompt before signing. Crypto involves risk — slippage, MEV, sandwich attacks, and smart-contract bugs are real. Use small amounts to test first.
