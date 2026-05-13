"use client";

import { useState, useEffect } from "react";
import { fetchChains, fetchTokens, fetchQuote, type QuoteResponse, type ChainsResponse, type TokensResponse } from "@/lib/api";
import { SwapForm } from "@/components/SwapForm";
import { QuoteTable } from "@/components/QuoteTable";
import { Hero } from "@/components/Hero";
import { Footer } from "@/components/Footer";

export default function HomePage() {
  const [chains, setChains] = useState<ChainsResponse>({});
  const [chain, setChain] = useState("arbitrum");
  const [tokens, setTokens] = useState<TokensResponse>({});
  const [quote, setQuote] = useState<QuoteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load chain list once
  useEffect(() => {
    fetchChains().then(setChains).catch((e) => setError(e.message));
  }, []);

  // Load tokens whenever chain changes
  useEffect(() => {
    if (!chain) return;
    fetchTokens(chain).then(setTokens).catch((e) => setError(e.message));
  }, [chain]);

  async function handleQuote(params: { sell: string; buy: string; amount: string; slippage_pct: number }) {
    setLoading(true);
    setError(null);
    setQuote(null);
    try {
      const result = await fetchQuote({ chain, ...params });
      setQuote(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Hero />
      <main className="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-6 pb-16">
        <section className="grid lg:grid-cols-5 gap-6 mt-8">
          <div className="lg:col-span-2">
            <SwapForm
              chains={chains}
              chain={chain}
              onChainChange={setChain}
              tokens={tokens}
              onSubmit={handleQuote}
              loading={loading}
            />
          </div>
          <div className="lg:col-span-3">
            {error && (
              <div className="card border-danger/50 bg-danger/5">
                <div className="flex items-start gap-3">
                  <div className="text-danger text-lg">⚠</div>
                  <div>
                    <div className="font-semibold text-danger mb-1">Error</div>
                    <div className="text-sm text-text-muted font-mono break-all">{error}</div>
                  </div>
                </div>
              </div>
            )}
            {loading && (
              <div className="card">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-accent animate-pulse-slow" />
                  <span className="text-text-muted">Querying aggregators in parallel…</span>
                </div>
              </div>
            )}
            {quote && !loading && <QuoteTable quote={quote} />}
            {!quote && !loading && !error && (
              <div className="card border-dashed text-center py-16">
                <div className="text-5xl mb-3">💹</div>
                <div className="text-text-muted">Enter a swap to see quotes from every aggregator.</div>
              </div>
            )}
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
