# Caveman × FTC

> Caveman is a Claude Code / Cursor / Cline / Codex / Continue / Windsurf
> skill that compresses agent output ~65-75% while keeping technical
> accuracy. Vendored as a git submodule at `tools/caveman/`.
>
> Upstream: <https://github.com/JuliusBrussee/caveman> · MIT · © Julius Brussee

## Why this matters for FTC

Our pipeline calls LLM judges and concept generators thousands of times per
drop: `luxury-score-auditor`, `theology-depth-auditor`, `restraint-editor`,
`theology-microcopy-writer`, `caption-writer`, etc. Token bytes paid for is
the dominant variable cost on the engine.

Conservative math, one full drop pass (1000 concepts × ~3 LLM passes each):

| Mode | Avg tokens / pass | Pass cost @ Sonnet 4.6 | Per-drop total |
| :--- | ---: | ---: | ---: |
| Default verbose | ~600 out | ~$0.005 | ~$15 |
| **Caveman (lite)** | **~180 out** | **~$0.0015** | **~$4.50** |

Multiply across drops + scoring + ad copy iterations → caveman pays for
itself in week one and keeps paying for itself forever.

## Install (one command)

```bash
make caveman-install
# or, equivalently, from a clean checkout:
./tools/caveman/install.sh
```

This is the upstream installer; it detects every AI coding agent on your
machine (Claude Code, Cursor, Cline, Codex, Windsurf, Continue, OpenClaw,
Gemini CLI, etc.) and registers caveman for each.

Re-run any time. It's idempotent.

## Daily commands (inside your AI agent of choice)

| Command | Behavior |
| :--- | :--- |
| `/caveman` | toggle compression at the default level (lite) |
| `/caveman full` | stronger compression — fragment-based output |
| `/caveman ultra` | maximum compression — for rote/repetitive work |
| `/caveman-commit` | terse conventional-commit message from staged diff |
| `/caveman-review` | one-line PR review comments |
| `/caveman-stats` | shows token-savings since session start |
| `/caveman-compress <file>` | rewrite a memory file (e.g. CLAUDE.md) for density |

## FTC house policy

Adopt this rule of thumb when starting a Claude Code / Cursor session in
this repo:

- **`/caveman lite`** for every dev / refactor session by default.
- **`/caveman full`** when iterating on prompts, captions, or PDP copy
  (every byte cut is real money saved per concept).
- **Default verbose** when writing user-facing prose: `BUSINESS_PLAN.md`,
  `SECURITY_QUICKSTART.md`, lookbook copy. Restraint there is editorial,
  not compressive.

## Wiring into Python pipeline (optional)

Caveman is primarily a slash-command skill, but its compression rules can
be applied to system prompts we send via the Anthropic SDK in
`ftc/scoring.py` and `ftc/concepts.py`. To enable:

```bash
export FTC_CAVEMAN=lite     # or: full | ultra
python run_test.py
```

When the env var is set, our judge / generator prepends the relevant
caveman rule block to the system prompt so the model returns dense JSON
without prose padding. The schema validator still enforces correctness, so
we never lose accuracy.

## Updating

```bash
git submodule update --remote tools/caveman
git commit -am "Bump caveman submodule"
```

## Uninstall

```bash
make caveman-uninstall
```

This calls the upstream uninstaller (per-agent reverse of the install).
