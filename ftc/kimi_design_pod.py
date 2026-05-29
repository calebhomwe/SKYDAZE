"""Kimi K2 design brainstorm pod — 22 named agents, each a different angle.

Each agent emits a design BRIEF — natural-language description of the
graphic-tee design they advocate. Briefs feed into GLM ranking, then
image generation (OpenRouter GPT Image 2 / Fal.ai Seedream-4).

Real mode: parallel calls to moonshotai/kimi-k2 via OpenRouter.
Dry-run mode: deterministic curated briefs from each persona's seed.

Per master context Section 2, BoohooMAN informs men's pacing and
composition ONLY — FTC silhouette + material + non-fast-fashion ethic
remain non-negotiable. Two of the 22 agents are explicitly BoohooMAN-
men's-reference focused.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from .config import RUN_MODE

KIMI_MODEL = os.getenv("KIMI_MODEL", "moonshotai/kimi-k2")


@dataclass(frozen=True)
class KimiAgent:
    id: str
    name: str
    angle: str
    # A short content brief seed used for the prompt + dry-run fallback
    persona_brief: str


KIMI_POD: tuple[KimiAgent, ...] = (
    KimiAgent("K-01", "kimi-hymn-fragmentarian",
              "Hymn fragments at Sermon volume",
              "Pull a 2-4 word fragment from Wesley/Watts/Newton hymns; "
              "set in heavyweight serif at maximum scale; bone or onyx ground."),
    KimiAgent("K-02", "kimi-augustine-curator",
              "Augustine Confessions as graphic tee",
              "Quote Augustine in fragment form (e.g. 'LATE HAVE I LOVED THEE'); "
              "hand-drawn marker treatment; CPFM naive-hand aesthetic; bone ground."),
    KimiAgent("K-03", "kimi-greek-typographer",
              "Greek NT words as decorative type",
              "Single Greek word ΑΓΑΠΗ/ΛΟΓΟΣ/ΧΑΡΙΣ; massive grotesque weight; "
              "Cey Adams 3-color discipline; onyx ground."),
    KimiAgent("K-04", "kimi-hebrew-typographer",
              "Hebrew words at high contrast",
              "Single Hebrew word שלום/חסד/אמונה; bold serif; "
              "Eric Haze graffiti weight without graffiti; bone ground."),
    KimiAgent("K-05", "kimi-latin-formalist",
              "Latin phrases in Trajan register",
              "Latin phrase (SOLI DEO GLORIA, LUX MUNDI, PAX VOBISCUM); "
              "Trajan or Cinzel; circular emblem composition (Sk8thing); bone ground."),
    KimiAgent("K-06", "kimi-diaspora-place-marker",
              "Diaspora cities as primary content",
              "Diaspora city name (DMV, BROOKLYN, PECKHAM, LAGOS); "
              "tour-poster layout (Awake NY); secondary line lists dates; onyx ground."),
    KimiAgent("K-07", "kimi-historical-figure",
              "Historical Christian figures",
              "Name of historical figure (AUGUSTINE, BONHOEFFER, TUBMAN, THURMAN, DAY); "
              "halftone-portrait Pyer Moss aesthetic; bone ground."),
    KimiAgent("K-08", "kimi-trinitarian-stacker",
              "Trinitarian three-line phrases",
              "Trinitarian stack (FATHER/SON/SPIRIT; MERCY/GRACE/PEACE); "
              "Cey Adams three-line stack discipline; onyx ground."),
    KimiAgent("K-09", "kimi-cpfm-naive-hand",
              "CPFM naive-hand discipline",
              "Single hymn or Augustine fragment; deliberately wonky hand-drawn type; "
              "marker scribble accents; bone ground; CPFM grade."),
    KimiAgent("K-10", "kimi-cey-adams-bold",
              "Cey Adams 3-color discipline",
              "Single Greek word centered; massive Helvetica Black; "
              "max 3 colors total; onyx ground."),
    KimiAgent("K-11", "kimi-eric-haze-graffiti",
              "Eric Haze graffiti weight without graffiti",
              "Single Hebrew or Greek word at Impact 240pt with subtle drips; "
              "no actual graffiti; bone ground."),
    KimiAgent("K-12", "kimi-sk8thing-emblem",
              "Sk8thing layered-emblem aesthetic",
              "Circular emblem with Latin phrase wrapping; "
              "Trajan inside; BAPE album-cover composition; onyx ground."),
    KimiAgent("K-13", "kimi-brain-dead-halftone",
              "Brain Dead halftone print discipline",
              "Halftone dot field suggesting a portrait; Latin or Greek caption; "
              "newspaper register; bone ground."),
    KimiAgent("K-14", "kimi-heron-preston-industrial",
              "Heron Preston industrial typography",
              "Vertical wheatpaste panel with Latin phrase; Impact 180pt; "
              "torn-edge marks; onyx ground."),
    KimiAgent("K-15", "kimi-awake-ny-tour-poster",
              "Awake NY tour-poster discipline",
              "Hymn fragment as tour headline; city list below; "
              "thin horizontal rules; bone ground."),
    KimiAgent("K-16", "kimi-pyer-moss-essay-tee",
              "Pyer Moss historical-essay tee",
              "Historical figure name + their tradition (AUGUSTINIAN/METHODIST/MYSTIC); "
              "halftone portrait above; bone ground."),
    KimiAgent("K-17", "kimi-verdy-single-motif",
              "Verdy single-motif discipline",
              "One symbol (LAMP, VINE, STONE, OLIVE); hand-drawn; "
              "wonky caption below; bone ground."),
    KimiAgent("K-18", "kimi-illuminated-mss",
              "Medieval illuminated manuscript reference",
              "Illuminated capital + Augustine quote in Cinzel; "
              "decorative border; bone ground."),
    KimiAgent("K-19", "kimi-shout-tier-maximalist",
              "Maximum intensity all-over-print",
              "Greek or Hebrew word repeated 45+ times across the field; "
              "hero block over the top; onyx ground."),
    KimiAgent("K-20", "kimi-quiet-statement",
              "Statement tier at the quiet end",
              "Three-line trinitarian phrase; sparse layout; "
              "thin underscore mark; bone ground."),
    # BoohooMAN men's reference (Section 2 master context — pacing/composition only)
    KimiAgent("K-21", "kimi-boohooman-mens-headline",
              "BoohooMAN men's editorial headline pacing — restraint palette",
              "Drop headline composition: top eyebrow rule, hero word at "
              "Impact 240pt, accent slash, sub-line, bottom rule with city "
              "roster. BoohooMAN editorial pacing applied to FTC. "
              "Onyx ground, bone type. NEVER fast-fashion silhouette or "
              "promo-discount language."),
    KimiAgent("K-22", "kimi-boohooman-photo-overlay",
              "BoohooMAN men's photo-overlay pacing — abstracted figure",
              "Composition: top brand bar, suggested figure (halftone dot "
              "column, no actual photography), bottom hero word slab. "
              "BoohooMAN editorial 'model + headline' composition rhythm "
              "borrowed; FTC material standards preserved. Onyx ground."),
)


def _seed_for(agent: KimiAgent) -> int:
    return int(hashlib.sha256(agent.id.encode()).hexdigest()[:8], 16)


def _dry_run_brief(agent: KimiAgent, request_seed: int) -> dict[str, Any]:
    """Deterministic brief — used when no OPENROUTER_API_KEY."""
    rng = random.Random(_seed_for(agent) ^ request_seed)
    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "angle": agent.angle,
        "design_brief": agent.persona_brief,
        "seed": _seed_for(agent) ^ request_seed,
        "source": "dry-run-stub",
    }


def _real_brief(agent: KimiAgent, request_seed: int, openrouter_key: str) -> dict[str, Any]:
    """Real Kimi K2 brief via OpenRouter."""
    import httpx

    system_prompt = f"""You are {agent.name}, one of 22 design agents in the
