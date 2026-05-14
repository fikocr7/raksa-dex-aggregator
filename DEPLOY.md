# Deployment Guide

This guide walks through deploying Raksa to a free-tier production stack:

- **Backend** → Render.com (Docker, free tier, auto-sleep after 15min idle)
- **Frontend** → Vercel (Next.js native, free tier, no sleep)
- **Total cost: $0/month** for hobby/portfolio use

> **Why Render and not Railway?** Railway dropped its free tier in 2023. Render still offers 750 free hours/month for web services. If you have Railway credits, the included `railway.toml` works the same way — just import the repo and deploy.

---

## Step 1 — Backend on Render

### 1.1 Create the service

1. Go to https://render.com → sign up with GitHub
2. Authorize Render to read your repos
3. Click **New +** → **Web Service**
4. Pick repo `fikocr7/raksa-dex-aggregator`
5. Render auto-detects the `render.yaml` blueprint and pre-fills:
   - Name: `raksa-backend`
   - Region: Singapore
   - Plan: Free
   - Dockerfile: `./backend/Dockerfile`
   - Health check: `/health`
6. Click **Apply** and wait ~3-5min for first build

### 1.2 Verify

Once green, your URL will be something like:
```
https://raksa-backend.onrender.com
```

Test it:
```bash
curl https://raksa-backend.onrender.com/health
# → {"status":"ok","version":"0.1.0"}

curl "https://raksa-backend.onrender.com/api/quote?chain=arbitrum&sell=USDC&buy=ETH&amount=1"
# → returns 3-7 quotes
```

> **Free tier note**: the service sleeps after 15min of no traffic. First request after sleep takes ~30s. To keep it warm, set up a cron ping to `/health` every 10min (UptimeRobot has a free tier for this).

---

## Step 2 — Frontend on Vercel

### 2.1 Get a WalletConnect Project ID

1. Go to https://cloud.walletconnect.com → sign up
2. Create a project named "Raksa"
3. Copy the **Project ID** (looks like `e26a650dc9dcb42361db6c0b370fface`)

### 2.2 Deploy

1. Go to https://vercel.com → sign up with GitHub
2. Click **Add New** → **Project**
3. Import `fikocr7/raksa-dex-aggregator`
4. Configure:
   - **Root Directory**: `frontend`  *(important — Vercel needs to know the monorepo subdir)*
   - **Framework Preset**: Next.js (auto-detected)
   - **Environment Variables**:
     - `NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID` = `<your-id-from-step-2.1>`
     - `NEXT_PUBLIC_API_URL` = `https://raksa-backend.onrender.com` (from step 1.2)
5. Click **Deploy** — wait ~2min

### 2.3 Verify

Vercel gives you a URL like `https://raksa-dex-aggregator.vercel.app`. Open it:

- ✅ Page loads with "Raksa" header
- ✅ "Connect Wallet" button (top-right) opens RainbowKit modal
- ✅ Type `100 USDC → ETH` on Arbitrum → table shows quotes from Paraswap/OpenOcean/KyberSwap
- ✅ Click winning row → "Approve & Swap" button appears

---

## Step 3 — Custom Domain (optional)

### Vercel (frontend)
1. Vercel project → **Settings** → **Domains** → add `raksa.yourdomain.com`
2. Add CNAME record at your DNS provider:
   ```
   CNAME raksa  cname.vercel-dns.com
   ```
3. Vercel auto-issues SSL via Let's Encrypt (~1min)

### Render (backend)
1. Render service → **Settings** → **Custom Domain** → add `api.raksa.yourdomain.com`
2. Add CNAME record:
   ```
   CNAME api.raksa  raksa-backend.onrender.com
   ```
3. Update Vercel env var `NEXT_PUBLIC_API_URL` → `https://api.raksa.yourdomain.com`
4. Redeploy frontend (Vercel → Deployments → Redeploy latest)

---

## Troubleshooting

### Backend returns 502 from frontend (CORS error in console)
- The backend's `main.py` already sets `allow_origins=["*"]`. If you still see CORS, check the network tab — the actual error is usually that the backend is sleeping (Render free tier). Hit `/health` first to wake it.

### "Connect Wallet" modal doesn't open
- Open browser console — if you see `Project ID is undefined`, the Vercel env var didn't propagate. Redeploy the project (env vars are baked in at build time, not runtime).

### Frontend builds but quotes time out
- Default httpx timeout is 8s per aggregator. Some aggregators (especially OKX) are slow from certain regions. Check Render logs for which adapter is failing — you can drop slow ones in `backend/app/service.py:AGGREGATORS`.

### Render free tier ran out of hours
- Either upgrade to paid ($7/mo Starter plan) or migrate to Fly.io (also Docker-friendly, generous free allowance). The Dockerfile is portable — same image works on both.

---

## Architecture After Deploy

```
        ┌──────────────────────────────┐
        │  raksa.vercel.app (Vercel)   │
        │  Next.js + RainbowKit + wagmi │
        └────────────┬─────────────────┘
                     │ HTTPS
                     ▼
        ┌──────────────────────────────┐
        │ raksa-backend.onrender.com   │
        │ FastAPI + httpx              │
        └────────────┬─────────────────┘
                     │ parallel fan-out
        ┌────────────┼────────────┬────────────┬────────────┐
        ▼            ▼            ▼            ▼            ▼
    1inch       Paraswap        0x        OpenOcean     KyberSwap
                                                            │
                                                       OKX │ Jupiter
                                                            ▼
                                                          (Solana)
```
