"""Tests for configuration and forbidden-term validation."""

from ftc.config import PipelineConfig, load_config, validate_no_forbidden


def test_load_config_defaults():
    config = load_config()
    assert isinstance(config, PipelineConfig)
    assert config.luxury_score_threshold == 0.82
    assert config.theology_depth_threshold == 0.75


def test_forbidden_terms_detected():
    violations = validate_no_forbidden("This design has skulls and neon colors")
    assert "skulls" in violations
    assert "neon" in violations


def test_clean_text_passes():
    violations = validate_no_forbidden("Elegant tonal embroidery on heavyweight cotton")
    assert violations == []


def test_forbidden_case_insensitive():
    violations = validate_no_forbidden("CARTOON style graphics")
    assert "cartoon" in violations
