#!/usr/bin/env python3
"""Generate LUMENFALL cover/key art via OpenRouter image models (optional)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "assets" / "textures" / "cover_prompt.json"
PROMPT = (
    "Premium mobile rhythm game key art, Arcaea-inspired futuristic aesthetic, "
    "abstract divine light beams, cyan and gold on deep void black, "
    "minimal typography LUMENFALL, cinematic, no characters, ultra sharp UI poster"
)


def main() -> int:
    key = os.getenv("OPENROUTER_API_KEY")
    payload = {"prompt": PROMPT, "model": "openrouter/auto", "status": "prompt_only"}
    if not key or key.startswith("<missing"):
        payload["status"] = "dry_run_no_key"
        OUT.write_text(json.dumps(payload, indent=2))
        print(f"Dry-run prompt saved: {OUT}")
        return 0

    # Image endpoint varies by provider; store prompt + metadata for manual/agent render.
    payload["status"] = "ready_for_openrouter_image_api"
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"Prompt packaged for OpenRouter image generation: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
