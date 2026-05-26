"""Procedural SVG streetwear graphic engine.

Generates high-fidelity SVG graphics for FTC streetwear — Christian symbols
abstracted into geometry, scripture-as-form, light/shadow studies, monastic
typography compositions. Outputs are self-contained SVGs renderable directly.

Real photorealistic versions come from the OpenRouter image worker
(workers/openrouter_image_worker.py) using these SVGs as ControlNet hints.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .colors import Palette, best_text_color, palette_for

GraphicStyle = Literal[
    "cornerstone",
    "veil",
    "living-water",
    "ember",
    "threshold",
    "covenant-arc",
    "manna",
    "wilderness",
    "still-waters",
    "vine",
    "ladder",
    "alabaster",
    "broken-grid",
    "mercy-seat",
    "tabernacle",
]

ALL_STYLES: tuple[GraphicStyle, ...] = (
    "cornerstone", "veil", "living-water", "ember", "threshold",
    "covenant-arc", "manna", "wilderness", "still-waters", "vine",
    "ladder", "alabaster", "broken-grid", "mercy-seat", "tabernacle",
)

VIEWBOX = "0 0 1200 1500"
W, H = 1200, 1500


@dataclass
class GraphicSpec:
    style: GraphicStyle
    title: str
    palette: Palette
    seed: int
    typography: str  # "humanist-serif" | "grotesque" | "mono"


def _rng(seed: int) -> random.Random:
    return random.Random(seed)


def _bg(palette: Palette) -> str:
    return f'<rect x="0" y="0" width="{W}" height="{H}" fill="{palette.hexes[0]}"/>'


def _grain(seed: int, opacity: float = 0.04) -> str:
    """Subtle noise overlay using filter primitives."""
    return f"""
    <filter id="grain-{seed}" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="{seed}"/>
      <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {opacity} 0"/>
    </filter>
    <rect x="0" y="0" width="{W}" height="{H}" filter="url(#grain-{seed})"/>
    """


def _cornerstone(spec: GraphicSpec) -> str:
    """A single tonal stone block, slightly off-center — what the builders refused."""
    rng = _rng(spec.seed)
    cx, cy = 600 + rng.randint(-40, 40), 750 + rng.randint(-30, 30)
    size = 280
    angle = rng.uniform(-3, 3)
    accent = spec.palette.hexes[2] if len(spec.palette.hexes) > 2 else spec.palette.hexes[-1]
    mid = spec.palette.hexes[1]
    return f"""
    <g transform="rotate({angle:.2f} {cx} {cy})">
      <rect x="{cx - size//2}" y="{cy - size//2}" width="{size}" height="{size}"
            fill="{mid}" stroke="{accent}" stroke-width="2" opacity="0.95"/>
      <rect x="{cx - size//2 + 18}" y="{cy - size//2 + 18}" width="{size - 36}" height="{size - 36}"
            fill="none" stroke="{accent}" stroke-width="0.6" opacity="0.7"/>
    </g>
    """


def _veil(spec: GraphicSpec) -> str:
    """Translucent vertical bands — what shadow agreed to release."""
    rng = _rng(spec.seed)
    out = []
    band_w = 90
    for i in range(W // band_w + 2):
        x = i * band_w
        opacity = 0.04 + (rng.random() * 0.16)
        out.append(
            f'<rect x="{x}" y="0" width="{band_w}" height="{H}" '
            f'fill="{spec.palette.hexes[-1]}" opacity="{opacity:.3f}"/>'
        )
    return "\n".join(out)


def _living_water(spec: GraphicSpec) -> str:
    """Concentric ripple geometry, soft."""
    rng = _rng(spec.seed)
    cx, cy = 600, 750
    accent = spec.palette.hexes[2] if len(spec.palette.hexes) > 2 else spec.palette.hexes[1]
    out = []
    for i in range(14):
        r = 60 + i * 48
        opacity = 0.85 - i * 0.055
        if opacity < 0.05:
            break
        out.append(
            f'<circle cx="{cx + rng.randint(-3,3)}" cy="{cy + rng.randint(-3,3)}" '
            f'r="{r}" fill="none" stroke="{accent}" stroke-width="{1.4 - i*0.06:.2f}" '
            f'opacity="{opacity:.3f}"/>'
        )
    return "\n".join(out)


def _ember(spec: GraphicSpec) -> str:
    """Off-center radial glow — what remains after the fire."""
    cx, cy = 700, 800
    accent = spec.palette.hexes[2] if len(spec.palette.hexes) > 2 else spec.palette.hexes[1]
    return f"""
    <defs>
      <radialGradient id="ember-{spec.seed}" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="{accent}" stop-opacity="0.95"/>
        <stop offset="50%" stop-color="{accent}" stop-opacity="0.25"/>
        <stop offset="100%" stop-color="{spec.palette.hexes[0]}" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="{cx}" cy="{cy}" r="500" fill="url(#ember-{spec.seed})"/>
    """


def _threshold(spec: GraphicSpec) -> str:
    """Horizontal line dividing upper and lower fields."""
    accent = spec.palette.hexes[-1]
    return f"""
    <rect x="0" y="730" width="{W}" height="1.2" fill="{accent}" opacity="0.85"/>
    <rect x="0" y="755" width="{W}" height="0.4" fill="{accent}" opacity="0.4"/>
    """


def _covenant_arc(spec: GraphicSpec) -> str:
    """A wide arch — covenant geometry."""
    accent = spec.palette.hexes[-1]
    mid = spec.palette.hexes[1] if len(spec.palette.hexes) > 1 else accent
    return f"""
    <path d="M 100 1100 Q 600 450 1100 1100" fill="none"
          stroke="{accent}" stroke-width="2" opacity="0.9"/>
    <path d="M 140 1080 Q 600 520 1060 1080" fill="none"
          stroke="{mid}" stroke-width="0.8" opacity="0.5"/>
    """


def _manna(spec: GraphicSpec) -> str:
    """Field of small dots — daily bread."""
    rng = _rng(spec.seed)
    out = []
    accent = spec.palette.hexes[-1]
    for _ in range(180):
        x = rng.randint(80, W - 80)
        y = rng.randint(120, H - 200)
        r = rng.uniform(1.2, 3.4)
        op = rng.uniform(0.3, 0.85)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r:.2f}" fill="{accent}" opacity="{op:.2f}"/>')
    return "\n".join(out)


def _wilderness(spec: GraphicSpec) -> str:
    """Sparse vertical marks — long horizon."""
    rng = _rng(spec.seed)
    out = []
    accent = spec.palette.hexes[-1]
    for _ in range(38):
        x = rng.randint(60, W - 60)
        y = rng.randint(700, 1100)
        height = rng.randint(10, 80)
        op = rng.uniform(0.25, 0.7)
        out.append(
            f'<rect x="{x}" y="{y}" width="0.8" height="{height}" fill="{accent}" opacity="{op:.2f}"/>'
        )
    return "\n".join(out)


def _still_waters(spec: GraphicSpec) -> str:
    """Horizontal layered bands — quiet water."""
    out = []
    accent = spec.palette.hexes[-1]
    for i, y in enumerate(range(900, 1300, 16)):
        op = 0.18 + 0.04 * (i % 3)
        out.append(f'<rect x="100" y="{y}" width="{W - 200}" height="1.2" fill="{accent}" opacity="{op:.2f}"/>')
    return "\n".join(out)


def _vine(spec: GraphicSpec) -> str:
    """A single twisting line — the true vine."""
    rng = _rng(spec.seed)
    accent = spec.palette.hexes[-1]
    points = []
    x, y = 200, 200
    for _ in range(40):
        x += rng.randint(15, 30)
        y += rng.randint(20, 38)
        if y > H - 200:
            break
        points.append(f"{x},{y}")
        # branch occasionally
    path = "M " + " L ".join(points)
    return f'<path d="{path}" fill="none" stroke="{accent}" stroke-width="1.4" opacity="0.85"/>'


def _ladder(spec: GraphicSpec) -> str:
    """Vertical rungs ascending — Jacob's ladder, abstracted."""
    accent = spec.palette.hexes[-1]
    out = []
    for i in range(22):
        y = 1280 - i * 52
        op = 0.85 - i * 0.035
        out.append(
            f'<rect x="540" y="{y}" width="120" height="2.5" fill="{accent}" opacity="{op:.2f}"/>'
        )
    out.append(f'<rect x="540" y="280" width="2" height="1000" fill="{accent}" opacity="0.6"/>')
    out.append(f'<rect x="658" y="280" width="2" height="1000" fill="{accent}" opacity="0.6"/>')
    return "\n".join(out)


