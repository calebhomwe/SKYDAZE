"""FTC Pipeline — Phase 3: Full Generation batch runner.

Generates the full concept batch (default: 100), validates schema + forbidden
terms + quality gates, and writes concept + QA artifacts.

By default this script requires Phase 2 to be fully passed.
Override for simulation with:
  FTC_ALLOW_FULL_GEN_WITHOUT_PHASE2=1 python3 full_generate.py
"""

from __future__ import annotations

import json
import os
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
    "Drop: First Light Full Collection. One hundred pieces, luxury Christian streetwear, "
    "heavyweight 280-320gsm, restrained palettes, abstract theology through threshold, "
    "cornerstone, water, ember, and veil motifs."
)


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _phase_2_passed() -> bool:
    ledger_path = Path("artifacts/qa/test_batch_ledger.json")
    ledger = _load_json(ledger_path)
    if not isinstance(ledger, list) or len(ledger) != 5:
        return False
    pass_count = sum(1 for item in ledger if str(item.get("verdict", "")).upper() == "PASS")
    kill_count = sum(1 for item in ledger if str(item.get("verdict", "")).upper() == "KILL")
    return pass_count == 5 and kill_count == 0


def _load_synthesis() -> dict:
    path = Path("artifacts/scrapes/reference_synthesis.json")
    if path.exists():
        return json.loads(path.read_text())
    return {"clusters": [], "totals": {}}


def main() -> int:
    n = int(os.getenv("FTC_FULL_GENERATION_COUNT", "100"))
    allow_without_phase2 = os.getenv("FTC_ALLOW_FULL_GEN_WITHOUT_PHASE2", "").lower() in {
        "1",
        "true",
        "yes",
    }
    if not allow_without_phase2 and not _phase_2_passed():
        console.print(
            "[red]Phase 2 is not fully passed (needs 5 PASS, 0 KILL). "
            "Set FTC_ALLOW_FULL_GEN_WITHOUT_PHASE2=1 only for simulation.[/red]"
        )
        return 2

    console.rule(f"[bold]FTC Full Generation — {n} concepts (mode={RUN_MODE})[/bold]")
    synthesis = _load_synthesis()
    concepts = generate(n=n, drop_brief=DROP_BRIEF, synthesis=synthesis)
    if len(concepts) != n:
        console.print(f"[red]Expected {n} concepts, got {len(concepts)}[/red]")
        return 2

    pass_count = 0
    flag_count = 0
    kill_count = 0
    ledger: list[dict] = []

    for concept in concepts:
        schema_errors = validate(concept)
        forbidden_hits = scan_concept(concept)
        score = score_concept(concept)

        if schema_errors or forbidden_hits:
            verdict = "KILL"
            kill_count += 1
        elif score.passes():
            verdict = "PASS"
            pass_count += 1
        elif score.is_flagged():
            verdict = "FLAG"
            flag_count += 1
        else:
            verdict = "KILL"
            kill_count += 1

        ledger.append(
            {
                "id": concept.get("id"),
                "title": concept.get("title"),
                "schema_errors": schema_errors,
                "forbidden_hits": forbidden_hits,
                "luxury_score": score.luxury_score,
                "theology_depth": score.theology_depth,
                "rationale": score.rationale,
                "verdict": verdict,
            }
        )

    concepts_path = artifact_path("concepts", "full_generation.json")
    concepts_path.write_text(json.dumps(concepts, indent=2))
    ledger_path = artifact_path("qa", "full_generation_ledger.json")
    ledger_path.write_text(json.dumps(ledger, indent=2))

    summary_path = artifact_path(
        "qa",
        "full_generation_summary.json",
    )
    summary_path.write_text(
        json.dumps(
            {
                "count": n,
                "pass_count": pass_count,
                "flag_count": flag_count,
                "kill_count": kill_count,
                "mode": RUN_MODE,
            },
            indent=2,
        )
    )

    table = Table(title="Phase 3 Summary")
    table.add_column("Count", justify="right")
    table.add_column("PASS", justify="right")
    table.add_column("FLAG", justify="right")
    table.add_column("KILL", justify="right")
    table.add_row(str(n), str(pass_count), str(flag_count), str(kill_count))
    console.print(table)
    console.print(f"Concepts: {concepts_path}")
    console.print(f"Ledger:   {ledger_path}")
    console.print(f"Summary:  {summary_path}")

    if kill_count > 0:
        console.rule("[bold red]Phase 3 finished with KILL artifacts[/bold red]")
        return 1
    console.rule("[bold green]Phase 3 finished (no KILL artifacts)[/bold green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
