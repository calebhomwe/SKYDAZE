"""FTC pipeline status reporter for humans and automation.

This script summarizes Phase 1 (scraping) and Phase 2 (test batch) progress
from artifacts. It is designed to be consumed by n8n Execute Command nodes.

Usage:
    python pipeline_status.py
    python pipeline_status.py --json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

ARTIFACTS = Path("artifacts")
SCRAPE_SYNTHESIS = ARTIFACTS / "scrapes" / "reference_synthesis.json"
TEST_LEDGER = ARTIFACTS / "qa" / "test_batch_ledger.json"


def _load_json(path: Path) -> dict[str, Any] | list[dict[str, Any]] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def build_status() -> dict[str, Any]:
    synthesis = _load_json(SCRAPE_SYNTHESIS)
    ledger = _load_json(TEST_LEDGER)

    scrape_complete = bool(synthesis)
    clusters = len(synthesis.get("clusters", [])) if isinstance(synthesis, dict) else 0

    pass_count = 0
    flag_count = 0
    kill_count = 0
    if isinstance(ledger, list):
        for item in ledger:
            verdict = str(item.get("verdict", "")).upper()
            if verdict == "PASS":
                pass_count += 1
            elif verdict == "FLAG":
                flag_count += 1
            elif verdict == "KILL":
                kill_count += 1

    test_complete = isinstance(ledger, list) and len(ledger) > 0
    full_generation_unlocked = pass_count == 5 and kill_count == 0

    phase_1_status = "complete" if scrape_complete else "pending"
    if not test_complete:
        phase_2_status = "pending"
    elif full_generation_unlocked:
        phase_2_status = "complete"
    elif kill_count == 0:
        phase_2_status = "flagged"
    else:
        phase_2_status = "blocked"

    return {
        "phase_1_reference_scraping": {
            "status": phase_1_status,
            "synthesis_exists": scrape_complete,
            "cluster_count": clusters,
            "artifact": str(SCRAPE_SYNTHESIS),
        },
        "phase_2_test_batch": {
            "status": phase_2_status,
            "ledger_exists": test_complete,
            "pass_count": pass_count,
            "flag_count": flag_count,
            "kill_count": kill_count,
            "artifact": str(TEST_LEDGER),
        },
        "phase_3_full_generation": {
            "status": "unlocked" if full_generation_unlocked else "locked",
            "requires": "5 PASS in Phase 2 and 0 KILL",
        },
        "ready_for_testing": scrape_complete and test_complete,
    }


def print_human(status: dict[str, Any]) -> None:
    console = Console()
    table = Table(title="FTC Pipeline Status")
    table.add_column("Stage")
    table.add_column("Status", justify="center")
    table.add_column("Notes")

    p1 = status["phase_1_reference_scraping"]
    table.add_row(
        "Phase 1: Reference Scraping",
        p1["status"],
        f"clusters={p1['cluster_count']} · {p1['artifact']}",
    )

    p2 = status["phase_2_test_batch"]
    table.add_row(
        "Phase 2: Test Batch (5 concepts)",
        p2["status"],
        (
            f"pass={p2['pass_count']} flag={p2['flag_count']} kill={p2['kill_count']} "
            f"· {p2['artifact']}"
        ),
    )

    p3 = status["phase_3_full_generation"]
    table.add_row("Phase 3: Full Generation (100)", p3["status"], p3["requires"])
    table.add_row(
        "Near test-ready",
        "yes" if status["ready_for_testing"] else "no",
        "Phase 1 + Phase 2 artifacts present",
    )
    console.print(table)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()

    status = build_status()
    if args.json:
        print(json.dumps(status, indent=2))
        return 0
    print_human(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
