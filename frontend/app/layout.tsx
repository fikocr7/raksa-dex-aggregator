import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Raksa · DEX Aggregator",
  description:
    "Find the best swap rate across 1inch, Paraswap, 0x, OpenOcean, KyberSwap — compare in parallel, swap with the winner.",
  keywords: [
    "DEX",
    "aggregator",
    "crypto",
    "swap",
    "1inch",
    "Paraswap",
    "0x",
    "OpenOcean",
    "KyberSwap",
  ],
  openGraph: {
    title: "Raksa · DEX Aggregator",
    description:
      "Find the best swap rate across every major DEX aggregator.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        <div className="min-h-screen flex flex-col">{children}</div>
      </body>
    </html>
  );
}
