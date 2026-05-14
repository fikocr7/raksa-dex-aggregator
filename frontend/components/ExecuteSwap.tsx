"use client";

import { ConnectButton } from "@rainbow-me/rainbowkit";
import { useState } from "react";
import { useAccount, useChainId, useSwitchChain, useWriteContract, useSendTransaction, useWaitForTransactionReceipt, useReadContract } from "wagmi";
import { erc20Abi, type Address, parseUnits } from "viem";
import type { Quote, QuoteResponse } from "@/lib/api";
import { fetchSwapTx } from "@/lib/api";
import { cn } from "@/lib/utils";

const WAGMI_CHAIN_BY_SLUG: Record<string, number> = {
  ethereum: 1,
  arbitrum: 42161,
  optimism: 10,
  base: 8453,
  polygon: 137,
  bsc: 56,
};

const NATIVE_SENTINEL = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee";

type Props = {
  quote: QuoteResponse;
  selected: Quote;
  slippagePct: number;
};

export function ExecuteSwap({ quote, selected, slippagePct }: Props) {
  const { address, isConnected } = useAccount();
  const currentChainId = useChainId();
  const { switchChain, isPending: switchingChain } = useSwitchChain();

  const expectedChainId = WAGMI_CHAIN_BY_SLUG[quote.chain];
  const wrongChain = isConnected && expectedChainId && currentChainId !== expectedChainId;
  const evm = quote.chain !== "solana";
  const supportedSwap = ["kyberswap", "paraswap"].includes(selected.source);

  const [stage, setStage] = useState<"idle" | "fetching" | "approving" | "swapping" | "done" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [swapTx, setSwapTx] = useState<Awaited<ReturnType<typeof fetchSwapTx>> | null>(null);
  const [approveHash, setApproveHash] = useState<Address | null>(null);
  const [swapHash, setSwapHash] = useState<Address | null>(null);

  const isNative = quote.sell.address.toLowerCase() === NATIVE_SENTINEL;
  const amountInRaw = swapTx ? BigInt(swapTx.amount_in_raw) : 0n;

  // Read current allowance (only relevant for ERC20 sells)
  const { data: allowance, refetch: refetchAllowance } = useReadContract({
    abi: erc20Abi,
    address: !isNative && swapTx ? (swapTx.sell_token as Address) : undefined,
    functionName: "allowance",
    args: address && swapTx ? [address, swapTx.allowance_target as Address] : undefined,
    query: { enabled: !isNative && !!swapTx && !!address },
  });

  const needsApproval = !isNative && swapTx && (allowance === undefined || (allowance as bigint) < amountInRaw);

  const { writeContractAsync: writeApprove, isPending: writingApprove } = useWriteContract();
  const { sendTransactionAsync, isPending: writingSwap } = useSendTransaction();
  const { isLoading: waitingApprove, isSuccess: approveDone } = useWaitForTransactionReceipt({ hash: approveHash || undefined });
  const { isLoading: waitingSwap, isSuccess: swapDone } = useWaitForTransactionReceipt({ hash: swapHash || undefined });

  async function handleClick() {
    if (!isConnected || !address) return;
    setErrorMsg(null);

    try {
      // 1) Switch chain if mismatched
      if (wrongChain && expectedChainId) {
        await switchChain({ chainId: expectedChainId });
      }

      // 2) Fetch swap calldata if not already cached
      let tx = swapTx;
      if (!tx) {
        setStage("fetching");
        tx = await fetchSwapTx({
          source: selected.source,
          chain: quote.chain,
          sell: quote.sell.symbol,
          buy: quote.buy.symbol,
          amount: quote.sell.amount,
          sender: address,
          slippage_pct: slippagePct,
        });
        setSwapTx(tx);
      }

      // 3) ERC20 approve if needed
      if (!isNative) {
        const currentAllowance = (allowance as bigint | undefined) ?? 0n;
        if (currentAllowance < BigInt(tx.amount_in_raw)) {
          setStage("approving");
          const hash = await writeApprove({
            abi: erc20Abi,
            address: tx.sell_token as Address,
            functionName: "approve",
            args: [tx.allowance_target as Address, BigInt(tx.amount_in_raw)],
          });
          setApproveHash(hash);
          // Wait happens in the background via useWaitForTransactionReceipt
          // We'll rely on the user clicking again, OR auto-continue when approveDone flips
        }
      }

      // 4) Send swap tx (only if approval already in or native)
      const ok = isNative || (allowance !== undefined && (allowance as bigint) >= BigInt(tx.amount_in_raw));
      if (ok) {
        setStage("swapping");
        const hash = await sendTransactionAsync({
          to: tx.to as Address,
          data: tx.data as `0x${string}`,
          value: BigInt(tx.value),
          gas: tx.gas ? BigInt(tx.gas) : undefined,
        });
        setSwapHash(hash);
      }
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "Unknown error");
      setStage("error");
    }
  }

  // Auto-advance once approval lands
  if (approveDone && stage === "approving" && swapTx) {
    refetchAllowance();
    // user re-clicks to send swap (UX choice — explicit second confirmation is safer)
  }
  if (swapDone && stage === "swapping") {
    setTimeout(() => setStage("done"), 0);
  }

  // Solana — wallet connect not implemented yet (would need @solana/wallet-adapter)
  if (!evm) {
    return (
      <div className="card border-warning/40 bg-warning/5">
        <div className="font-semibold text-warning mb-1">Solana swap execution coming soon</div>
        <div className="text-sm text-text-muted">
          Quote-only for now. Phantom + @solana/wallet-adapter integration on the roadmap.
        </div>
      </div>
    );
  }

  if (!supportedSwap) {
    return (
      <div className="card border-warning/40 bg-warning/5">
        <div className="font-semibold text-warning mb-1">
          Swap execution not yet supported for {selected.source}
        </div>
        <div className="text-sm text-text-muted">
          Currently you can execute swaps via <span className="font-mono">kyberswap</span> or{" "}
          <span className="font-mono">paraswap</span>. Use the comparison above to pick a winner among them.
        </div>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="card flex items-center justify-between gap-4">
        <div>
          <div className="font-semibold mb-0.5">Ready to swap?</div>
          <div className="text-sm text-text-muted">
            Connect a wallet to execute via <span className="text-accent capitalize">{selected.source}</span>.
          </div>
        </div>
        <ConnectButton accountStatus="address" chainStatus="none" showBalance={false} />
      </div>
    );
  }

  const buttonLabel = (() => {
    if (stage === "fetching") return "Building tx…";
    if (writingApprove || waitingApprove) return "Approving…";
    if (writingSwap || waitingSwap) return "Swapping…";
    if (wrongChain) return switchingChain ? "Switching network…" : `Switch to ${quote.chain}`;
    if (stage === "done" && swapDone) return "✓ Swap submitted";
    if (needsApproval) return `Approve ${quote.sell.symbol}`;
    return `Swap ${quote.sell.amount} ${quote.sell.symbol} → ${quote.buy.symbol}`;
  })();

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-semibold">Execute via {selected.source}</div>
          <div className="text-xs text-text-muted">
            Connected: <span className="font-mono">{address?.slice(0, 6)}…{address?.slice(-4)}</span>
          </div>
        </div>
        <ConnectButton accountStatus="address" chainStatus="icon" showBalance={false} />
      </div>

      <button
        onClick={handleClick}
        disabled={writingApprove || waitingApprove || writingSwap || waitingSwap || stage === "fetching" || switchingChain}
        className={cn("btn-primary w-full py-3 font-semibold", stage === "done" && "bg-emerald-500")}
      >
        {buttonLabel}
      </button>

      {(approveHash || swapHash) && (
        <div className="text-xs text-text-muted space-y-1 pt-2 border-t border-border">
          {approveHash && (
            <div className="font-mono break-all">
              Approve: {approveHash.slice(0, 10)}…{approveHash.slice(-8)} {approveDone ? "✓" : "⏳"}
            </div>
          )}
          {swapHash && (
            <div className="font-mono break-all">
              Swap: {swapHash.slice(0, 10)}…{swapHash.slice(-8)} {swapDone ? "✓" : "⏳"}
            </div>
          )}
        </div>
      )}

      {errorMsg && (
        <div className="text-xs text-danger font-mono break-all border-t border-border pt-2">
          {errorMsg.slice(0, 250)}
        </div>
      )}

      <div className="text-xs text-text-dim border-t border-border pt-2">
        ⚠ This is on-chain. Swaps can fail or revert. Always double-check the recipient (your wallet),
        sell amount, and minimum receive ({(BigInt(swapTx?.min_amount_out_raw ?? "0")).toString().slice(0, 12)}…) before signing.
      </div>
    </div>
  );
}
