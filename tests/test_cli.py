"""Tests for the CLI entry point."""

import json

from ftc.cli import main


def test_status_command(capsys):
    ret = main(["status"])
    assert ret == 0
    out = capsys.readouterr().out
    assert "FTC Pipeline" in out


def test_validate_valid_concept(tmp_path):
    concept = {
        "id": "FTC-001",
        "title": "Cornerstone",
        "theological_core": "Christ as the rejected stone that became the foundation",
        "aesthetic_direction": "Muted earth tones, architectural composition",
        "typography_layout": "Distressed serif at center chest",
        "color_palette": ["#2C2C2C", "#A89F91"],
        "print_technique": "Tonal embroidery",
        "fal_ai_visual_prompt": "Luxury tee editorial 4:5",
        "novita_video_prompt": "5s fabric motion",
        "nano_banana_mockup_prompt": "Front chest placement",
        "reference_source_tags": ["stampd"],
        "promo_hook": "Instagram — ambient — Built on rock.",
    }
    f = tmp_path / "concept.json"
    f.write_text(json.dumps(concept))

    ret = main(["validate", str(f)])
    assert ret == 0


def test_validate_invalid_file():
    ret = main(["validate", "/nonexistent/file.json"])
    assert ret == 1


def test_check_env():
    ret = main(["check-env"])
    assert isinstance(ret, int)


def test_no_command(capsys):
    ret = main([])
    assert ret == 0
