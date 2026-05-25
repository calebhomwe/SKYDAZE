"""Concept generation (agents FTC-006, FTC-008, FTC-009, FTC-026).

Produces concept JSON objects that satisfy the Section 4 schema.
Real mode calls OpenRouter (DeepSeek-V3) for the theological core and
aesthetic direction. Dry-run mode emits hand-crafted exemplar concepts
so the pipeline can be exercised without a key.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .config import RUN_MODE, require

CONCEPT_SYSTEM_PROMPT = """You are the Theology Concept Architect of FTC FULL TIME CHRISTIAN.

Before writing, internalize FTC_MASTER_CONTEXT.md (Sections 1, 2, 4, 5).

You will receive a brief (drop theme + reference synthesis). Return EXACTLY
one JSON object conforming to the Section 4 schema:

{
  "id": "FTC-XXX",
  "title": "1-3 word title",
  "theological_core": "1 sentence of abstract doctrine/metaphor (no verse citation)",
  "aesthetic_direction": "1-2 sentences: mood, composition, material posture",
  "typography_layout": "Font treatment, placement, hierarchy",
  "color_palette": ["#hex1", "#hex2", "#hex3"],
  "print_technique": "Screen | Puff | Embroidery | Tonal | Discharge | Deboss",
  "fal_ai_visual_prompt": "Seedream 4.0 prompt at 4:5 AR with luxury cues",
  "novita_video_prompt": "5-10s motion brief",
  "nano_banana_mockup_prompt": "Garment template integration directive",
  "reference_source_tags": ["stampd", "pinterest_abstract", "kittl_typography"],
  "promo_hook": "Caption tone + platform + audio suggestion"
}

