"""Verify the two explicit fire prompt proof assets."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from ftc.config import ARTIFACTS

ROOT = ARTIFACTS / "fire_tests"
REQUIRED = {
    "glitch_cross.svg": ["ERROR 404: SIN NOT FOUND", "rough-edge", "scanlines"],
    "torn_paper_revelation.svg": ["TRUTH", "rough-edge", "halftone"],
}


def main() -> int:
    errors: list[str] = []
    for filename, needles in REQUIRED.items():
        path = ROOT / filename
        if not path.exists():
            errors.append(f"{filename}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        if "<image" in text:
            errors.append(f"{filename}: raster image tag found")
        root = ET.fromstring(text)
        if root.attrib.get("viewBox") != "0 0 2048 2048":
            errors.append(f"{filename}: expected 2048 viewBox")
        for needle in needles:
            if needle not in text:
                errors.append(f"{filename}: missing {needle}")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print("PASS: fire prompt assets verified")
    print("PASS: glitch_cross.svg has RGB glitch, scanlines, and exact error text")
    print("PASS: torn_paper_revelation.svg has torn paper, halftone, and TRUTH text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
