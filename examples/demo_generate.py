"""Demo: generate a design concept via the live OpenRouter API."""

import asyncio
import json
import sys

from ftc.config import load_config, validate_no_forbidden
from ftc.pipeline import ConceptGenerator


async def main() -> int:
    config = load_config()
    gen = ConceptGenerator(config, model="deepseek/deepseek-chat")

    prompt = (
        "Generate one FTC FULL TIME CHRISTIAN luxury streetwear concept. "
        "Theme: 'Living Water' — grace as an inexhaustible hidden wellspring. "
        "Use muted indigo/white palette, fluid ink wash textures, discharge print technique. "
        "You MUST output a JSON object with EXACTLY these fields:\n"
        '{"id": "FTC-101", "title": "string", '
        '"theological_core": "1-sentence abstract doctrine", '
        '"aesthetic_direction": "style + mood notes", '
        '"typography_layout": "font treatment + placement", '
        '"color_palette": ["#HEX1", "#HEX2", "#HEX3"], '
        '"print_technique": "technique name", '
        '"fal_ai_visual_prompt": "image gen prompt for Seedream 4.0, 4:5 AR", '
        '"novita_video_prompt": "5-10s motion prompt", '
        '"nano_banana_mockup_prompt": "mockup directive", '
        '"reference_source_tags": ["tag1", "tag2"], '
        '"promo_hook": "caption + platform + audio"}\n'
        "Return ONLY this JSON object, no extra keys."
    )

    print("Generating concept via OpenRouter (DeepSeek-V3)...")
    try:
        raw = await gen.generate(prompt)
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1

    print("\n--- Raw API response ---")
    print(json.dumps(raw, indent=2))

    print("\n--- Validation ---")
    try:
        concept = gen.validate_concept(raw)
        print(f'✓ Valid concept: {concept.id} — "{concept.title}"')
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return 1

    violations = validate_no_forbidden(
        f"{concept.title} {concept.theological_core} {concept.aesthetic_direction}"
    )
    if violations:
        print(f"✗ Forbidden terms: {violations}")
        return 1
    print("✓ No forbidden terms")

    score = gen.score_concept(concept)
    print("\n--- Quality Gate ---")
    print(f"  Luxury:   {score.luxury_score}")
    print(f"  Theology: {score.theology_depth}")
    result = "✓ PASS" if score.passes_auto else "⚠ REVIEW" if score.needs_review else "✗ KILL"
    print(f"  Result:   {result}")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
