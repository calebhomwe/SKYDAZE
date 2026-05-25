# SKYDAZE

FTC pipeline workspace for luxury Christian streetwear generation.

## Fast lane (close-to-test in minutes)

1. Run scrape phase (dry-run by default):
   - `python3 scraper.py`
2. Run test batch (5 concepts + gates):
   - `python3 run_test.py`
3. Check status:
   - `python3 pipeline_status.py`
4. Run full generation when unlocked:
   - `python3 full_generate.py`

Or run all three in sequence:

- `make sprint`
- `FTC_DRY_RUN_PASS_ALL=1 make sprint` (fast-lane unlock simulation)

## Team coordination

- Execution checklist: `EXECUTION_SPRINT_CHECKLIST.md`
- n8n orchestration: `n8n/README.md`
- n8n workflow import: `n8n/ftc_pipeline_orchestrator.json`

## Useful commands

- `make scrape`
- `make test`
- `make full`
- `make status`
- `make status-json`
