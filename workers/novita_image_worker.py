"""Novita image worker — Seedance + Flux Schnell.

Novita is cheap and fast for batch image work. Also handles video.

Usage:
  python workers/novita_image_worker.py --section tee --limit 5 --dry-run
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

API_BASE = "https://api.novita.ai/v3"

MODELS = {
    "seedance": os.getenv("NOVITA_MODEL_SEEDANCE", "seedance-pro-v1"),
    "flux-schnell": os.getenv("NOVITA_MODEL_FLUX_FAST", "FLUX.1-schnell"),
    "sdxl": os.getenv("NOVITA_MODEL_SDXL", "sdxl-base-1.0"),
}


def generate_image(
    prompt: str,
    *,
    model: str = "seedance",
    width: int = 832,
    height: int = 1024,
    seed: int | None = None,
) -> bytes | None:
    key = require("novita")
    if key.startswith("<missing"):
        return None

    model_slug = MODELS.get(model, model)
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "model_name": model_slug,
        "prompt": prompt,
        "width": width,
        "height": height,
        "image_num": 1,
        "guidance_scale": 3.5,
        "steps": 28,
    }
    if seed is not None:
        payload["seed"] = seed

    try:
        with httpx.Client(timeout=180) as client:
            resp = client.post(f"{API_BASE}/async/txt2img", headers=headers, json=payload)
            resp.raise_for_status()
            task = resp.json()
            task_id = task.get("task_id")
            if not task_id:
                return None
            for _ in range(60):
                time.sleep(2)
                status_resp = client.get(
                    f"{API_BASE}/async/task-result?task_id={task_id}",
                    headers=headers,
                )
                status_resp.raise_for_status()
                status = status_resp.json()
                if status.get("task", {}).get("status") == "TASK_STATUS_SUCCEED":
                    images = status.get("images") or []
                    if not images:
                        return None
                    image_url = images[0].get("image_url")
                    if not image_url:
                        return None
                    return client.get(image_url).content
                if status.get("task", {}).get("status") == "TASK_STATUS_FAILED":
                    return None
    except httpx.HTTPError as e:
        print(f"[error] Novita gen failed: {e}")
        return None
    return None


def build_prompt(concept: dict[str, Any], background: Literal["black", "white"]) -> str:
    bg_desc = "pure black backdrop" if background == "black" else "pure white backdrop"
    base = concept.get("fal_ai_visual_prompt", "")
    palette = ", ".join(concept.get("color_palette", []))
    return (
        f"{base}, {bg_desc}, soft window light, "
        f"320gsm cotton, color palette: {palette}, "
        f"editorial product photography, 4:5 aspect ratio, luxury streetwear, no neon"
    )


def run(section: str | None, limit: int, model: str, background: Literal["black", "white"], dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] Novita would generate {limit} images using {model}")
        return

    concepts_dir = Path("artifacts/collection_v1/concepts")
    out_dir = Path(f"artifacts/collection_v1/renders/novita/{model}")
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
        print(f"[{i+1}/{len(files)}] {f.stem} via Novita {model}")
        img = generate_image(prompt, model=model, width=832, height=1024)
        if img:
            out_path.write_bytes(img)
            print(f"  saved {out_path}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--section", default=None)
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--model", default="seedance", choices=list(MODELS.keys()))
    p.add_argument("--background", choices=["black", "white"], default="white")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    dry = args.dry_run or RUN_MODE in {"dry-run", "mock"}
    run(args.section, args.limit, args.model, args.background, dry)


if __name__ == "__main__":
    main()
