"""Resilient FTC sprint orchestrator for local + n8n automation.

Runs:
  1) scraper.py
  2) run_test.py
  3) pipeline_status.py (internally via build_status)

Unlike naive shell chaining, this script always emits final status even if
Phase 2 returns FLAG/KILL. Use --strict if you want non-zero exit on failures.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Any

from pipeline_status import build_status


@dataclass
class StepResult:
    name: str
    command: list[str]
    exit_code: int
    stdout_tail: str
    stderr_tail: str


def _tail(text: str, lines: int = 30) -> str:
    parts = text.splitlines()
    return "\n".join(parts[-lines:])


def run_step(name: str, command: list[str]) -> StepResult:
    proc = subprocess.run(command, capture_output=True, text=True)
    return StepResult(
        name=name,
        command=command,
        exit_code=proc.returncode,
        stdout_tail=_tail(proc.stdout),
        stderr_tail=_tail(proc.stderr),
    )


def orchestrate() -> dict[str, Any]:
    steps = [
        run_step("phase_1_scrape", [sys.executable, "scraper.py"]),
        run_step("phase_2_test_batch", [sys.executable, "run_test.py"]),
    ]
    status = build_status()
    return {
        "steps": [asdict(step) for step in steps],
        "status": status,
        "all_steps_succeeded": all(step.exit_code == 0 for step in steps),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if any step fails",
    )
    args = parser.parse_args()

    report = orchestrate()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(json.dumps(report, indent=2))

    if args.strict and not report["all_steps_succeeded"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
