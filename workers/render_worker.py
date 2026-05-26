"""Photoreal render worker.

For each design in artifacts/collection_v1/concepts/, calls Fal.ai
(Seedream-4 by default, Flux Pro as fallback) using fal_ai_visual_prompt
from the concept JSON. Saves the rendered image alongside the SVG and
updates the catalog to prefer the photoreal asset.

Run:
    cp .env.example .env   # fill FAL_KEY
    python workers/render_worker.py                 # render everything missing
    python workers/render_worker.py --section tracksuit --limit 50
    python workers/render_worker.py --dry-run       # estimate cost without calling

Cost guard:
    Hard-stops if estimated spend > FTC_DAILY_BUDGET_USD from .env.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Make `from ftc...` work whether the worker is run from repo root or workers/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ftc.config import ARTIFACTS, DAILY_BUDGET_USD, RUN_MODE  # noqa: E402

COLLECTION_DIR = ARTIFACTS / "collection_v1"
CONCEPTS_DIR = COLLECTION_DIR / "concepts"
RENDER_DIR = COLLECTION_DIR / "renders"

# Provider cost estimates (USD per image, rough)
COST_PER_IMAGE = {
    "fal-ai/flux-pro": 0.05,
    "fal-ai/bytedance/seedream/v4/text-to-image": 0.04,
}
DEFAULT_MODEL = "fal-ai/bytedance/seedream/v4/text-to-image"


def _designs_to_render(section: str | None, limit: int | None) -> list[dict]:
    if not CONCEPTS_DIR.exists():
        print(f"[error] {CONCEPTS_DIR} not found. Run: python generate_collection.py")
        sys.exit(2)
    concepts = []
    for path in sorted(CONCEPTS_DIR.glob("*.json")):
        c = json.loads(path.read_text())
        if section and not c["id"].lower().startswith(f"ftc-{section[:2].lower()}"):
            continue
        rendered = RENDER_DIR / f"{c['id']}.png"
        if rendered.exists():
            continue  # idempotent
        concepts.append(c)
        if limit and len(concepts) >= limit:
            break
    return concepts


def _estimate(n: int, model: str) -> float:
    return n * COST_PER_IMAGE.get(model, 0.05)


def _call_fal(prompt: str, model: str) -> bytes | None:
    """Real Fal.ai call. Imports fal_client lazily so dry-run stays dep-free."""
    import fal_client  # type: ignore

    handler = fal_client.submit(
        model,
        arguments={"prompt": prompt, "aspect_ratio": "4:5", "num_images": 1},
    )
    result = handler.get()
    images = result.get("images") or []
    if not images:
        return None
    img_url = images[0].get("url")
    if not img_url:
        return None
    import httpx

    r = httpx.get(img_url, timeout=120.0)
    r.raise_for_status()
    return r.content


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--section", choices=["tracksuit", "outerwear", "tee", "accessory"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    concepts = _designs_to_render(args.section, args.limit)
    est_cost = _estimate(len(concepts), args.model)
    print(f"[plan] {len(concepts)} designs to render with {args.model}")
    print(f"[plan] estimated cost: ${est_cost:.2f}  (FTC_DAILY_BUDGET_USD=${DAILY_BUDGET_USD})")

    if est_cost > DAILY_BUDGET_USD:
        print(f"[stop] estimate exceeds daily budget. Re-run with --limit N (try {int(DAILY_BUDGET_USD / COST_PER_IMAGE.get(args.model, 0.05))})")
        return 3
    if args.dry_run or RUN_MODE in {"dry-run", "mock"}:
        print("[dry-run] not calling Fal. Re-run with FTC_RUN_MODE=real after setting FAL_KEY.")
        return 0

    if not os.getenv("FAL_KEY"):
        print("[error] FAL_KEY not set. Add it to .env first.")
        return 4

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    fail = 0
    for i, c in enumerate(concepts, 1):
        prompt = c["fal_ai_visual_prompt"]
        try:
            blob = _call_fal(prompt, args.model)
            if not blob:
                raise RuntimeError("no image returned")
            (RENDER_DIR / f"{c['id']}.png").write_bytes(blob)
            ok += 1
            print(f"[{i}/{len(concepts)}] ok  {c['id']}")
        except Exception as exc:
            fail += 1
            print(f"[{i}/{len(concepts)}] fail {c['id']}: {exc}")
        time.sleep(0.4)  # gentle pacing

    print(f"\n[done] ok={ok}  fail={fail}  saved to {RENDER_DIR}")
    print("Re-run the catalog HTML to pick up the new renders.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