Constraints:
- No literal verse references. No skulls, crosses-as-props, neon, cartoon, fast-fashion.
- 2-5 hex codes; muted, earth, monochrome. No saturation above 70%.
- 280-320gsm cotton implied in the visual prompt.
- Restraint is the brand.
"""


_STUB_CONCEPTS: list[dict[str, Any]] = [
    {
        "id": "FTC-001",
        "title": "Cornerstone",
        "theological_core": "What the builders refused becomes the angle that holds the wall.",
        "aesthetic_direction": "Heavyweight overcast drape; one tonal mark at the chest, hidden interior text at the side seam; mood of slow architecture.",
        "typography_layout": "Worn humanist serif, 14pt tonal embroidery, centered upper chest; interior screen at side seam.",
        "color_palette": ["#1E1B17", "#A89B86", "#E8E2D3"],
        "print_technique": "Tonal embroidery",
        "fal_ai_visual_prompt": "Editorial product shot of a heavyweight 300gsm garment-washed cotton drop-shoulder tee in bone, soft tonal embroidery on chest, north window light, concrete backdrop, 4:5 aspect ratio, restrained luxury streetwear, Lemaire mood",
        "novita_video_prompt": "5s clip: slow tilt down a draped tee on a wooden hanger, light shifts from cold to warm ember, fabric settles into stillness",
        "nano_banana_mockup_prompt": "Apply tonal embroidery (40wt thread, density 0.6) to drop-shoulder tee template in bone; thread color #A89B86; chest center placement",
        "reference_source_tags": ["lemaire", "stampd_silhouette", "monastic_drape"],
        "promo_hook": "Caption: museum-label cadence. Instagram reel with field-recording ambient.",
    },
    {
        "id": "FTC-002",
        "title": "Veil",
        "theological_core": "Light reveals only what shadow has agreed to release.",
        "aesthetic_direction": "Heavyweight crew with translucent overlay reading at thread-level; composition reads at thumbnail; negative space at lower chest.",
        "typography_layout": "Display grotesque, 9pt deboss at left chest; no center mark.",
        "color_palette": ["#0E0D0C", "#3B362F", "#7C736A"],
        "print_technique": "Deboss",
        "fal_ai_visual_prompt": "Editorial close-up of a 300gsm garment-washed cotton crew in ink, subtle deboss at left chest, single overhead key light, plaster wall, 4:5 aspect ratio, FOG essentials silhouette, quiet luxury",
        "novita_video_prompt": "7s clip: hand lifts the hem; light grazes across deboss; cut to stillness",
        "nano_banana_mockup_prompt": "Apply 0.4mm deboss to crew template in ink; left chest placement; matte finish",
        "reference_source_tags": ["fog_essentials", "pinterest_abstract", "ssense_edit"],
        "promo_hook": "Caption: two-line fragment. Instagram still with sub-bass drone.",
    },
    {
        "id": "FTC-003",
        "title": "Living Water",
        "theological_core": "The well does not argue; it overflows.",
        "aesthetic_direction": "Garment-washed long-sleeve, water-blue undertone in palette, single puff-print mark resembling ripple geometry at sleeve.",
        "typography_layout": "Sans grotesque, 12pt puff, lower sleeve, parallel to seam.",
        "color_palette": ["#0F1416", "#5C7480", "#D7DDE0"],
        "print_technique": "Puff",
        "fal_ai_visual_prompt": "Editorial product shot of a 300gsm garment-washed long-sleeve in slate with subtle ripple geometry puff print at left sleeve, soft north light, concrete bench, 4:5 aspect ratio, quiet luxury streetwear, Lemaire restraint",
        "novita_video_prompt": "8s clip: water droplet hits fabric, drape shifts almost imperceptibly, lighting cools",
        "nano_banana_mockup_prompt": "Apply puff print (1.2mm raise) to long-sleeve template in slate; left sleeve, lower placement; tonal color #D7DDE0",
        "reference_source_tags": ["pinterest_abstract", "stampd_silhouette", "monastic_drape"],
        "promo_hook": "Caption: one-line image. TikTok still with field-recording water.",
    },
    {
        "id": "FTC-004",
        "title": "Ember",
        "theological_core": "What remains after the fire is heavier than what burned.",
        "aesthetic_direction": "Heavyweight hoodie, single tonal embroidery at hem reading like a ledger entry; mood of cooling iron.",
        "typography_layout": "Mono with humanist hand-feel, 10pt embroidery, hem inside-out style.",
        "color_palette": ["#1A1411", "#3A2A22", "#8A6E5C"],
        "print_technique": "Tonal embroidery",
        "fal_ai_visual_prompt": "Editorial close-up of a 320gsm garment-washed cotton hoodie in oxidized rust, tonal embroidery at hem, ember-temperature key light, brick texture distant, 4:5 aspect ratio, luxury streetwear",
        "novita_video_prompt": "6s clip: light slowly shifts from amber to ash; fabric stays still",
        "nano_banana_mockup_prompt": "Apply tonal embroidery (40wt thread) to hoodie hem template; rust colorway #8A6E5C; hem inside-out placement",
        "reference_source_tags": ["fog_essentials", "stampd_silhouette", "pinterest_abstract"],
        "promo_hook": "Caption: object-noun fragment. Instagram reel with drone synth and field crackle.",
    },
    {
        "id": "FTC-005",
        "title": "Threshold",
        "theological_core": "A door knows both rooms; it belongs to neither.",
        "aesthetic_direction": "Heavyweight tee with a horizontal puff line dividing chest into upper and lower fields; restraint as the design.",
        "typography_layout": "Type-free composition; the mark is geometric.",
        "color_palette": ["#11100E", "#5F574E", "#C8BFB1"],
        "print_technique": "Puff",
        "fal_ai_visual_prompt": "Editorial product shot of a 300gsm garment-washed cotton tee in bone, single horizontal puff line dividing chest, soft overhead light, plaster wall, 4:5 aspect ratio, Lemaire restraint, FOG silhouette",
        "novita_video_prompt": "5s clip: model stands still in doorway, light shifts across the chest line",
        "nano_banana_mockup_prompt": "Apply 1mm puff line horizontally across chest of tee template in bone; tonal color #5F574E; precise center placement",
        "reference_source_tags": ["pinterest_abstract", "lemaire", "ssense_edit"],
        "promo_hook": "Caption: silence with one word. Instagram still with ambient drone.",
    },
]


def generate_stub(n: int) -> list[dict[str, Any]]:
    """Return n hand-crafted exemplar concepts (clamped to available stubs)."""
    return [json.loads(json.dumps(c)) for c in _STUB_CONCEPTS[:n]]


def generate_via_openrouter(n: int, drop_brief: str, synthesis: dict) -> list[dict[str, Any]]:
    from openai import OpenAI

    client = OpenAI(
        api_key=require("openrouter"),
        base_url="https://openrouter.ai/api/v1",
    )

    user_msg = (
        f"DROP BRIEF:\n{drop_brief}\n\n"
        f"REFERENCE SYNTHESIS (top clusters):\n{json.dumps(synthesis.get('clusters', [])[:5], indent=2)}\n\n"
        f"Produce {n} distinct concepts. Return a JSON array of {n} objects matching the schema."
    )

    resp = client.chat.completions.create(
        model="deepseek/deepseek-chat",  # OpenRouter slug for DeepSeek-V3
        messages=[
            {"role": "system", "content": CONCEPT_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    content = resp.choices[0].message.content or "[]"
    parsed = json.loads(content)
    if isinstance(parsed, dict) and "concepts" in parsed:
        return parsed["concepts"]
    if isinstance(parsed, list):
        return parsed
    raise ValueError("OpenRouter returned unexpected payload shape")


def generate(n: int, drop_brief: str, synthesis: dict) -> list[dict[str, Any]]:
    if RUN_MODE in {"dry-run", "mock"} or not os.getenv("OPENROUTER_API_KEY"):
        return generate_stub(n)
    return generate_via_openrouter(n, drop_brief, synthesis)
