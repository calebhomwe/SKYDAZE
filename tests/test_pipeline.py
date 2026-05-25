"""Tests for the pipeline orchestration."""

import pytest

from ftc.config import PipelineConfig
from ftc.models import DesignConcept, QualityScore
from ftc.pipeline import ConceptGenerator, PipelineError

SAMPLE_CONCEPT = {
    "id": "FTC-042",
    "title": "Living Water",
    "theological_core": "Grace as an inexhaustible wellspring hidden beneath the surface",
    "aesthetic_direction": "Fluid ink wash textures, deep indigo-to-white gradient, organic flow",
    "typography_layout": (
        "Condensed grotesque at nape, watermark-opacity scripture fragment interior"
    ),
    "color_palette": ["#1A237E", "#E8EAF6", "#FAFAFA"],
    "print_technique": "Discharge print on garment-dyed indigo",
    "fal_ai_visual_prompt": (
        "Luxury heavyweight tee, indigo discharge print, fluid ink wash texture, "
        "editorial flat lay, 4:5 AR, natural light"
    ),
    "novita_video_prompt": "7s slow zoom, ink diffusion in water overlay, ambient light shift",
    "nano_banana_mockup_prompt": "Apply to oversized crew tee, indigo garment-dye, front panel",
    "reference_source_tags": ["pinterest_abstract", "fog_minimal"],
    "promo_hook": "TikTok — lo-fi ambient — 'Still waters. Deep roots.'",
}


def test_validate_concept():
    config = PipelineConfig()
    gen = ConceptGenerator(config)
    concept = gen.validate_concept(SAMPLE_CONCEPT)
    assert isinstance(concept, DesignConcept)
    assert concept.id == "FTC-042"


def test_score_concept_passes():
    config = PipelineConfig()
    gen = ConceptGenerator(config)
    concept = gen.validate_concept(SAMPLE_CONCEPT)
    score = gen.score_concept(concept)
    assert isinstance(score, QualityScore)
    assert score.passes_auto


@pytest.mark.anyio
async def test_generate_requires_api_key():
    config = PipelineConfig(openrouter_api_key="")
    gen = ConceptGenerator(config)
    with pytest.raises(PipelineError, match="OPENROUTER_API_KEY"):
        await gen.generate("Test prompt")


@pytest.mark.anyio
async def test_generate_rejects_forbidden():
    config = PipelineConfig(openrouter_api_key="test-key")
    gen = ConceptGenerator(config)
    with pytest.raises(PipelineError, match="forbidden"):
        await gen.generate("Design with skulls and cartoon aesthetics")