def _alabaster(spec: GraphicSpec) -> str:
    """Vertical column with subtle veining — alabaster jar."""
    rng = _rng(spec.seed)
    accent = spec.palette.hexes[-1]
    mid = spec.palette.hexes[1]
    return f"""
    <rect x="500" y="350" width="200" height="800" fill="{mid}" opacity="0.7"/>
    <path d="M 500 350 Q 500 320 540 320 L 660 320 Q 700 320 700 350"
          fill="{mid}" opacity="0.7"/>
    <path d="M 540 360 Q 580 800 540 1140" fill="none" stroke="{accent}"
          stroke-width="0.6" opacity="0.4"/>
    <path d="M 620 360 Q 660 800 620 1140" fill="none" stroke="{accent}"
          stroke-width="0.6" opacity="0.4"/>
    """


def _broken_grid(spec: GraphicSpec) -> str:
    """A grid with sections deliberately missing — grace as discontinuity."""
    rng = _rng(spec.seed)
    accent = spec.palette.hexes[-1]
    out = []
    for x in range(120, W - 120, 90):
        for y in range(200, H - 200, 90):
            if rng.random() > 0.18:  # 18% missing
                out.append(
                    f'<rect x="{x}" y="{y}" width="76" height="76" fill="none" '
                    f'stroke="{accent}" stroke-width="0.6" opacity="0.5"/>'
                )
    return "\n".join(out)


