# LUMENFALL Agent Squad

Curated OpenRouter Spawn workers for app-quality Godot development.

## Models (via OpenRouter)

| Worker | Agent | Model | Role |
|--------|-------|-------|------|
| codex-gameplay ×2 | codex | openai/gpt-5.3-codex | Gameplay, holds, arcs |
| claude-synthesis | claude | anthropic/claude-opus-4.6 | Architecture + QA gate |
| sonnet-gdscript ×2 | cursor | anthropic/claude-sonnet-4.6 | GDScript + UI |
| gemini-ux ×2 | cursor | google/gemini-2.5-pro | Menu/HUD polish |
| qwen-coder-tools | cursor | qwen/qwen3-coder-plus | Charts + tools |
| deepseek-perf | cursor | deepseek/deepseek-v4-flash | Stress/perf |
| kilocode-refactor ×2 | kilocode | (default) | Refactor |
| opencode-terminal | opencode | (default) | Scripts/QA |

## Commands

```bash
make spawn-lumenfall-plan      # 12-worker plan, no spend
make spawn-lumenfall-dry       # smoke 12 workers (validates models + prompt)
make spawn-lumenfall-execute   # launch 4 workers (bounded spend)
```

Plan file: `ops/spawn/swarm_plan_lumenfall.yaml`  
Prompt: `ops/spawn/prompts/lumenfall_app_squad.md` (no shell backticks — Spawn rejects them)

Requires `OPENROUTER_API_KEY` in environment.
