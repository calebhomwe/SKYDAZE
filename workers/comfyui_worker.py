"""ComfyUI render worker.

Submits each FTC design to a running ComfyUI instance and saves the
photoreal render alongside its SVG. Optionally uses the SVG itself as a
ControlNet (Canny) hint so the rendered garment matches our flat exactly.

Why ComfyUI?  Self-hosted = $0 per image on your own GPU, ~$0.002 per
image on RunPod spot. See docs/COMFYUI.md for the cost matrix.

Usage:
    # If ComfyUI is on the same machine:
    python workers/comfyui_worker.py --section tracksuit --limit 20

    # If ComfyUI is on RunPod / remote:
    COMFY_URL=https://xxxxxx-8188.proxy.runpod.net \\
      python workers/comfyui_worker.py --section accessory --limit 50

    # With SVG-as-ControlNet (best fidelity to our silhouettes):
    python workers/comfyui_worker.py --controlnet --limit 5

    # Just plan, don't call:
    python workers/comfyui_worker.py --dry-run --limit 5
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ftc.config import ARTIFACTS  # noqa: E402

COLLECTION_DIR = ARTIFACTS / "collection_v1"
CONCEPTS_DIR = COLLECTION_DIR / "concepts"
SVG_DIR = COLLECTION_DIR / "svg"
RENDER_DIR = COLLECTION_DIR / "renders"

WORKFLOW_DIR = Path(__file__).resolve().parent.parent / "ops" / "comfyui"
WORKFLOW_FLAT = WORKFLOW_DIR / "workflow_ftc_flat.json"
WORKFLOW_CONTROLNET = WORKFLOW_DIR / "workflow_ftc_controlnet.json"

DEFAULT_COMFY_URL = os.getenv("COMFY_URL", "http://127.0.0.1:8188")
DEFAULT_WIDTH = 832
DEFAULT_HEIGHT = 1024
DEFAULT_STEPS = 28


def _designs_to_render(section: str | None, limit: int | None) -> list[dict]:
    if not CONCEPTS_DIR.exists():
        print(f"[error] {CONCEPTS_DIR} not found. Run: python generate_collection.py")
        sys.exit(2)
    out: list[dict] = []
    for path in sorted(CONCEPTS_DIR.glob("*.json")):
        c = json.loads(path.read_text())
        if section and not c["id"].lower().startswith(f"ftc-{section[:2].lower()}"):
            continue
        if (RENDER_DIR / f"{c['id']}.png").exists():
            continue  # idempotent
        out.append(c)
        if limit and len(out) >= limit:
            break
    return out


def _hydrate_workflow(template: dict, *, prompt: str, seed: int,
                      width: int, height: int, steps: int,
                      svg_png_path: Path | None) -> dict:
    """Substitute prompt / seed / size / optional ControlNet image into the
    workflow JSON. Looks for nodes whose meta.title contains a placeholder
    or whose inputs contain {{POSITIVE_PROMPT}} / {{SEED}} / {{WIDTH}} /
    {{HEIGHT}} / {{STEPS}} / {{CONTROLNET_IMAGE}} string."""
    wf = json.loads(json.dumps(template))
    for node in wf.values():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs", {})
        for k, v in list(inputs.items()):
            if not isinstance(v, str):
                continue
            v2 = (v
                  .replace("{{POSITIVE_PROMPT}}", prompt)
                  .replace("{{SEED}}", str(seed))
                  .replace("{{WIDTH}}", str(width))
                  .replace("{{HEIGHT}}", str(height))
                  .replace("{{STEPS}}", str(steps)))
            if svg_png_path is not None:
                v2 = v2.replace("{{CONTROLNET_IMAGE}}", svg_png_path.name)
            inputs[k] = v2
        # Also handle numeric placeholders stored as strings → convert
        for k in ("seed", "steps", "width", "height", "batch_size"):
            if k in inputs and isinstance(inputs[k], str) and inputs[k].isdigit():
                inputs[k] = int(inputs[k])
    return wf


def _post_prompt(comfy_url: str, workflow: dict, client_id: str) -> str:
    r = httpx.post(
        f"{comfy_url}/prompt",
        json={"prompt": workflow, "client_id": client_id},
        timeout=60.0,
    )
    r.raise_for_status()
    return r.json()["prompt_id"]


def _wait_for(comfy_url: str, prompt_id: str, poll_s: float = 1.5, timeout_s: float = 600) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = httpx.get(f"{comfy_url}/history/{prompt_id}", timeout=30.0)
        if r.status_code == 200:
            hist = r.json()
            if hist and prompt_id in hist:
                entry = hist[prompt_id]
                if entry.get("status", {}).get("completed"):
                    return entry
        time.sleep(poll_s)
    raise TimeoutError(f"comfy job {prompt_id} did not complete within {timeout_s}s")


def _download_outputs(comfy_url: str, history_entry: dict, target_id: str) -> Path | None:
    outputs = history_entry.get("outputs", {})
    for node_outputs in outputs.values():
        for img in node_outputs.get("images", []):
            filename = img["filename"]
            subfolder = img.get("subfolder", "")
            type_ = img.get("type", "output")
            r = httpx.get(
                f"{comfy_url}/view",
                params={"filename": filename, "subfolder": subfolder, "type": type_},
                timeout=120.0,
            )
            r.raise_for_status()
            RENDER_DIR.mkdir(parents=True, exist_ok=True)
            out = RENDER_DIR / f"{target_id}.png"
            out.write_bytes(r.content)
            return out
    return None


def _upload_svg_as_controlnet(comfy_url: str, design_id: str) -> Path | None:
    """Upload the SVG as a PNG to ComfyUI's /upload/image endpoint."""
    svg_path = SVG_DIR / f"{design_id}.svg"
    if not svg_path.exists():
        return None
    try:
        import cairosvg  # type: ignore
    except ImportError:
        print(
            "[warn] cairosvg not installed; skipping ControlNet hint. "
            "pip install cairosvg  to enable SVG→PNG conversion."
        )
        return None
    png_bytes = cairosvg.svg2png(bytestring=svg_path.read_bytes(),
                                  output_width=DEFAULT_WIDTH,
                                  output_height=DEFAULT_HEIGHT)
    upload_name = f"ftc_silhouette_{design_id}.png"
    files = {"image": (upload_name, png_bytes, "image/png")}
    r = httpx.post(f"{comfy_url}/upload/image", files=files, data={"overwrite": "true"},
                   timeout=60.0)
    r.raise_for_status()
    return Path(upload_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--section", choices=["tracksuit", "outerwear", "tee", "accessory"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--comfy-url", default=DEFAULT_COMFY_URL)
    parser.add_argument("--controlnet", action="store_true",
                        help="Use the SVG silhouette as a ControlNet hint (best fidelity)")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workflow_path = WORKFLOW_CONTROLNET if args.controlnet else WORKFLOW_FLAT
    if not workflow_path.exists():
        print(f"[error] workflow not found: {workflow_path}")
        return 2
    template = json.loads(workflow_path.read_text())

    designs = _designs_to_render(args.section, args.limit)
    print(f"[plan] ComfyUI url:  {args.comfy_url}")
    print(f"[plan] workflow:     {workflow_path.name}")
    print(f"[plan] designs:      {len(designs)}")
    print(f"[plan] dimensions:   {args.width}x{args.height} @ {args.steps} steps")

    if args.dry_run:
        print("[dry-run] not calling ComfyUI.")
        return 0

    # Probe Comfy
    try:
        httpx.get(f"{args.comfy_url}/system_stats", timeout=10).raise_for_status()
    except Exception as exc:
        print(f"[error] ComfyUI unreachable at {args.comfy_url}: {exc}")
        print("        Start it (`python main.py` in ComfyUI), or set --comfy-url")
        return 3

    client_id = str(uuid.uuid4())
    ok = 0
    fail = 0
    for i, c in enumerate(designs, 1):
        cn_path = _upload_svg_as_controlnet(args.comfy_url, c["id"]) if args.controlnet else None
        wf = _hydrate_workflow(
            template,
            prompt=c["fal_ai_visual_prompt"],
            seed=abs(hash(c["id"])) % (2**31),
            width=args.width,
            height=args.height,
            steps=args.steps,
            svg_png_path=cn_path,
        )
        try:
            prompt_id = _post_prompt(args.comfy_url, wf, client_id)
            entry = _wait_for(args.comfy_url, prompt_id)
            out = _download_outputs(args.comfy_url, entry, c["id"])
            if out:
                ok += 1
                print(f"[{i}/{len(designs)}] ok   {c['id']} → {out.name}")
            else:
                fail += 1
                print(f"[{i}/{len(designs)}] fail {c['id']}: no output")
        except Exception as exc:
            fail += 1
            print(f"[{i}/{len(designs)}] fail {c['id']}: {exc}")

    print(f"\n[done] ok={ok} fail={fail} → {RENDER_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
