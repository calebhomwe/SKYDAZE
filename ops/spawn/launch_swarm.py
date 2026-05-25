"""Spawn CLI swarm launcher for FTC execution lanes.

Default behavior is cost-safe: it only writes a launch plan (`plan-only`).
Use `--mode dry-run` or `--mode execute` to run Spawn commands.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAN = REPO_ROOT / "ops" / "spawn" / "swarm_plan.yaml"
DEFAULT_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "spawn"


@dataclass(frozen=True)
class LaunchSpec:
    instance_name: str
    worker_name: str
    agent: str
    cloud: str
    model: str | None
    prompt_file: str | None
    purpose: str
    timeout_seconds: int


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _load_plan(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Swarm plan root must be a mapping.")
    if "workers" not in data or not isinstance(data["workers"], list):
        raise ValueError("Swarm plan must contain a 'workers' list.")
    return data


def _expand_specs(plan: dict[str, Any]) -> list[LaunchSpec]:
    defaults = plan.get("defaults", {})
    cloud_default = str(defaults.get("cloud", "local"))
    prompt_default = defaults.get("prompt_file")
    timeout_default = int(defaults.get("timeout_seconds", 420))
    specs: list[LaunchSpec] = []

    for worker in plan["workers"]:
        replicas = int(worker.get("replicas", 1))
        if replicas < 1:
            continue

        worker_name = str(worker["name"])
        agent = str(worker["agent"])
        cloud = str(worker.get("cloud", cloud_default))
        model = worker.get("model")
        prompt_file = worker.get("prompt_file", prompt_default)
        purpose = str(worker.get("purpose", "unspecified"))
        timeout_seconds = int(worker.get("timeout_seconds", timeout_default))

        for i in range(1, replicas + 1):
            instance_name = f"{worker_name}-{i:02d}"
            specs.append(
                LaunchSpec(
                    instance_name=instance_name,
                    worker_name=worker_name,
                    agent=agent,
                    cloud=cloud,
                    model=str(model) if model else None,
                    prompt_file=str(prompt_file) if prompt_file else None,
                    purpose=purpose,
                    timeout_seconds=timeout_seconds,
                )
            )
    return specs


def _resolve_spawn_binary() -> str:
    home = Path.home()
    candidates = [
        shutil.which("spawn"),
        str(home / ".local" / "bin" / "spawn"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError(
        "Spawn CLI not found. Install first with:\n"
        "curl -fsSL --proto '=https' https://openrouter.ai/labs/spawn/cli/install.sh | bash"
    )


def _resolve_prompt_file(prompt_file: str | None) -> str | None:
    if not prompt_file:
        return None
    path = Path(prompt_file)
    if not path.is_absolute():
        path = REPO_ROOT / prompt_file
    return str(path)


def _build_command(spawn_bin: str, spec: LaunchSpec, mode: str) -> list[str]:
    cmd = [spawn_bin, spec.agent, spec.cloud, "--headless", "--output", "json"]
    if mode == "dry-run":
        cmd.append("--dry-run")
    if spec.model:
        cmd.extend(["--model", spec.model])
    prompt_file = _resolve_prompt_file(spec.prompt_file)
    if prompt_file:
        cmd.extend(["--prompt-file", prompt_file])
    return cmd


def _parse_json_line(output: str) -> dict[str, Any] | None:
    for line in reversed(output.splitlines()):
        line = line.strip()
        if not line.startswith("{") or not line.endswith("}"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _strip_ansi(text: str) -> str:
    ansi_escape = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
    return ansi_escape.sub("", text)


def _terminate_process_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except PermissionError:
        return

    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except PermissionError:
        return


def _run_one(
    *,
    spawn_bin: str,
    spec: LaunchSpec,
    mode: str,
    logs_dir: Path,
) -> dict[str, Any]:
    cmd = _build_command(spawn_bin, spec, mode)
    started = datetime.now(UTC)
    proc = subprocess.Popen(
        cmd,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        start_new_session=True,
        env={**os.environ, "PATH": f"{Path.home() / '.bun' / 'bin'}:{os.environ.get('PATH', '')}"},
    )
    timed_out = False
    stdout = ""
    stderr = ""
    return_code = 0
    try:
        stdout, stderr = proc.communicate(timeout=spec.timeout_seconds)
        return_code = proc.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        _terminate_process_group(proc.pid)
        stdout, stderr = proc.communicate(timeout=10)
        return_code = 124

    ended = datetime.now(UTC)
    elapsed_s = (ended - started).total_seconds()
    combined = (stdout or "") + ("\n" + stderr if stderr else "")
    cleaned = _strip_ansi(combined)
    payload = _parse_json_line(combined)

    log_file = logs_dir / f"{spec.instance_name}.log"
    log_file.write_text(combined)
    clean_log_file = logs_dir / f"{spec.instance_name}.clean.log"
    clean_log_file.write_text(cleaned)

    return {
        "instance_name": spec.instance_name,
        "worker_name": spec.worker_name,
        "agent": spec.agent,
        "cloud": spec.cloud,
        "purpose": spec.purpose,
        "model": spec.model,
        "timeout_seconds": spec.timeout_seconds,
        "command": cmd,
        "returncode": return_code,
        "success": return_code == 0,
        "timed_out": timed_out,
        "elapsed_seconds": elapsed_s,
        "json_payload": payload,
        "log_file": str(log_file),
        "clean_log_file": str(clean_log_file),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def _preflight(artifact_dir: Path) -> dict[str, Any]:
    def exists(binary: str) -> bool:
        return bool(shutil.which(binary))

    spawn_ok = True
    try:
        _resolve_spawn_binary()
    except RuntimeError:
        spawn_ok = False

    docker_compose_ok = False
    docker_message = "docker not found"
    if exists("docker"):
        try:
            proc = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            docker_compose_ok = proc.returncode == 0
            docker_message = (proc.stdout or proc.stderr or "").strip() or "unknown"
        except Exception as exc:
            docker_message = str(exc)

    payload = {
        "checked_at": _timestamp(),
        "spawn": spawn_ok,
        "bun": exists("bun") or (Path.home() / ".bun" / "bin" / "bun").exists(),
        "python3": exists("python3"),
        "docker_compose": docker_compose_ok,
        "docker_compose_message": docker_message,
        "unreal_editor": exists("UnrealEditor"),
    }
    _write_json(artifact_dir / "preflight.json", payload)
    return payload


def _launch(
    *,
    specs: list[LaunchSpec],
    mode: str,
    max_parallel: int,
    artifact_dir: Path,
) -> dict[str, Any]:
    spawn_bin = _resolve_spawn_binary()
    run_id = _timestamp()
    run_root = artifact_dir / run_id
    logs_dir = run_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_parallel) as pool:
        futures = [
            pool.submit(_run_one, spawn_bin=spawn_bin, spec=spec, mode=mode, logs_dir=logs_dir)
            for spec in specs
        ]
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as exc:
                results.append(
                    {
                        "instance_name": "unknown",
                        "worker_name": "unknown",
                        "agent": "unknown",
                        "cloud": "unknown",
                        "purpose": "unknown",
                        "model": None,
                        "returncode": 1,
                        "success": False,
                        "timed_out": False,
                        "elapsed_seconds": 0,
                        "error": str(exc),
                    }
                )

    results.sort(key=lambda item: item["instance_name"])
    success_count = sum(1 for item in results if item["success"])
    fail_count = len(results) - success_count

    summary = {
        "run_id": run_id,
        "mode": mode,
        "total_requested": len(specs),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results,
    }
    _write_json(run_root / "summary.json", summary)
    _write_json(artifact_dir / "latest_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch or plan a Spawn agent swarm.")
    parser.add_argument("--plan-file", default=str(DEFAULT_PLAN), help="Path to swarm_plan.yaml")
    parser.add_argument(
        "--mode",
        choices=["plan-only", "dry-run", "execute"],
        help="Override plan mode. Default: plan mode from YAML or plan-only.",
    )
    parser.add_argument(
        "--max-parallel",
        type=int,
        help="Override max parallel launches. Default from YAML defaults.max_parallel.",
    )
    parser.add_argument(
        "--max-launches",
        type=int,
        help="Optional cap for launches (useful for smoke tests).",
    )
    parser.add_argument(
        "--artifact-dir",
        default=str(DEFAULT_ARTIFACT_DIR),
        help="Where run plans and summaries are written.",
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Only run dependency checks and write preflight.json.",
    )
    args = parser.parse_args()

    plan_path = Path(args.plan_file)
    if not plan_path.is_absolute():
        plan_path = REPO_ROOT / plan_path
    if not plan_path.exists():
        raise FileNotFoundError(f"Swarm plan not found: {plan_path}")

    plan = _load_plan(plan_path)
    defaults = plan.get("defaults", {})
    mode = args.mode or str(defaults.get("mode", "plan-only"))
    max_parallel = int(args.max_parallel or defaults.get("max_parallel", 4))

    specs = _expand_specs(plan)
    if args.max_launches is not None:
        specs = specs[: args.max_launches]

    artifact_dir = Path(args.artifact_dir)
    if not artifact_dir.is_absolute():
        artifact_dir = REPO_ROOT / artifact_dir
    artifact_dir.mkdir(parents=True, exist_ok=True)
    preflight = _preflight(artifact_dir)
    print(
        "Preflight:",
        f"spawn={preflight['spawn']}",
        f"bun={preflight['bun']}",
        f"python3={preflight['python3']}",
        f"docker_compose={preflight['docker_compose']}",
        f"unreal_editor={preflight['unreal_editor']}",
    )
    if args.preflight_only:
        print(f"Preflight report written: {artifact_dir / 'preflight.json'}")
        return 0

    plan_payload = {
        "created_at": _timestamp(),
        "plan_file": str(plan_path),
        "mode": mode,
        "max_parallel": max_parallel,
        "worker_count": len(specs),
        "workers": [spec.__dict__ for spec in specs],
    }
    _write_json(artifact_dir / "launch_plan.json", plan_payload)
    print(f"Launch plan written: {artifact_dir / 'launch_plan.json'}")
    print(f"Workers requested: {len(specs)}")

    if mode == "plan-only":
        print("Mode=plan-only, no Spawn commands executed.")
        return 0

    summary = _launch(specs=specs, mode=mode, max_parallel=max_parallel, artifact_dir=artifact_dir)
    print(
        "Completed run:",
        f"success={summary['success_count']}",
        f"failed={summary['fail_count']}",
        f"mode={summary['mode']}",
    )
    return 0 if summary["fail_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
