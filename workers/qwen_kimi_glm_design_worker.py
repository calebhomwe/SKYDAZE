"""Qwen-VL3 + 22 Kimi + GLM 4.6 / GLM 4.5-Air design orchestrator.

Pipeline:
  1. 22 Kimi K2 agents (ftc/kimi_design_pod.py) fan out in parallel,
     each producing one design brief paragraph.
  2. GLM 4.6 (`z-ai/glm-4.6`) ranks the 22 briefs, selects top N.
  3. GLM 4.5-Air (`z-ai/glm-4.5-air`) runs the forbidden-term safety scan.
  4. Image generation — primary: OpenRouter GPT Image 2 (`openai/gpt-image-1`);
     fallback: Fal.ai Seedream-4. Each surviving brief gets rendered to
     a 4:5 (832x1024) PNG.
  5. Qwen VL3 (`qwen/qwen3-vl-235b-a22b-instruct`) reviews each PNG and
     writes brand-alignment scores to the manifest.

NO procedural SVG fallback. If no OPENROUTER_API_KEY: write a markdown
brief plan to artifacts/work_log/ and exit. No image generation without keys.

Usage:
  python3 workers/qwen_kimi_glm_design_worker.py --request-seed 2026
  FTC_RUN_MODE=real python3 workers/qwen_kimi_glm_design_worker.py --top 12

Override slugs:
  KIMI_MODEL=moonshotai/kimi-k2
  GLM_MODEL=z-ai/glm-4.6
  GLM_FAST_MODEL=z-ai/glm-4.5-air
  QWEN_VL_MODEL=qwen/qwen3-vl-235b-a22b-instruct
  IMAGE_MODEL_PRIMARY=openai/gpt-image-1
  IMAGE_MODEL_FALLBACK=fal-ai/bytedance/seedream/v4/text-to-image
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ftc.config import RUN_MODE
from ftc.kimi_design_pod import brainstorm

GLM_MODEL = os.getenv("GLM_MODEL", "z-ai/glm-4.6")
GLM_FAST_MODEL = os.getenv("GLM_FAST_MODEL", "z-ai/glm-4.5-air")
QWEN_VL_MODEL = os.getenv("QWEN_VL_MODEL", "qwen/qwen3-vl-235b-a22b-instruct")
IMAGE_MODEL_PRIMARY = os.getenv("IMAGE_MODEL_PRIMARY", "openai/gpt-image-1")
IMAGE_MODEL_FALLBACK = os.getenv("IMAGE_MODEL_FALLBACK", "fal-ai/bytedance/seedream/v4/text-to-image")


def _openrouter_chat(model: str, system: str, user: str, *, response_json: bool = True, timeout: int = 60) -> dict | None:
    """Single OpenRouter chat completion. Returns parsed JSON or None on error."""
    key = os.getenv("OPENROUTER_API_KEY", "")
    if not key:
        return None
    import httpx

    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.2,
    }
    if response_json:
        payload["response_format"] = {"type": "json_object"}
    try:
        resp = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content) if response_json else {"content": content}
    except Exception as e:
        print(f"[{model}] chat failed: {e}")
        return None


def glm_rank(briefs: list[dict[str, Any]], top_n: int) -> list[dict[str, Any]]:
    """GLM-4.6 ranks 22 briefs, returns top N."""
    if RUN_MODE in {"dry-run", "mock"} or not os.getenv("OPENROUTER_API_KEY"):
        return briefs[:top_n]
    system = """You are the FTC Brand Steward.
