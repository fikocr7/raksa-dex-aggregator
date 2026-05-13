export function Hero() {
  return (
    <header className="relative w-full max-w-5xl mx-auto px-4 sm:px-6 pt-8 sm:pt-14">
      <nav className="flex items-center justify-between mb-12 animate-fade-in">
        <div className="flex items-center gap-2">
          <div className="text-2xl">🔥</div>
          <span className="font-bold tracking-tight text-lg">Raksa</span>
          <span className="chip">v0.1</span>
        </div>
        <div className="flex items-center gap-3">
          <a
            href="https://github.com/fikocr7/kiro"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-text-muted hover:text-text transition"
          >
            GitHub
          </a>
          <a
            href="#docs"
            className="text-sm text-text-muted hover:text-text transition"
          >
            Docs
          </a>
        </div>
      </nav>

      <div className="text-center animate-slide-up">
        <h1 className="text-4xl sm:text-6xl font-bold tracking-tight mb-4">
          <span className="bg-gradient-to-r from-accent via-emerald-300 to-cyan-300 bg-clip-text text-transparent">
            Best swap rate.
          </span>
          <br />
          <span className="text-text">Every time.</span>
        </h1>
        <p className="text-text-muted text-lg max-w-2xl mx-auto">
          Raksa queries{" "}
          <span className="text-text font-semibold">1inch</span>,{" "}
          <span className="text-text font-semibold">Paraswap</span>,{" "}
          <span className="text-text font-semibold">0x</span>,{" "}
          <span className="text-text font-semibold">OpenOcean</span>, and{" "}
          <span className="text-text font-semibold">KyberSwap</span> in parallel.
          You get the winner.
        </p>
      </div>
    </header>
  );
}
