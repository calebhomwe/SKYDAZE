"""Strict JSON schema for concept artifacts (Section 4)."""

from __future__ import annotations

from jsonschema import Draft202012Validator

CONCEPT_SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "FTC Concept",
    "type": "object",
    "required": [
        "id",
        "title",
        "theological_core",
        "aesthetic_direction",
        "typography_layout",
        "color_palette",
        "print_technique",
        "fal_ai_visual_prompt",
        "novita_video_prompt",
        "nano_banana_mockup_prompt",
        "reference_source_tags",
        "promo_hook",
    ],
    "additionalProperties": False,
    "properties": {
        "id": {"type": "string", "pattern": r"^FTC-\d{3,4}$"},
        "title": {"type": "string", "minLength": 1, "maxLength": 64},
        "theological_core": {"type": "string", "minLength": 1, "maxLength": 280},
        "aesthetic_direction": {"type": "string", "minLength": 1},
        "typography_layout": {"type": "string", "minLength": 1},
        "color_palette": {
            "type": "array",
            "minItems": 2,
            "maxItems": 5,
            "items": {"type": "string", "pattern": r"^#[0-9A-Fa-f]{6}$"},
        },
        "print_technique": {"type": "string", "minLength": 1},
        "fal_ai_visual_prompt": {"type": "string", "minLength": 1},
        "novita_video_prompt": {"type": "string", "minLength": 1},
        "nano_banana_mockup_prompt": {"type": "string", "minLength": 1},
        "reference_source_tags": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string"},
        },
        "promo_hook": {"type": "string", "minLength": 1},
    },
}

_validator = Draft202012Validator(CONCEPT_SCHEMA)


def validate(concept: dict) -> list[str]:
    """Return a list of human-readable error strings; empty list if valid."""
    return [
        f"{'.'.join(str(p) for p in err.path) or '<root>'}: {err.message}"
        for err in _validator.iter_errors(concept)
    ]
