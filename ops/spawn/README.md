# OpenRouter Spawn Swarm Bootstrap

This folder gives you a reusable local swarm launcher with budget-safe defaults.

## What is included

- `swarm_plan.yaml`: default worker layout (54 workers declared)
- `launch_swarm.py`: plans/launches Spawn workers and writes structured logs
- `prompts/*.md`: role-specific execution contracts

## Quick start

1) Install Spawn CLI:

```bash
curl -fsSL --proto '=https' https://openrouter.ai/labs/spawn/cli/install.sh | bash
```

2) Ensure keys are available (example):

```bash
export OPENROUTER_API_KEY=sk-or-v1-...
```

3) Build a plan only (no credits consumed):

```bash
python3 ops/spawn/launch_swarm.py --mode plan-only
```

4) Smoke test one worker:

```bash
python3 ops/spawn/launch_swarm.py --mode dry-run --max-launches 1
```

5) Launch the full declared swarm:

```bash
python3 ops/spawn/launch_swarm.py --mode execute
```

## Artifacts

All run data is written under `artifacts/spawn/`:

- `launch_plan.json`
- `latest_summary.json`
- `YYYYMMDDTHHMMSSZ/summary.json`
- `YYYYMMDDTHHMMSSZ/logs/*.log`

## Notes

- Default `mode` in `swarm_plan.yaml` is `plan-only` to avoid accidental spend.
- Model override entries in `swarm_plan.yaml` should be validated with dry-runs first.
- Existing `ops/n8n` workflows can call this launcher as a command step.
