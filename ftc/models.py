"""Pydantic models for the FTC design concept schema (Section 4 of Master Context)."""

from pydantic import BaseModel, Field


class DesignConcept(BaseModel):
    """A single FTC design concept following the strict JSON schema."""

    id: str = Field(..., pattern=r"^FTC-\d{3,}$", description="Concept ID, e.g. FTC-001")
    title: str
    theological_core: str = Field(..., description="1-sentence abstract doctrine/metaphor")
    aesthetic_direction: str = Field(..., description="Style + mood + composition notes")
    typography_layout: str = Field(..., description="Font treatment, placement, hierarchy")
    color_palette: list[str] = Field(..., min_length=1, description="List of HEX color codes")
    print_technique: str = Field(..., description="Screen/Puff/Embroidery/Tonal/Discharge/etc.")
    fal_ai_visual_prompt: str = Field(
        ..., description="Optimized for Seedream 4.0. Includes luxury cues + 4:5 AR"
    )
    novita_video_prompt: str = Field(..., description="5-10s motion: fabric/lighting/texture focus")
    nano_banana_mockup_prompt: str = Field(
        ..., description="Garment template integration directive"
    )
    reference_source_tags: list[str] = Field(default_factory=list)
    promo_hook: str = Field(..., description="Caption tone + platform + audio suggestion")


class QualityScore(BaseModel):
    """Quality gate scores per Section 5 of Master Context."""

    luxury_score: float = Field(..., ge=0.0, le=1.0)
    theology_depth: float = Field(..., ge=0.0, le=1.0)

    @property
    def passes_auto(self) -> bool:
        return self.luxury_score >= 0.82 and self.theology_depth >= 0.75

    @property
    def needs_review(self) -> bool:
        return not self.passes_auto and self.luxury_score >= 0.75 and self.theology_depth >= 0.60

    @property
    def auto_kill(self) -> bool:
        return self.luxury_score < 0.60 or self.theology_depth < 0.60