def _mercy_seat(spec: GraphicSpec) -> str:
    """Two facing wing arcs — cherubim over the mercy seat, abstracted."""
    accent = spec.palette.hexes[-1]
    return f"""
    <path d="M 200 900 Q 350 500 600 800 Q 850 500 1000 900" fill="none"
          stroke="{accent}" stroke-width="2" opacity="0.85"/>
    <rect x="320" y="900" width="560" height="120" fill="none"
          stroke="{accent}" stroke-width="1.2" opacity="0.6"/>
    """


def _tabernacle(spec: GraphicSpec) -> str:
    """Nested rectangles — outer court, holy place, holy of holies."""
    accent = spec.palette.hexes[-1]
    return f"""
    <rect x="200" y="350" width="800" height="800" fill="none" stroke="{accent}" stroke-width="1.2" opacity="0.8"/>
    <rect x="320" y="470" width="560" height="560" fill="none" stroke="{accent}" stroke-width="1" opacity="0.7"/>
    <rect x="440" y="590" width="320" height="320" fill="none" stroke="{accent}" stroke-width="0.8" opacity="0.6"/>
    """


STYLE_RENDERERS = {
    "cornerstone": _cornerstone,
    "veil": _veil,
    "living-water": _living_water,
    "ember": _ember,
    "threshold": _threshold,
    "covenant-arc": _covenant_arc,
    "manna": _manna,
    "wilderness": _wilderness,
    "still-waters": _still_waters,
    "vine": _vine,
    "ladder": _ladder,
    "alabaster": _alabaster,
    "broken-grid": _broken_grid,
    "mercy-seat": _mercy_seat,
    "tabernacle": _tabernacle,
}


def _typography(spec: GraphicSpec) -> str:
    """Render the design title in restrained typography."""
    text_color = best_text_color(spec.palette.hexes[0])
    family_map = {
        "humanist-serif": "Georgia, 'Times New Roman', serif",
        "grotesque": "Inter, Helvetica, sans-serif",
        "mono": "'JetBrains Mono', Menlo, monospace",
    }
    family = family_map.get(spec.typography, family_map["grotesque"])
    return f"""
    <text x="{W//2}" y="1380" font-family="{family}" font-size="22"
          fill="{text_color}" text-anchor="middle"
          letter-spacing="6" opacity="0.85">{spec.title.upper()}</text>
    <text x="{W//2}" y="1420" font-family="{family}" font-size="11"
          fill="{text_color}" text-anchor="middle"
          letter-spacing="3" opacity="0.55">FTC · FULL TIME CHRISTIAN</text>
    """


def render_graphic(spec: GraphicSpec) -> str:
    """Return a self-contained SVG document for one streetwear graphic."""
    renderer = STYLE_RENDERERS[spec.style]
    body = renderer(spec)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}" width="{W}" height="{H}">
  <defs>
    {_grain(spec.seed)}
  </defs>
  {_bg(spec.palette)}
  {body}
  {_typography(spec)}
</svg>
"""


def _seed_for(title: str, style: GraphicStyle, palette_idx: int) -> int:
    h = hashlib.sha256(f"{title}:{style}:{palette_idx}".encode()).hexdigest()
    return int(h[:8], 16)


def generate_collection(
    out_dir: Path,
    count: int = 30,
    sections: tuple[str, ...] = ("tee", "tracksuit", "outerwear", "accessory"),
) -> list[Path]:
    """Generate `count` streetwear graphics across all styles + palettes."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    titles = [
        "Cornerstone", "Veil", "Living Water", "Ember", "Threshold",
        "Covenant", "Manna", "Wilderness", "Still Waters", "True Vine",
        "Jacob's Ladder", "Alabaster", "Broken Grid", "Mercy Seat",
        "Tabernacle", "Cedar", "Anchor", "Watchman", "Refuge",
        "Salt", "Light", "Stone", "Witness", "Shepherd",
        "Harvest", "Linen", "Olive", "Fig", "Cedar of Lebanon",
        "Sojourner",
    ]
    typography_options = ["humanist-serif", "grotesque", "mono"]

    for i in range(count):
        style = ALL_STYLES[i % len(ALL_STYLES)]
        title = titles[i % len(titles)]
        section = sections[i % len(sections)]
        palette = palette_for(section, i, seed=f"FTC-GRAPHIC-{i:03d}")
        spec = GraphicSpec(
            style=style,
            title=title,
            palette=palette,
            seed=_seed_for(title, style, i),
            typography=typography_options[i % 3],
        )
        svg = render_graphic(spec)
        path = out_dir / f"ftc-graphic-{i:03d}-{style}-{title.lower().replace(' ', '-').replace(chr(39), '')}.svg"
        path.write_text(svg)
        paths.append(path)
    return paths


if __name__ == "__main__":
    from pathlib import Path as _P
    out = _P(__file__).resolve().parent.parent / "artifacts" / "graphics"
    paths = generate_collection(out, count=30)
    print(f"Generated {len(paths)} graphics into {out}")
    for p in paths[:5]:
        print(" -", p.name)
