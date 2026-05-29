"""Convert FTC bold graphic tees to Roblox shirt decal PNGs.

Reads SVGs from `artifacts/graphics-bold/` and writes 585×559 px PNGs to
`parked/genesis-roblox-edition/roblox/shirt-decals-bold/`.
"""

from __future__ import annotations

from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parent.parent.parent.parent
SRC = ROOT / "artifacts" / "graphics-bold"
DST = ROOT / "parked" / "genesis-roblox-edition" / "roblox" / "shirt-decals-bold"

WIDTH = 585
HEIGHT = 559


def main() -> None:
    if not SRC.exists():
        print(f"[error] no SVGs at {SRC} — run `python3 -m ftc.bold_graphics_engine` first")
        return

    DST.mkdir(parents=True, exist_ok=True)

    svgs = sorted(SRC.glob("*.svg"))
    for i, svg in enumerate(svgs, 1):
        out = DST / (svg.stem + ".png")
        cairosvg.svg2png(
            url=str(svg),
            write_to=str(out),
            output_width=WIDTH,
            output_height=HEIGHT,
        )
        print(f"[{i:>2}/{len(svgs)}] {out.name}")

    print(f"\nWrote {len(svgs)} bold-tier Roblox-ready PNGs to {DST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