FTC FULL TIME CHRISTIAN brand pipeline.

YOUR ANGLE: {agent.angle}
YOUR PERSONA BRIEF: {agent.persona_brief}

BRAND CONSTITUTION (from FTC_MASTER_CONTEXT.md):
- Luxury Christian streetwear, $80-280 MSRP
- Restraint palette: bone #EFE9D8, ash #8C8782, slate #3D3B36, onyx #15110D, accents under 0.55 saturation
- 320 gsm heavyweight cotton blanks
- BoohooMAN reference: pacing and composition ONLY, never fast-fashion ethic
- Forbidden: skulls, neon, crosses-as-decoration, direct verse citations, cartoon aesthetics, Comic Sans, performative Christianity

YOUR TASK: produce ONE graphic-tee design brief suitable for direct submission
to an image generation model (GPT Image 2 or Seedream-4). The brief is a
natural-language paragraph (60-140 words) describing the final tee image.

Required elements:
- Garment: specify "heavyweight 320 gsm cotton tee, garment-washed"
- Background: pure black studio OR pure white studio (alternate per brief)
- Composition: specify hero-text placement, secondary text, decorative marks
- Typography: name the typeface family register (humanist serif / grotesque / mono / hand-drawn marker / Impact display / Trajan)
- Color palette: 2-3 hex codes from FTC restraint palette
- Photographic treatment: editorial product shot, soft north window light, 4:5 aspect

