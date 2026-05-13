export function Footer() {
  return (
    <footer className="border-t border-border mt-auto">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-text-muted">
        <div className="flex items-center gap-2">
          <span className="text-accent">🔥</span>
          <span>Raksa — open source DEX aggregator</span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/fikocr7/kiro"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-text transition"
          >
            GitHub
          </a>
          <a
            href="https://github.com/fikocr7/kiro/blob/main/LICENSE"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-text transition"
          >
            MIT License
          </a>
          <span>© 2026</span>
        </div>
      </div>
    </footer>
  );
}
