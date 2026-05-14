"use client";

import type { Quote, QuoteResponse } from "@/lib/api";
import { cn, formatNumber, formatGas, percentDiff } from "@/lib/utils";

type Props = {
  quote: QuoteResponse;
  selectedSource?: string;
  onSelect?: (q: Quote) => void;
};

export function QuoteTable({ quote, selectedSource, onSelect }: Props) {
  const winnerAmount = quote.quotes[0]?.amount_out || "0";
  const isClickable = !!onSelect;

  return (
    <div className="card animate-slide-up space-y-5">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-text-muted">Comparison</div>
          <div className="font-mono mt-1">
            <span className="text-accent">{quote.sell.amount}</span>{" "}
            <span className="text-text-muted">{quote.sell.symbol}</span>
            <span className="text-text-dim mx-2">→</span>
            <span className="text-text-muted">{quote.buy.symbol}</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs uppercase tracking-wider text-text-muted">Fetched</div>
          <div className="font-mono text-sm">
            <span className="text-accent">{quote.elapsed_ms}</span>{" "}
            <span className="text-text-muted">ms</span>
          </div>
        </div>
      </div>

      {quote.quotes.length === 0 ? (
        <div className="text-center py-8 text-text-muted">No quotes returned.</div>
      ) : (
        <div className="space-y-2">
          {quote.quotes.map((q) => {
            const isSelected = q.source === selectedSource;
            return (
            <div
              key={q.source}
              onClick={isClickable ? () => onSelect?.(q) : undefined}
              role={isClickable ? "button" : undefined}
              tabIndex={isClickable ? 0 : undefined}
              className={cn(
                "rounded-lg border p-4 transition",
                isClickable && "cursor-pointer hover:border-accent/50",
                isSelected
                  ? "border-accent bg-accent/10 ring-1 ring-accent/40"
                  : q.winner
                  ? "border-accent/40 bg-accent/5"
                  : "border-border bg-bg-elevated hover:border-border-strong"
              )}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      "h-10 w-10 rounded-lg flex items-center justify-center font-bold",
                      q.winner ? "bg-accent text-black" : "bg-bg-card text-text-muted"
                    )}
                  >
                    {q.winner ? "🏆" : q.source.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold capitalize">{q.source}</span>
                      {q.winner && (
                        <span className="chip border-accent/40 bg-accent/10 text-accent">
                          Best
                        </span>
                      )}
                    </div>
                    {q.route_summary && (
                      <div className="text-xs text-text-muted font-mono mt-0.5">
                        {q.route_summary}
                      </div>
                    )}
                  </div>
                </div>

                <div className="text-right">
                  <div className={cn("font-mono text-lg", q.winner ? "text-accent" : "text-text")}>
                    {formatNumber(q.amount_out, 8)}
                  </div>
                  <div className="text-xs text-text-muted">{quote.buy.symbol}</div>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-border/50 flex items-center gap-4 text-xs">
                <div>
                  <span className="text-text-muted">Gas: </span>
                  <span className="font-mono">{formatGas(q.gas)}</span>
                </div>
                {q.gas_price_gwei !== null && (
                  <div>
                    <span className="text-text-muted">Gwei: </span>
                    <span className="font-mono">{q.gas_price_gwei.toFixed(2)}</span>
                  </div>
                )}
                {q.price_impact_pct !== null && (
                  <div>
                    <span className="text-text-muted">Impact: </span>
                    <span className="font-mono">{q.price_impact_pct.toFixed(3)}%</span>
                  </div>
                )}
                {!q.winner && (
                  <div className="ml-auto">
                    <span className="text-text-muted">vs best: </span>
                    <span className="font-mono text-danger">
                      {percentDiff(q.amount_out, winnerAmount)}
                    </span>
                  </div>
                )}
              </div>
            </div>
            );
          })}
        </div>
      )}

      {quote.errors.length > 0 && (
        <details className="border-t border-border pt-4">
          <summary className="text-xs uppercase tracking-wider text-text-muted cursor-pointer hover:text-text">
            {quote.errors.length} source{quote.errors.length > 1 ? "s" : ""} failed (click to expand)
          </summary>
          <div className="mt-3 space-y-2">
            {quote.errors.map((e) => (
              <div key={e.source} className="flex items-start gap-2 text-xs">
                <span className="text-danger">✗</span>
                <span className="text-text capitalize font-semibold w-20 flex-shrink-0">
                  {e.source}:
                </span>
                <span className="font-mono text-text-muted break-all">{e.error}</span>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
