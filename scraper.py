"""FTC Pipeline — Phase 1: Reference Scraping.

Usage:
    python scraper.py                      # uses scrape_targets.yaml
    FTC_RUN_MODE=real python scraper.py    # hits Firecrawl / network
    FTC_RUN_MODE=dry-run python scraper.py # offline; synthesizes fixtures

Output:
    artifacts/scrapes/raw/<host>/*.json    (firecrawl payloads)
    artifacts/scrapes/reference_synthesis.json
"""

from __future__ import annotations

import json
import sys
import time

import yaml
from rich.console import Console
from rich.table import Table

from ftc.config import RUN_MODE, TARGETS, artifact_path
from ftc.scrapers import scrape_url
from ftc.synthesizer import synthesize

console = Console()


def _load_targets() -> dict:
    if not TARGETS.exists():
        console.print(f"[red]scrape_targets.yaml not found at {TARGETS}[/red]")
        sys.exit(2)
    return yaml.safe_load(TARGETS.read_text())


def main() -> int:
    cfg = _load_targets()
    limits = cfg.get("limits", {})
    rps = float(limits.get("rate_limit_rps", 0.5))
    user_agent = limits.get("user_agent", "FTC-ReferenceBot/0.1")
    respect_robots = bool(limits.get("respect_robots_txt", True))
    max_per_host = int(limits.get("max_pages_per_host", 10))

    console.rule(f"[bold]FTC Reference Scraping  (mode={RUN_MODE})[/bold]")

    results = []
    per_host: dict[str, int] = {}

    for category, value in cfg.items():
        if category == "limits" or not isinstance(value, list):
            continue
        console.print(f"\n[bold cyan]{category}[/bold cyan]  ({len(value)} URLs)")
        for url in value:
            host = url.split("/")[2] if "://" in url else url
            if per_host.get(host, 0) >= max_per_host:
                console.print(f"  [yellow]skip[/yellow] host-cap reached: {url}")
                continue
            per_host[host] = per_host.get(host, 0) + 1

            t0 = time.time()
            r = scrape_url(
                url, category=category, user_agent=user_agent, respect_robots=respect_robots,
            )
            dt = time.time() - t0
            console.print(
                f"  [green]ok[/green] {r.source:<18} {len(r.tokens):>2} tokens  "
                f"{dt:>4.1f}s  {url}"
            )
            results.append(r)
            time.sleep(max(0.0, 1.0 / rps if rps > 0 else 0))

    synthesis = synthesize(results)

    table = Table(title="Reference Synthesis — Top Clusters")
    table.add_column("Token")
    table.add_column("Frequency", justify="right")
    table.add_column("Sources", justify="right")
    for c in synthesis["clusters"]:
        table.add_row(c["token"], str(c["frequency"]), str(len(c["sources"])))
    console.print(table)

    summary_path = artifact_path("scrapes", "scrape_summary.json")
    summary_path.write_text(
        json.dumps(
            {
                "mode": RUN_MODE,
                "total_results": len(results),
                "by_source": {
                    src: sum(1 for r in results if r.source == src)
                    for src in {r.source for r in results}
                },
                "synthesis_clusters": len(synthesis["clusters"]),
            },
            indent=2,
        )
    )

    console.rule("[bold green]Phase 1 complete — Reference Scraping[/bold green]")
    console.print(f"Synthesis written to: artifacts/scrapes/reference_synthesis.json")
    console.print(f"Summary written to:   {summary_path.relative_to(summary_path.parents[2])}")
    console.print("\nNext: [bold]python run_test.py[/bold]  (Phase 2 — 5-concept test batch)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
