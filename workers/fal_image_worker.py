"""Fal.ai image worker — Flux Pro / Seedream-4 / Nano Banana.

Fal.ai is the cheapest-but-best path for Seedream-4 (which gives a different
aesthetic to Flux) and Nano Banana (mockup-specialized).

Usage:
  python workers/fal_image_worker.py --section tee --limit 5 --dry-run
  python workers/fal_image_worker.py --model seedream-4 --limit 20
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Literal

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ftc.config import RUN_MODE, require

API_BASE = "https://fal.run"

MODELS = {
    "flux-pro": os.getenv("FAL_MODEL_FLUX", "fal-ai/flux-pro/v1.1"),
    "flux-schnell": os.getenv("FAL_MODEL_FLUX_FAST", "fal-ai/flux/schnell"),
    "seedream-4": os.getenv("FAL_MODEL_SEEDREAM", "fal-ai/bytedance/seedream/v4/text-to-image"),
    "nano-banana": os.getenv("FAL_MODEL_NANO_BANANA", "fal-ai/nano-banana"),
    "nano-banana-2": os.getenv("FAL_MODEL_NANO_BANANA_2", "fal-ai/nano-banana/v2"),
}


def generate_image(
    prompt: str,
    *,
    model: str = "flux-pro",
    width: int = 832,
    height: int = 1024,
    seed: int | None = None,
) -> bytes | None:
    """Call Fal.ai, return raw image bytes or None."""
    key = require("fal")
    if key.startswith("<missing"):
        return None

    model_slug = MODELS.get(model, model)
    headers = {
        "Authorization": f"Key {key}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_images": 1,
        "enable_safety_checker": True,
    }
    if seed is not None:
        payload["seed"] = seed

    try:
        with httpx.Client(timeout=180) as client:
            resp = client.post(f"{API_BASE}/{model_slug}", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as e:
        print(f"[error] Fal.ai gen failed: {e}")
        return None

    # Fal returns `images: [{ url, width, height }]`
    images = data.get("images") or data.get("data") or []
    if not images:
        return None
    url = images[0].get("url")
    if not url:
        return None
    try:
        with httpx.Client(timeout=60) as client:
            return client.get(url).content
    except httpx.HTTPError:
        return None


def build_prompt(concept: dict[str, Any], background: Literal["black", "white"]) -> str:
    bg_desc = "pure black studio backdrop" if background == "black" else "pure white studio backdrop"
    base = concept.get("fal_ai_visual_prompt", "")
    palette = ", ".join(concept.get("color_palette", []))
    return (
        f"{base}, {bg_desc}, soft north window light, "
        f"320gsm garment-washed cotton, color palette: {palette}, "
        f"editorial product photography, 4:5 aspect ratio, "
        f"luxury streetwear, Lemaire restraint, no neon"
    )


def run(
    section: str | None,
    limit: int,
    model: str,
    background: Literal["black", "white"],
    dry_run: bool,
) -> None:
    if dry_run:
        print(f"[dry-run] Fal.ai would generate {limit} images using {model}")
        return

    concepts_dir = Path("artifacts/collection_v1/concepts")
    out_dir = Path(f"artifacts/collection_v1/renders/fal/{model}")
    out_dir.mkdir(parents=True, exist_ok=True)
    if not concepts_dir.exists():
        print(f"[error] no concepts in {concepts_dir}")
        return
    files = sorted(concepts_dir.glob("*.json"))
    if section:
        files = [f for f in files if section in f.name]
    files = files[:limit]
    for i, f in enumerate(files):
        concept = json.loads(f.read_text())
        out_path = out_dir / f"{f.stem}.png"
        if out_path.exists():
            continue
        prompt = build_prompt(concept, background)
        print(f"[{i+1}/{len(files)}] {f.stem} via {model}")
        img = generate_image(prompt, model=model, width=832, height=1024)
        if img:
            out_path.write_bytes(img)
            print(f"  saved {out_path}")
        time.sleep(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--section", default=None)
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--model", default="flux-pro", choices=list(MODELS.keys()))
    p.add_argument("--background", choices=["black", "white"], default="white")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    dry = args.dry_run or RUN_MODE in {"dry-run", "mock"}
    run(args.section, args.limit, args.model, args.background, dry)


if __name__ == "__main__":
    main()
