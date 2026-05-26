"""OpenRouter image generation worker.

Drives Gemini Flash Image / Flux Pro 1.1 / DALL·E 3 via OpenRouter.
Configured for FTC streetwear graphics + GENESIS game backdrops.

Usage:
  python workers/openrouter_image_worker.py --section tee --limit 5 --dry-run
  python workers/openrouter_image_worker.py --section outerwear --limit 50
  python workers/openrouter_image_worker.py --target worlds --limit 13

All requests go through OpenRouter — single API key, multi-model.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Literal

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ftc.config import RUN_MODE, require

API_BASE = "https://openrouter.ai/api/v1"

# OpenRouter image model slugs (mid-2025 catalog — override via env)
MODELS = {
    "gemini-flash-image": os.getenv("OR_IMAGE_GEMINI", "google/gemini-2.5-flash-image-preview"),
    "flux-1.1-pro": os.getenv("OR_IMAGE_FLUX", "black-forest-labs/flux-1.1-pro"),
    "flux-schnell": os.getenv("OR_IMAGE_FLUX_FAST", "black-forest-labs/flux-schnell"),
    "dalle-3": os.getenv("OR_IMAGE_DALLE", "openai/dall-e-3"),
}


def generate_image(
    prompt: str,
    *,
    model: str = "flux-1.1-pro",
    width: int = 832,
    height: int = 1024,
    seed: int | None = None,
) -> bytes | None:
    """Call OpenRouter image gen, return raw image bytes or None."""
    key = require("openrouter")
    if key.startswith("<missing"):
        return None

    model_slug = MODELS.get(model, model)
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/calebhomwe/SKYDAZE",
        "X-Title": "FTC FULL TIME CHRISTIAN",
    }
    payload: dict[str, Any] = {
        "model": model_slug,
        "prompt": prompt,
        "size": f"{width}x{height}",
    }
    if seed is not None:
        payload["seed"] = seed

    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(f"{API_BASE}/images/generations", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as e:
        print(f"[error] OpenRouter image gen failed: {e}")
        return None

    # OpenAI-compatible response: data[0].b64_json OR data[0].url
    if "data" not in data or not data["data"]:
        return None
    entry = data["data"][0]
    if "b64_json" in entry:
        return base64.b64decode(entry["b64_json"])
    if "url" in entry:
        try:
            with httpx.Client(timeout=60) as client:
                return client.get(entry["url"]).content
        except httpx.HTTPError:
            return None
    return None


def build_streetwear_prompt(concept: dict[str, Any], background: Literal["black", "white"]) -> str:
    """Compose a Flux-friendly prompt from a Section 4 concept."""
    bg_desc = "pure black studio backdrop" if background == "black" else "pure white studio backdrop"
    base = concept.get("fal_ai_visual_prompt", "")
    palette = ", ".join(concept.get("color_palette", []))
    return (
        f"{base}, {bg_desc}, soft north window light, "
        f"320gsm garment-washed cotton, color palette: {palette}, "
        f"editorial product photography, 4:5 aspect ratio, "
        f"luxury streetwear, Lemaire restraint, Fear of God silhouette, "
        f"shot on Hasselblad with 80mm lens, no skin smoothing, no neon"
    )


def build_world_prompt(world: dict[str, Any]) -> str:
    """Compose a Flux prompt for a GENESIS world establishing shot."""
    palette = ", ".join(world.get("palette", []))
    return (
        f"Cinematic establishing shot of {world['name']}, "
        f"{world['region']}, golden hour, painterly Studio Ghibli style, "
        f"atmospheric perspective, fog band at horizon, "
        f"color palette: {palette}, "
        f"16:9 aspect ratio, no people in frame, no text overlay, "
        f"contemplative quiet luxury aesthetic"
    )


def run(
    target: Literal["streetwear", "worlds"],
    section: str | None,
    limit: int,
    model: str,
    background: Literal["black", "white"],
    dry_run: bool,
) -> None:
    if dry_run:
        print(f"[dry-run] would generate {limit} images for target={target} model={model}")
        if target == "streetwear":
            print(f"[dry-run] section={section} background={background}")
            print(f"[dry-run] example prompt: {build_streetwear_prompt({'fal_ai_visual_prompt': 'tonal embroidery tee in bone', 'color_palette': ['#EFE9D8', '#A88B6E']}, background)}")
        return

    if target == "streetwear":
        concepts_dir = Path("artifacts/collection_v1/concepts")
        out_dir = Path("artifacts/collection_v1/renders/openrouter")
        out_dir.mkdir(parents=True, exist_ok=True)
        if not concepts_dir.exists():
            print(f"[error] no concepts in {concepts_dir} — run `make collection` first")
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
            prompt = build_streetwear_prompt(concept, background)
            print(f"[{i+1}/{len(files)}] generating {f.stem}")
            img = generate_image(prompt, model=model, width=832, height=1024)
            if img:
                out_path.write_bytes(img)
                print(f"  saved {out_path}")
            time.sleep(1)  # gentle rate limit

    elif target == "worlds":
        from game.genesis.world_schema import ALL_WORLDS
        out_dir = Path("artifacts/game/genesis/renders/openrouter")
        out_dir.mkdir(parents=True, exist_ok=True)
        for i, world in enumerate(ALL_WORLDS[:limit]):
            world_dict = {
                "name": world.name,
                "region": world.region,
                "palette": list(world.palette),
            }
            out_path = out_dir / f"{world.id}-{world.name.lower().replace(' ', '-')}.png"
            if out_path.exists():
                continue
            prompt = build_world_prompt(world_dict)
            print(f"[{i+1}/{limit}] generating world {world.name}")
            img = generate_image(prompt, model=model, width=1280, height=720)
            if img:
                out_path.write_bytes(img)
                print(f"  saved {out_path}")
            time.sleep(1)


def main() -> None:
    p = argparse.ArgumentParser(description="FTC OpenRouter image worker")
    p.add_argument("--target", choices=["streetwear", "worlds"], default="streetwear")
    p.add_argument("--section", default=None, help="tee | tracksuit | outerwear | accessory")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--model", default="flux-1.1-pro", choices=list(MODELS.keys()))
    p.add_argument("--background", choices=["black", "white"], default="white")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    dry = args.dry_run or RUN_MODE in {"dry-run", "mock"}
    run(args.target, args.section, args.limit, args.model, args.background, dry)


if __name__ == "__main__":
    main()
