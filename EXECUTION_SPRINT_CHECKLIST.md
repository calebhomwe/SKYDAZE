# FTC 5-Minute Sprint Checklist (Speed Mode)

Goal: get the pipeline near test-ready with clear ownership and no idle gaps.

## A. Immediate sequence (run in order)

1. **Phase 1 scrape (dry-run first)**
   - Command: `python3 scraper.py`
   - Success: `artifacts/scrapes/reference_synthesis.json` exists.
2. **Phase 2 test batch (5 concepts)**
   - Command: `python3 run_test.py`
   - Success: `artifacts/qa/test_batch_ledger.json` exists.
3. **Status checkpoint**
   - Command: `python3 pipeline_status.py`
   - Success: clear PASS/FLAG/KILL summary.
4. **If Phase 2 has KILL**
   - Fix prompt/schema/forbidden causes, then rerun Phase 2.
5. **If Phase 2 is PASS**
   - Unlock and run full generation next sprint.
   - Command: `python3 full_generate.py`

Optional fast-lane simulation for orchestration checks:
- `FTC_DRY_RUN_PASS_ALL=1 make sprint`

## B. Ownership map (who is on task)

- **Pipeline execution:** `phase-director`, `drop-architect`
- **Scrape quality:** `firecrawl-operator`, `reference-synthesizer`
- **Concept quality gates:** `quality-gate-keeper`, `json-schema-validator`, `forbidden-term-detector`, `theology-depth-auditor`
- **Creative ad generation:** `trap-cinema-creative-director`, `cinematic-video-prompt-engineer`, `visual-qwen-shot-generator`, `audio-speech-score-designer`
- **Routing/infra:** `openrouter-multimodal-router`, `cost-monitor`, `api-health-checker`

## C. Fast blocker triage

- **Missing artifacts:** rerun prior phase command, do not skip ahead.
- **Forbidden terms present:** regenerate only failed concepts, keep passing ones.
- **Low luxury/theology score:** route to `FLAG` review path; tighten prompts before retry.
- **Provider issues:** Novita video -> OpenRouter fallback immediately.

## D. Done definition for “close to being tested”

- Phase 1 artifact exists.
- Phase 2 ledger exists and has no schema failures.
- `pipeline_status.py` reports both Phase 1 and Phase 2 artifacts present.
- Team can run status from one command without manual inspection.