Output ONLY a JSON object:
{{
  "design_brief": "<paragraph>",
  "headline_text": "<the main word/phrase that appears on the tee>",
  "background": "<black or white>",
  "intensity_tier": "<3-Statement, 4-Sermon, or 5-Shout>"
}}
"""

    try:
        resp = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/calebhomwe/SKYDAZE",
                "X-Title": "FTC FULL TIME CHRISTIAN",
            },
            json={
                "model": KIMI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Request seed: {request_seed}. Produce one brief now."},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.85,
            },
            timeout=60,
        )
        resp.raise_for_status()
        parsed = json.loads(resp.json()["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"[{agent.id}] Kimi call failed: {e} → dry-run fallback")
        return _dry_run_brief(agent, request_seed)

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "angle": agent.angle,
        "design_brief": parsed.get("design_brief", agent.persona_brief),
        "headline_text": parsed.get("headline_text", ""),
        "background": parsed.get("background", "white"),
        "intensity_tier": parsed.get("intensity_tier", "4-Sermon"),
        "seed": _seed_for(agent) ^ request_seed,
        "source": KIMI_MODEL,
    }


def brainstorm(request_seed: int = 0, parallel: int = 8) -> list[dict[str, Any]]:
    """Fan out 22 Kimi agents in parallel. Returns 22 design briefs."""
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    use_real = RUN_MODE not in {"dry-run", "mock"} and bool(openrouter_key)

    if not use_real:
        return [_dry_run_brief(a, request_seed) for a in KIMI_POD]

    results: list[dict[str, Any] | None] = [None] * len(KIMI_POD)
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        futures = {
            pool.submit(_real_brief, agent, request_seed, openrouter_key): i
            for i, agent in enumerate(KIMI_POD)
        }
        for future in as_completed(futures):
            i = futures[future]
            try:
                results[i] = future.result()
            except Exception as e:
                print(f"[K-{i+1:02d}] failed: {e}")
                results[i] = _dry_run_brief(KIMI_POD[i], request_seed)
    return [r for r in results if r is not None]


if __name__ == "__main__":
    briefs = brainstorm(request_seed=2026)
    print(f"Got {len(briefs)} briefs:\n")
    for b in briefs:
        print(f"{b['agent_id']:>5}  {b['agent_name']:<32}  ({b['source']})")