Score each brief on: luxury_score, theology_depth, brand_alignment (0-1 each).
Output JSON: {"ranked_ids": ["K-XX", "K-YY", ...]} - top first."""
    user = f"BRIEFS:\n{json.dumps([{k: b[k] for k in ('agent_id', 'angle', 'design_brief')} for b in briefs], indent=2)}\n\nReturn top {top_n} ranked by your scoring."
    out = _openrouter_chat(GLM_MODEL, system, user)
    if not out:
        return briefs[:top_n]
    ranked_ids = out.get("ranked_ids", [])
    order = {bid: i for i, bid in enumerate(ranked_ids)}
    return sorted(briefs, key=lambda b: order.get(b["agent_id"], 999))[:top_n]


def glm_safety_scan(briefs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """GLM-4.5-Air forbidden-term scan."""
    if RUN_MODE in {"dry-run", "mock"} or not os.getenv("OPENROUTER_API_KEY"):
        return briefs
    system = (
        "You are the Forbidden Term Scanner. Forbidden: skulls, neon, "
        "crosses-as-decoration, direct verse citations like 'John 3:16', "
        "Comic Sans, cartoon aesthetics, performative Christianity, "
        "fast-fashion promo language. "
        'Output JSON: {"results": [{"agent_id": "K-XX", "is_safe": true}]}'
    )
    user = f"BRIEFS:\n{json.dumps([{k: b[k] for k in ('agent_id', 'design_brief')} for b in briefs], indent=2)}"
    out = _openrouter_chat(GLM_FAST_MODEL, system, user)
    if not out:
        return briefs
    safe_ids = {r["agent_id"] for r in out.get("results", []) if r.get("is_safe", True)}
    return [b for b in briefs if b["agent_id"] in safe_ids]


def render_via_gpt_image_2(prompt: str) -> bytes | None:
    """Primary path — OpenRouter GPT Image 2."""
    key = os.getenv("OPENROUTER_API_KEY", "")
    if not key:
        return None
    import httpx

    try:
        resp = httpx.post(
            "https://openrouter.ai/api/v1/images/generations",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/calebhomwe/SKYDAZE",
                "X-Title": "FTC FULL TIME CHRISTIAN",
            },
            json={
                "model": IMAGE_MODEL_PRIMARY,
                "prompt": prompt,
                "size": "832x1024",
                "n": 1,
            },
            timeout=180,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            return None
        first = data[0]
        if first.get("b64_json"):
            return base64.b64decode(first["b64_json"])
        if first.get("url"):
            return httpx.get(first["url"], timeout=60).content
    except Exception as e:
        print(f"[GPT Image 2] failed: {e}")
    return None


def render_via_seedream(prompt: str) -> bytes | None:
    """Fallback path — Fal.ai Seedream-4."""
    fal_key = os.getenv("FAL_KEY", "")
    if not fal_key:
        return None
    import httpx

    try:
        resp = httpx.post(
            f"https://fal.run/{IMAGE_MODEL_FALLBACK}",
            headers={"Authorization": f"Key {fal_key}", "Content-Type": "application/json"},
            json={
                "prompt": prompt,
                "image_size": {"width": 832, "height": 1024},
                "num_images": 1,
                "enable_safety_checker": True,
            },
            timeout=180,
        )
        resp.raise_for_status()
        images = resp.json().get("images", [])
        if not images:
            return None
        url = images[0].get("url")
        if url:
            return httpx.get(url, timeout=60).content
    except Exception as e:
        print(f"[Seedream] failed: {e}")
    return None


def render_brief(brief: dict[str, Any], idx: int, out_dir: Path) -> tuple[Path | None, str]:
    """Render via primary, fallback to Seedream. Returns (path, provider_name)."""
    prompt = brief["design_brief"]
    img = render_via_gpt_image_2(prompt)
    provider = IMAGE_MODEL_PRIMARY
    if not img:
        img = render_via_seedream(prompt)
        provider = IMAGE_MODEL_FALLBACK
    if not img:
        return None, "no-image-no-key"
    headline_slug = (brief.get("headline_text") or brief["agent_name"]).lower()
    safe_slug = "".join(c if c.isalnum() else "-" for c in headline_slug)[:40].strip("-")
    path = out_dir / f"ftc-kimi-{idx:03d}-{brief['agent_id']}-{safe_slug}.png"
    path.write_bytes(img)
    return path, provider


def qwen_review(path: Path) -> dict[str, Any]:
    """Qwen VL3 review on a rendered image."""
    key = os.getenv("OPENROUTER_API_KEY", "")
    if not key or not path.exists():
        return {"source": "skipped"}
    import httpx

    img_b64 = base64.b64encode(path.read_bytes()).decode()
    system = "Score this FTC graphic tee image on luxury_score, theology_depth, brand_alignment (0-1 each). JSON only."
    try:
        resp = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": QWEN_VL_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Score this image."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    ]},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1,
            },
            timeout=90,
        )
        resp.raise_for_status()
        scores = json.loads(resp.json()["choices"][0]["message"]["content"])
        scores["source"] = QWEN_VL_MODEL
        return scores
    except Exception as e:
        return {"source": "error", "error": str(e)}


def write_dry_run_plan(briefs: list[dict[str, Any]]) -> Path:
    """When no keys present, write a markdown plan instead of generating images."""
    plan_path = Path("artifacts/work_log") / "kimi_glm_qwen_plan.md"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Qwen-VL3 + 22 Kimi + GLM 4.6/4.5-Air → GPT Image 2 / Seedream-4 (DRY-RUN PLAN)",
        "",
        "This file is produced when `OPENROUTER_API_KEY` is absent. It shows",
        "exactly what the worker would do if the key were set.",
        "",
        "## Pipeline",
        "1. **22 Kimi K2 agents** brainstorm in parallel → 22 design briefs",
        "2. **GLM 4.6** ranks the 22 briefs → top N",
        "3. **GLM 4.5-Air** runs forbidden-term safety scan",
        f"4. **{IMAGE_MODEL_PRIMARY}** generates 4:5 PNGs (832x1024)",
        f"5. Fallback if primary fails: **{IMAGE_MODEL_FALLBACK}**",
        f"6. **{QWEN_VL_MODEL}** reviews each PNG for brand alignment",
        "",
        f"## To run for real",
        "```bash",
        "export OPENROUTER_API_KEY=sk-or-...    # required",
        "export FAL_KEY=...                      # optional (Seedream fallback)",
        "FTC_RUN_MODE=real python3 workers/qwen_kimi_glm_design_worker.py",
        "```",
        "",
        "## The 22 briefs that would be submitted right now (dry-run stubs)",
        "",
        "| # | Agent | Angle | Brief seed |",
        "| ---: | :--- | :--- | :--- |",
    ]
    for i, b in enumerate(briefs):
        brief_preview = b.get("design_brief", "")[:140].replace("|", "\\|")
        lines.append(f"| {i+1} | `{b['agent_id']}` {b['agent_name']} | {b['angle']} | {brief_preview} |")
    plan_path.write_text("\n".join(lines))
    return plan_path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--request-seed", type=int, default=2026)
    p.add_argument("--top", type=int, default=12, help="How many to render after GLM ranking")
    p.add_argument("--review", action="store_true", help="Run Qwen VL3 review on each render")
    args = p.parse_args()

    print(f"[1/5] 22 Kimi briefs (seed={args.request_seed})...")
    briefs = brainstorm(request_seed=args.request_seed)
    print(f"      Got {len(briefs)} briefs ({briefs[0]['source']}).")

    # If no key, write the plan and exit honestly.
    if not os.getenv("OPENROUTER_API_KEY") or RUN_MODE in {"dry-run", "mock"}:
        plan_path = write_dry_run_plan(briefs)
        print(f"\n[no-key] OPENROUTER_API_KEY not set or FTC_RUN_MODE=dry-run.")
        print(f"         Wrote plan: {plan_path}")
        print(f"         Set OPENROUTER_API_KEY (and FAL_KEY for Seedream) and rerun for real renders.")
        return

    print(f"[2/5] GLM-4.6 rank → top {args.top}...")
    ranked = glm_rank(briefs, top_n=args.top)
    print(f"      Selected {len(ranked)}.")

    print(f"[3/5] GLM-4.5-Air safety scan...")
    safe = glm_safety_scan(ranked)
    print(f"      {len(safe)}/{len(ranked)} passed.")

    out_dir = Path("artifacts/graphics-kimi")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[4/5] Rendering via {IMAGE_MODEL_PRIMARY} (fallback: {IMAGE_MODEL_FALLBACK})...")
    manifest: list[dict] = []
    for i, brief in enumerate(safe):
        path, provider = render_brief(brief, i, out_dir)
        entry = dict(brief)
        entry["render_path"] = str(path) if path else None
        entry["render_provider"] = provider
        if args.review and path:
            entry["qwen_review"] = qwen_review(path)
        manifest.append(entry)
        status = path.name if path else "FAILED (no provider)"
        print(f"      [{i+1}/{len(safe)}] {provider:<46}  {status}")
        time.sleep(0.5)

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    log = Path("artifacts/work_log") / "kimi_glm_qwen_run.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Qwen-VL3 + 22 Kimi + GLM 4.6/4.5-Air → GPT Image 2 / Seedream-4 run",
        "",
        f"Request seed: {args.request_seed}",
        f"Kimi: {os.getenv('KIMI_MODEL', 'moonshotai/kimi-k2')} (22 agents)",
        f"GLM rank: {GLM_MODEL}",
        f"GLM safety: {GLM_FAST_MODEL}",
        f"Image primary: {IMAGE_MODEL_PRIMARY}",
        f"Image fallback: {IMAGE_MODEL_FALLBACK}",
        f"VL review: {QWEN_VL_MODEL if args.review else 'skipped'}",
        "",
        "| # | Agent | Provider | Render | Review |",
        "| ---: | :--- | :--- | :--- | :--- |",
    ]
    for i, entry in enumerate(manifest):
        ok = "✓" if entry.get("render_path") else "✗"
        review = entry.get("qwen_review", {}).get("brand_alignment", "—")
        lines.append(f"| {i+1} | {entry['agent_name']} | {entry['render_provider']} | {ok} | {review} |")
    log.write_text("\n".join(lines))

    print(f"\nDone. {sum(1 for m in manifest if m.get('render_path'))} images, {len(safe) - sum(1 for m in manifest if m.get('render_path'))} failed.")
    print(f"Manifest: {out_dir / 'manifest.json'}")
    print(f"Work log: {log}")


if __name__ == "__main__":
    main()
