"""Raksa CLI — ``raksa quote --from USDC --to ETH --amount 100 --chain arbitrum``."""
from __future__ import annotations

import asyncio
import os
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .service import compare_quotes

app = typer.Typer(
    name="raksa",
    help="Raksa DEX Aggregator - find the best swap rate across 5+ DEX aggregators.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def quote(
    from_token: Annotated[str, typer.Option("--from", "-f", help="Sell token symbol or address")],
    to_token: Annotated[str, typer.Option("--to", "-t", help="Buy token symbol or address")],
    amount: Annotated[str, typer.Option("--amount", "-a", help="Amount to sell, human-readable")],
    chain: Annotated[str, typer.Option("--chain", "-c", help="Chain slug")] = "ethereum",
    slippage: Annotated[float, typer.Option("--slippage", "-s", help="Slippage tolerance %")] = 1.0,
    json_out: Annotated[bool, typer.Option("--json", help="Emit JSON instead of table")] = False,
) -> None:
    """Compare swap quotes across every supported aggregator."""
    try:
        result = asyncio.run(
            compare_quotes(
                chain=chain,
                sell_symbol=from_token,
                buy_symbol=to_token,
                amount=amount,
                slippage_pct=slippage,
            )
        )
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    if json_out:
        console.print_json(result.model_dump_json())
        return

    # Header
    console.print()
    console.print(
        f"[bold cyan]◆ {result.sell.amount} {result.sell.symbol}[/bold cyan]"
        f" → [bold magenta]{result.buy.symbol}[/bold magenta]"
        f"  on [yellow]{result.chain}[/yellow]"
        f"  [dim]({result.elapsed_ms}ms)[/dim]"
    )

    if not result.quotes:
        console.print("[red]No quotes available.[/red]")
        for err in result.errors:
            console.print(f"  [red]✗[/red] {err.source}: {err.error}")
        raise typer.Exit(code=1)

    table = Table(show_header=True, header_style="bold", title=None)
    table.add_column("Source", style="cyan")
    table.add_column("Amount Out", justify="right", style="green")
    table.add_column("Gas", justify="right", style="dim")
    table.add_column("Route", style="yellow")
    table.add_column("", style="bold green")

    for q in result.quotes:
        mark = "🏆" if q.winner else ""
        gas = f"{q.gas:,}" if q.gas else "—"
        route = q.route_summary or "—"
        table.add_row(q.source, q.amount_out, gas, route[:30], mark)

    console.print(table)

    if result.errors:
        console.print()
        console.print("[dim]Failed sources:[/dim]")
        for err in result.errors:
            hint = ""
            if "API_KEY" in err.error:
                hint = f"  [dim](set {err.source.upper()}_API_KEY to enable)[/dim]"
            console.print(f"  [red]✗[/red] [cyan]{err.source}[/cyan]: {err.error[:80]}{hint}")

    if result.best_source:
        winner_q = result.quotes[0]
        console.print()
        console.print(
            f"[bold green]Best: {result.best_source}[/bold green]"
            f" → [green]{winner_q.amount_out} {result.buy.symbol}[/green]"
        )


@app.command()
def chains() -> None:
    """List supported chains."""
    from .chains import CHAIN_IDS

    table = Table(show_header=True, header_style="bold")
    table.add_column("Slug", style="cyan")
    table.add_column("Chain ID", justify="right")
    for slug, cid in CHAIN_IDS.items():
        table.add_row(slug, str(cid))
    console.print(table)


@app.command()
def tokens(chain: Annotated[str, typer.Argument(help="Chain slug")]) -> None:
    """List known tokens for a chain."""
    from .chains import TOKENS

    if chain.lower() not in TOKENS:
        console.print(f"[red]Unknown chain:[/red] {chain}")
        raise typer.Exit(code=1)

    table = Table(show_header=True, header_style="bold", title=f"Tokens on {chain}")
    table.add_column("Symbol", style="cyan")
    table.add_column("Address", style="dim")
    table.add_column("Decimals", justify="right")
    for sym, (addr, dec) in TOKENS[chain.lower()].items():
        table.add_row(sym, addr, str(dec))
    console.print(table)


@app.command()
def version() -> None:
    """Print version."""
    from .main import __version__
    console.print(f"raksa {__version__}")


if __name__ == "__main__":
    app()
