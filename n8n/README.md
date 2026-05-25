# n8n Orchestration (Stay-On-Task Mode)

This folder gives a fast automation loop so the team stops manual ping-pong.

## Import workflow

1. Open n8n.
2. Import `n8n/ftc_pipeline_orchestrator.json`.
3. Set the workflow execution environment to repo root (`/workspace`).
4. Run once manually, then enable Cron if desired.

## What the workflow does

1. Runs `python3 pipeline_orchestrate.py --json`
2. Executes scrape + test batch in sequence
3. Always emits structured status JSON (even when Phase 2 is blocked)
4. Parses JSON payload for downstream alerts/actions

## Recommended environment variables

- `FTC_RUN_MODE=dry-run` for fast local validation.
- `FTC_RUN_MODE=real` when keys are configured and you want live providers.
- `FTC_DRY_RUN_PASS_ALL=1` to simulate full PASS unlock during dry-run.
- Optional budget guardrail: `FTC_DAILY_BUDGET_USD=50`

## Fast downstream extensions

- Add Slack node after `Parse Pipeline Status` for alerts.
- Add If node on `status.phase_3_full_generation.status == "unlocked"` to trigger full generation.
- Add Notion/Jira node to auto-update sprint task status.

## Single-command local status

Use this outside n8n too:

- `python3 pipeline_status.py`
- `python3 pipeline_status.py --json`
