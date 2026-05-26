#!/usr/bin/env python3
"""Retry pipeline: generate 1000 clean design assets (SVG + PNG + EPS)."""

from __future__ import annotations

import argparse
import json
import sys
import time

from rich.console import Console
from rich.table import Table

from ftc.print_assets import export_print_pack
from ftc.trend_researcher import research_trends

console = Console()


def main() -> int:
    parser = argparse.ArgumentParser(description="FTC retry asset pipeline")
    parser.add_argument("--n", type=int, default=1000, help="Number of assets")
    parser.add_argument("--seed", default="FTC-PRINT-PACK-V2", help="Deterministic seed")
    parser.add_argument("--no-text", action="store_true", help="Strip all text layers")
    parser.add_argument("--skip-research", action="store_true", help="Skip trend synthesis step")
    args = parser.parse_args()

    console.rule("[bold]FTC Retry Pack — Pure Design Assets[/bold]")
    t0 = time.time()

    if not args.skip_research:
        console.print("[bold cyan]Research:[/bold cyan] Synthesizing trends from Reddit/Pinterest/YouTube references...")
        trends = research_trends()
        console.print(f"  Trend clusters: [green]{len(trends.get('trends', []))}[/green]")
    else:
        console.print("[dim]Research skipped[/dim]")

    console.print("[bold cyan]Generation:[/bold cyan] Exporting SVG + PNG + EPS assets...")
    result = export_print_pack(
        n=args.n,
        seed=args.seed,
        include_text=not args.no_text,
        clean_output=True,
    )

    elapsed = time.time() - t0
    table = Table(title="Retry Pack Summary")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Total assets", str(result["count"]))
    table.add_row("SVG folder", result["svg_dir"])
    table.add_row("PNG folder", result["png_dir"])
    table.add_row("EPS folder", result["eps_dir"])
    table.add_row("Manifest", result["manifest"])
    table.add_row("Elapsed", f"{elapsed:.1f}s")
    console.print(table)

    console.print("[green]Done.[/green]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
