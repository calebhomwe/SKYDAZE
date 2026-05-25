# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

FTC FULL TIME CHRISTIAN is an AI-powered luxury Christian streetwear design pipeline. The core flow is: reference scraping -> concept generation (LLM) -> visual generation -> mockup rendering -> e-commerce. See `FTC_MASTER_CONTEXT.md` for the brand bible and full specification.

### Development environment

- **Language:** Python 3.12
- **Package manager:** pip with `pyproject.toml` (editable install: `pip install -e ".[dev]"`)
- **Linter/formatter:** ruff (configured in `pyproject.toml`)
- **Test framework:** pytest with anyio plugin for async tests

### Key commands

| Task | Command |
|------|---------|
| Install deps | `pip install -e ".[dev]"` |
| Lint | `ruff check ftc/ tests/` |
| Format | `ruff format ftc/ tests/` |
| Test | `pytest -v` |
| Run CLI | `ftc-pipeline status` / `ftc-pipeline validate <file>` / `ftc-pipeline check-env` |

### Non-obvious notes

- `$HOME/.local/bin` must be on `PATH` for `ruff`, `pytest`, and `ftc-pipeline` CLI to work (pip installs there as non-root).
- API keys (`OPENROUTER_API_KEY`, `FAL_AI_API_KEY`, `FIRECRAWL_API_KEY`, `NOVITA_API_KEY`) are not required for tests or local validation — only for live generation. Tests mock or skip API calls.
- The `DesignConcept` model enforces an `FTC-XXX` ID pattern and requires at least one color in `color_palette`.
- Quality gate thresholds are in `ftc/config.py`: luxury ≥ 0.82, theology ≥ 0.75, auto-kill < 0.60.
- The forbidden terms list (Section 1 of master context) is enforced by `validate_no_forbidden()` in `ftc/config.py`.
