# Contributing to Raksa

## Development Setup

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Adding a New Aggregator

1. Create `backend/app/aggregators/myaggregator.py`:

    ```python
    from ..models import Quote
    from .base import Aggregator, QuoteContext

    class MyAggregator(Aggregator):
        name = "myagg"
        supported_chains = frozenset({"ethereum", "arbitrum"})

        async def get_quote(self, ctx: QuoteContext) -> Quote:
            # call your API, return Quote(...)
            ...
    ```

2. Register it in `backend/app/aggregators/__init__.py`:

    ```python
    from .myaggregator import MyAggregator
    # ...
    def get_all_aggregators() -> list[Aggregator]:
        return [
            OneInch(), Paraswap(), ZeroX(),
            OpenOcean(), KyberSwap(),
            MyAggregator(),  # ← add here
        ]
    ```

3. Run `pytest tests/` — existing tests should still pass.

4. Open PR.

## Code Style

- Backend: `ruff check app/` must pass. `mypy --strict` recommended.
- Frontend: `npm run typecheck` + `npm run lint` must pass.
- Keep lines under 100 chars where reasonable.

## Commit Messages

Conventional commits format:
- `feat: add Matcha aggregator`
- `fix: handle 1inch v6 response shape change`
- `docs: clarify CLI usage`
- `chore: bump deps`

## License

By contributing, you agree your code is released under MIT.
