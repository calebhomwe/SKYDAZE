"""Verify generated FTC collection artifacts.

This is intentionally lightweight so it can run in Cursor Cloud without
external services. It checks that the requested 1000 print designs exist,
that every design has SVG, EPS, mockup, and concept files, and that the
primary SVGs are scalable vector artwork with no raster images.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from ftc.config import ARTIFACTS

ROOT = ARTIFACTS / "collection_v1"
EXPECTED = 1000


def _fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def _count_files(path: Path, pattern: str) -> int:
    return len(list(path.glob(pattern)))


def _validate_svg(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if "<image" in text:
        errors.append(f"{path.name}: raster image tag found")
    root = ET.fromstring(text)
    if root.attrib.get("viewBox") != "0 0 2048 2048":
        errors.append(f"{path.name}: expected 2048 viewBox")
    if root.attrib.get("width") != "2048" or root.attrib.get("height") != "2048":
        errors.append(f"{path.name}: expected 2048 width/height")
    return errors


def main() -> int:
    if not ROOT.exists():
        return _fail(f"{ROOT} does not exist. Run python generate_collection.py first.")

    designs_path = ROOT / "designs.json"
    summary_path = ROOT / "summary.json"
    if not designs_path.exists():
        return _fail("designs.json missing")
    if not summary_path.exists():
        return _fail("summary.json missing")

    designs = json.loads(designs_path.read_text(encoding="utf-8"))
    if len(designs) != EXPECTED:
        return _fail(f"expected {EXPECTED} designs, found {len(designs)}")

    expected_counts = {
        "svg": _count_files(ROOT / "svg", "*.svg"),
        "eps": _count_files(ROOT / "eps", "*.eps"),
        "mockups": _count_files(ROOT / "mockups", "*.svg"),
        "concepts": _count_files(ROOT / "concepts", "*.json"),
    }
    missing = {name: count for name, count in expected_counts.items() if count != EXPECTED}
    if missing:
        return _fail(f"wrong file counts: {missing}")

    svg_errors: list[str] = []
    for row in designs:
        svg_path = ROOT / row["svg_path"]
        eps_path = ROOT / row["eps_path"]
        if not svg_path.exists():
            svg_errors.append(f"{row['id']}: SVG missing")
            continue
        if not eps_path.exists():
            svg_errors.append(f"{row['id']}: EPS missing")
        svg_errors.extend(_validate_svg(svg_path))
        if eps_path.exists() and not eps_path.read_text(encoding="utf-8").startswith("%!PS-Adobe"):
            svg_errors.append(f"{row['id']}: EPS header missing")
        if row.get("asset_type") != "standalone_vector_graphic":
            svg_errors.append(f"{row['id']}: wrong asset_type")
        if "hat" not in row.get("usable_surfaces", []):
            svg_errors.append(f"{row['id']}: hat surface missing")

    if svg_errors:
        for error in svg_errors[:20]:
            print(error)
        return _fail(f"{len(svg_errors)} validation errors")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    exports = summary.get("asset_exports", {})
    if exports.get("print_svg") != EXPECTED or exports.get("eps") != EXPECTED:
        return _fail(f"summary export counts wrong: {exports}")

    print(f"PASS: {EXPECTED} standalone print graphics verified")
    print(f"PASS: counts {expected_counts}")
    print("PASS: SVG files are 2048x2048 vectors with no raster image tags")
    print("PASS: EPS companions and portable surface metadata present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
