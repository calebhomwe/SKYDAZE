"""FTC Pipeline — Phase 2: Test Batch (5 concepts).

Generates 5 concept JSON objects, validates them against:
  - Section 4 strict schema
  - Section 1 forbidden-term scan
  - Section 5 quality gates (luxury >= 0.82, theology >= 0.75)

Phase 3 (Full Generation, 100 pieces) unlocks ONLY if all 5 PASS.

Usage:
    python run_test.py
    FTC_RUN_MODE=real python run_test.py     # hits OpenRouter + Anthropic
    FTC_RUN_MODE=dry-run python run_test.py  # offline; uses stub concepts + stub scores
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ftc.concepts import generate
from ftc.config import RUN_MODE, artifact_path
from ftc.forbidden import scan_concept
from ftc.schema import validate
from ftc.scoring import score_concept

console = Console()

DROP_BRIEF = (
    "Drop: First Light. Five pieces. Heavyweight cotton, garment-washed, "
    "monochrome + earth-tone palette. Theological through-line: thresholds, "
    "cornerstones, water, ember, veil. Restraint is the design."
)


def _load_synthesis() -> dict:
    path = Path("artifacts/scrapes/reference_synthesis.json")
    if path.exists():
        return json.loads(path.read_text())
    return {"clusters": [], "totals": {}}


def main() -> int:
    console.rule(f"[bold]FTC Test Batch — 5 concepts  (mode={RUN_MODE})[/bold]")

    synthesis = _load_synthesis()
    if not synthesis["clusters"]:
        console.print(
            "[yellow]No reference_synthesis.json found — run scraper.py first "
            "(or proceeding with empty synthesis)[/yellow]"
        )

    concepts = generate(n=5, drop_brief=DROP_BRIEF, synthesis=synthesis)
    if len(concepts) != 5:
        console.print(f"[red]Expected 5 concepts, got {len(concepts)}[/red]")
        return 2

    table = Table(title="Gate Results")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Schema", justify="center")
    table.add_column("Forbidden", justify="center")
    table.add_column("Luxury", justify="right")
    table.add_column("Theology", justify="right")
    table.add_column("Verdict", justify="center")

    pass_count = 0
    flag_count = 0
    kill_count = 0
    ledger: list[dict] = []

    for concept in concepts:
        schema_errors = validate(concept)
        forbidden_hits = scan_concept(concept)
        score = score_concept(concept)

        if schema_errors:
            verdict = "[red]KILL[/red]"
            kill_count += 1
            reason = f"schema: {'; '.join(schema_errors[:2])}"
        elif forbidden_hits:
            verdict = "[red]KILL[/red]"
            kill_count += 1
            reason = f"forbidden: {forbidden_hits[:2]}"
        elif score.passes():
            verdict = "[green]PASS[/green]"
            pass_count += 1
            reason = "ok"
        elif score.is_flagged():
            verdict = "[yellow]FLAG[/yellow]"
            flag_count += 1
            reason = "score in [0.75, 0.82) — needs human review"
        else:
            verdict = "[red]KILL[/red]"
            kill_count += 1
            reason = f"score below threshold (lux={score.luxury_score}, theo={score.theology_depth})"

        table.add_row(
            concept.get("id", "?"),
            concept.get("title", "?")[:18],
            "ok" if not schema_errors else "fail",
            "ok" if not forbidden_hits else "fail",
            f"{score.luxury_score:.2f}",
            f"{score.theology_depth:.2f}",
            verdict,
        )
        ledger.append({
            "id": concept.get("id"),
            "title": concept.get("title"),
            "schema_errors": schema_errors,
            "forbidden_hits": forbidden_hits,
            "luxury_score": score.luxury_score,
            "theology_depth": score.theology_depth,
            "rationale": score.rationale,
            "reason": reason,
            "verdict": verdict.replace("[red]", "").replace("[/red]", "")
                            .replace("[green]", "").replace("[/green]", "")
                            .replace("[yellow]", "").replace("[/yellow]", ""),
        })

    console.print(table)

    concepts_path = artifact_path("concepts", "test_batch.json")
    concepts_path.write_text(json.dumps(concepts, indent=2))

    ledger_path = artifact_path("qa", "test_batch_ledger.json")
    ledger_path.write_text(json.dumps(ledger, indent=2))

    console.print(
        f"\nPASS={pass_count}  FLAG={flag_count}  KILL={kill_count}"
    )
    console.print(f"Concepts: {concepts_path}")
    console.print(f"Ledger:   {ledger_path}")

    if pass_count == 5:
        console.rule("[bold green]Phase 2 PASS — Full Generation (Phase 3) UNLOCKED[/bold green]")
        return 0
    if kill_count == 0:
        console.rule("[bold yellow]Phase 2 FLAGGED — human review required[/bold yellow]")
        return 1
    console.rule("[bold red]Phase 2 BLOCKED — fix kills before unlocking Phase 3[/bold red]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
