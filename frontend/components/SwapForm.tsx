"use client";

import { useState, useEffect } from "react";
import type { ChainsResponse, TokensResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

type Props = {
  chains: ChainsResponse;
  chain: string;
  onChainChange: (chain: string) => void;
  tokens: TokensResponse;
  onSubmit: (p: { sell: string; buy: string; amount: string; slippage_pct: number }) => void;
  loading: boolean;
};

export function SwapForm({ chains, chain, onChainChange, tokens, onSubmit, loading }: Props) {
  const [sell, setSell] = useState("USDC");
  const [buy, setBuy] = useState("ETH");
  const [amount, setAmount] = useState("100");
  const [slippage, setSlippage] = useState(1.0);

  // Pick sensible defaults when chain tokens load
  useEffect(() => {
    const symbols = Object.keys(tokens);
    if (symbols.length === 0) return;
    if (!symbols.includes(sell)) setSell(symbols.find((s) => s.includes("USDC")) || symbols[0]);
    if (!symbols.includes(buy)) {
      const native = symbols.find((s) => ["ETH", "BNB", "MATIC"].includes(s));
      setBuy(native || symbols[1] || symbols[0]);
    }
  }, [tokens]); // eslint-disable-line react-hooks/exhaustive-deps

  function swap() {
    setSell(buy);
    setBuy(sell);
  }

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!amount || parseFloat(amount) <= 0) return;
    if (sell === buy) return;
    onSubmit({ sell, buy, amount, slippage_pct: slippage });
  }

  const tokenOptions = Object.keys(tokens);

  return (
    <form onSubmit={submit} className="card space-y-5 animate-slide-up">
      <div>
        <label className="block text-xs uppercase tracking-wider text-text-muted mb-2">
          Chain
        </label>
        <select
          value={chain}
          onChange={(e) => onChainChange(e.target.value)}
          className="input cursor-pointer"
        >
          {Object.keys(chains).map((c) => (
            <option key={c} value={c}>
              {c.charAt(0).toUpperCase() + c.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-xs uppercase tracking-wider text-text-muted mb-2">
          You pay
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            inputMode="decimal"
            value={amount}
            onChange={(e) => setAmount(e.target.value.replace(/[^\d.]/g, ""))}
            placeholder="0.0"
            className="input font-mono text-lg"
          />
          <select
            value={sell}
            onChange={(e) => setSell(e.target.value)}
            className="input w-32 cursor-pointer"
          >
            {tokenOptions.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex justify-center -my-3">
        <button
          type="button"
          onClick={swap}
          className="rounded-full border border-border bg-bg-card p-2 hover:border-accent hover:text-accent transition"
          aria-label="Swap direction"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M7 10l5-5 5 5M7 14l5 5 5-5" />
          </svg>
        </button>
      </div>

      <div>
        <label className="block text-xs uppercase tracking-wider text-text-muted mb-2">
          You receive
        </label>
        <select
          value={buy}
          onChange={(e) => setBuy(e.target.value)}
          className="input cursor-pointer"
        >
          {tokenOptions.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-xs uppercase tracking-wider text-text-muted mb-2 flex justify-between">
          <span>Slippage</span>
          <span className="text-text">{slippage}%</span>
        </label>
        <div className="flex gap-2">
          {[0.1, 0.5, 1.0, 3.0].map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSlippage(s)}
              className={cn(
                "flex-1 rounded-lg border px-3 py-1.5 text-sm transition",
                slippage === s
                  ? "border-accent bg-accent/10 text-accent"
                  : "border-border bg-bg-elevated hover:border-border-strong"
              )}
            >
              {s}%
            </button>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !amount || parseFloat(amount) <= 0 || sell === buy}
        className="btn-primary w-full py-3 text-base font-semibold"
      >
        {loading ? "Comparing…" : "Compare Rates"}
      </button>
    </form>
  );
}
