"""Convert FTC streetwear graphics to Roblox shirt decal PNGs.

Reads SVGs from `artifacts/graphics/` and writes 585×559 px PNGs to
`parked/genesis-roblox-edition/roblox/shirt-decals/`. Those are the
exact dimensions Roblox uses for shirt templates.

Usage:
  python3 parked/genesis-roblox-edition/roblox/convert_decals.py
"""

from __future__ import annotations

from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parent.parent.parent.parent
SRC = ROOT / "artifacts" / "graphics"
DST = ROOT / "parked" / "genesis-roblox-edition" / "roblox" / "shirt-decals"

# Roblox shirt template dimensions
WIDTH = 585
HEIGHT = 559


def main() -> None:
    if not SRC.exists():
        print(f"[error] no SVGs at {SRC} — run `make graphics` first")
        return

    DST.mkdir(parents=True, exist_ok=True)

    svgs = sorted(SRC.glob("*.svg"))
    if not svgs:
        print(f"[error] no .svg files in {SRC}")
        return

    for i, svg in enumerate(svgs, 1):
        out = DST / (svg.stem + ".png")
        cairosvg.svg2png(
            url=str(svg),
            write_to=str(out),
            output_width=WIDTH,
            output_height=HEIGHT,
        )
        print(f"[{i:>2}/{len(svgs)}] {out.name}")

    print(f"\nWrote {len(svgs)} Roblox-ready PNGs to {DST.relative_to(ROOT)}")
    print(f"Next: upload to Roblox Studio as 'Shirt' assets, paste asset IDs into ShirtCustomizer.lua")


if __name__ == "__main__":
    main()
