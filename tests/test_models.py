"""Tests for the FTC design concept models and quality gates."""

import pytest
from pydantic import ValidationError

from ftc.models import DesignConcept, QualityScore

VALID_CONCEPT = {
    "id": "FTC-001",
    "title": "Cornerstone",
    "theological_core": "Christ as the rejected stone that became the foundation",
    "aesthetic_direction": "Muted earth tones, architectural composition, heavyweight drape",
    "typography_layout": "Distressed serif at center chest, tonal secondary text at hem",
    "color_palette": ["#2C2C2C", "#A89F91", "#F5F0EB"],
    "print_technique": "Tonal embroidery + discharge print",
    "fal_ai_visual_prompt": (
        "Luxury heavyweight cotton tee, muted earth palette, abstract stone texture, "
        "architectural draping, editorial lighting, 4:5 AR"
    ),
    "novita_video_prompt": "5s slow pan, fabric physics on heavyweight cotton, warm diffused light",
    "nano_banana_mockup_prompt": "Apply to relaxed-fit heavyweight tee, drop shoulder, front chest",
    "reference_source_tags": ["stampd", "pinterest_abstract", "kittl_typography"],
    "promo_hook": "Instagram Reels — ambient minimal audio — 'Built different. Built on rock.'",
}


def test_valid_concept():
    concept = DesignConcept.model_validate(VALID_CONCEPT)
    assert concept.id == "FTC-001"
    assert concept.title == "Cornerstone"
    assert len(concept.color_palette) == 3


def test_concept_requires_ftc_id():
    bad = {**VALID_CONCEPT, "id": "BAD-001"}
    with pytest.raises(ValidationError):
        DesignConcept.model_validate(bad)


def test_concept_requires_colors():
    bad = {**VALID_CONCEPT, "color_palette": []}
    with pytest.raises(ValidationError):
        DesignConcept.model_validate(bad)


def test_quality_passes_auto():
    score = QualityScore(luxury_score=0.85, theology_depth=0.80)
    assert score.passes_auto is True
    assert score.needs_review is False
    assert score.auto_kill is False


def test_quality_needs_review():
    score = QualityScore(luxury_score=0.78, theology_depth=0.70)
    assert score.passes_auto is False
    assert score.needs_review is True
    assert score.auto_kill is False


def test_quality_auto_kill():
    score = QualityScore(luxury_score=0.50, theology_depth=0.40)
    assert score.passes_auto is False
    assert score.needs_review is False
    assert score.auto_kill is True
