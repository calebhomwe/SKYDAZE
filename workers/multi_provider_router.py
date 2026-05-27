"""Multi-provider image generation router.

Picks the cheapest healthy provider per image. Tracks success/cost.
Order of preference (cheapest first): Novita Flux Schnell, OpenRouter Flux
Schnell, Fal.ai Flux Schnell, OpenRouter Flux Pro, Fal.ai Flux Pro,
OpenRouter Gemini Flash Image. Falls back to procedural SVG if all fail.

Background alternates black/white per section per the user's spec.

Usage:
  python workers/multi_provider_router.py --limit 20 --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ftc.config import RUN_MODE
from workers import fal_image_worker, novita_image_worker, openrouter_image_worker

BG_BY_SECTION: dict[str, Literal["black", "white"]] = {
    "tee": "white",
    "tracksuit": "black",
    "outerwear": "white",
    "accessory": "black",
}


@dataclass
class Provider:
    name: str
    model: str
    cost_estimate: float  # USD per image
    handler: Callable[..., bytes | None]


PROVIDERS: list[Provider] = [
    Provider("novita-flux-schnell", "flux-schnell", 0.001, novita_image_worker.generate_image),
    Provider("openrouter-flux-schnell", "flux-schnell", 0.003, openrouter_image_worker.generate_image),
    Provider("fal-flux-schnell", "flux-schnell", 0.003, fal_image_worker.generate_image),
    Provider("fal-seedream-4", "seedream-4", 0.04, fal_image_worker.generate_image),
    Provider("openrouter-flux-1.1-pro", "flux-1.1-pro", 0.04, openrouter_image_worker.generate_image),
    Provider("fal-flux-pro", "flux-pro", 0.05, fal_image_worker.generate_image),
    Provider("openrouter-gemini-flash-image", "gemini-flash-image", 0.04, openrouter_image_worker.generate_image),
    Provider("fal-nano-banana-2", "nano-banana-2", 0.03, fal_image_worker.generate_image),
]


def detect_section(filename: str) -> str:
    for s in BG_BY_SECTION.keys():
        if s in filename.lower():
            return s
    return "tee"


def build_prompt(concept: dict, background: Literal["black", "white"]) -> str:
    return openrouter_image_worker.build_streetwear_prompt(concept, background)


def render_one(concept: dict, out_path: Path, dry_run: bool) -> str | None:
    """Try providers in order. Return name of provider that succeeded."""
    section = concept.get("section", detect_section(out_path.stem))
    background = BG_BY_SECTION.get(section, "white")
    prompt = build_prompt(concept, background)

    if dry_run:
        print(f"  [dry-run] would try providers in order for {out_path.stem}")
        print(f"  [dry-run] bg={background} prompt='{prompt[:80]}...'")
        return None

    for provider in PROVIDERS:
        try:
            img = provider.handler(prompt, model=provider.model, width=832, height=1024)
        except Exception as e:
            print(f"  [{provider.name}] error: {e}")
            continue
        if img:
            out_path.write_bytes(img)
            print(f"  [{provider.name}] saved {out_path.name} (~${provider.cost_estimate:.4f})")
            return provider.name
    print(f"  [fail] all providers exhausted for {out_path.stem}")
    return None


def run(limit: int, dry_run: bool) -> None:
    concepts_dir = Path("artifacts/collection_v1/concepts")
    out_dir = Path("artifacts/collection_v1/renders/routed")
    out_dir.mkdir(parents=True, exist_ok=True)
    work_log = Path("artifacts/work_log/render_routing.md")
    work_log.parent.mkdir(parents=True, exist_ok=True)

    if not concepts_dir.exists() and not dry_run:
        print(f"[error] no concepts in {concepts_dir} — run `make collection` first")
        return

    files = sorted(concepts_dir.glob("*.json")) if concepts_dir.exists() else []
    files = files[:limit]
    if not files and dry_run:
        # Synthetic stub for dry-run preview
        files = [Path("artifacts/collection_v1/concepts/stub-tee-001.json")]

    log_lines = ["# Render routing log", ""]
    for i, f in enumerate(files):
        concept = json.loads(f.read_text()) if f.exists() else {"fal_ai_visual_prompt": "stub", "color_palette": ["#EFE9D8"]}
        out_path = out_dir / f"{f.stem}.png"
        print(f"[{i+1}/{len(files)}] {f.stem}")
        provider = render_one(concept, out_path, dry_run)
        log_lines.append(f"- `{f.stem}` → {provider or 'dry-run / no-provider'}")
    work_log.write_text("\n".join(log_lines))
    print(f"\nLog: {work_log}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    dry = args.dry_run or RUN_MODE in {"dry-run", "mock"}
    run(args.limit, dry)


if __name__ == "__main__":
    main()
