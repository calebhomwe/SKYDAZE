"""GENESIS mesh renderer — procedural isometric SVG worlds.

Generates beautiful isometric neighborhood/world tiles for each World in
world_schema.py. Uses real coordinate-derived seeding so Scarborough always
looks like Scarborough across runs.

Style: Monument Valley meets Studio Ghibli backgrounds — quiet, layered,
restrained palette, atmospheric depth via sky gradient + fog band + grain.
"""

from __future__ import annotations

import hashlib
import math
import random
from pathlib import Path
from typing import Iterable

from .world_schema import ALL_WORLDS, World

W, H = 1600, 900
HORIZON = 520
TILE_W, TILE_H = 80, 40  # isometric tile size
GRID_COLS, GRID_ROWS = 20, 12


def _seed_for(world: World) -> int:
    h = hashlib.sha256(world.id.encode()).hexdigest()
    return int(h[:8], 16)


def _sky_gradient(world: World) -> str:
    p = world.palette
    return f"""
    <defs>
      <linearGradient id="sky-{world.id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{p[0]}"/>
        <stop offset="55%" stop-color="{p[1]}"/>
        <stop offset="100%" stop-color="{p[2]}"/>
      </linearGradient>
      <linearGradient id="ground-{world.id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{p[2]}"/>
        <stop offset="50%" stop-color="{p[3] if len(p) > 3 else p[2]}"/>
        <stop offset="100%" stop-color="{p[4] if len(p) > 4 else p[3] if len(p) > 3 else p[2]}"/>
      </linearGradient>
      <radialGradient id="sun-{world.id}" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="{p[4] if len(p) > 4 else p[3] if len(p) > 3 else '#fff'}" stop-opacity="0.9"/>
        <stop offset="100%" stop-color="{p[4] if len(p) > 4 else p[3] if len(p) > 3 else '#fff'}" stop-opacity="0"/>
      </radialGradient>
      <filter id="grain-{world.id}" x="0" y="0" width="100%" height="100%">
        <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{_seed_for(world)}"/>
        <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.05 0"/>
      </filter>
    </defs>
    """


def _sky_and_horizon(world: World) -> str:
    return f"""
    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#sky-{world.id})"/>
    <circle cx="1180" cy="280" r="220" fill="url(#sun-{world.id})"/>
    <rect x="0" y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="url(#ground-{world.id})"/>
    """


def _iso_point(col: float, row: float, origin_x: float = 800, origin_y: float = 600) -> tuple[float, float]:
    """Convert grid coordinates to screen coordinates (isometric)."""
    x = origin_x + (col - row) * (TILE_W / 2)
    y = origin_y + (col + row) * (TILE_H / 2)
    return x, y


def _building(col: float, row: float, height: int, color: str, accent: str, roof: str = "flat") -> str:
    """Render an isometric building block at grid position (col, row)."""
    # Base footprint corners
    bw, bh = 1.4, 1.4  # building footprint in tiles
    tx_n, ty_n = _iso_point(col, row)              # north
    tx_e, ty_e = _iso_point(col + bw, row)         # east
    tx_s, ty_s = _iso_point(col + bw, row + bh)    # south
    tx_w, ty_w = _iso_point(col, row + bh)         # west

    # Top corners (offset up by height)
    top_n = (tx_n, ty_n - height)
    top_e = (tx_e, ty_e - height)
    top_s = (tx_s, ty_s - height)
    top_w = (tx_w, ty_w - height)

    # Darken/lighten for face contrast
    parts = []
    # left face (west)
    parts.append(
        f'<polygon points="{tx_n},{ty_n} {tx_w},{ty_w} {top_w[0]},{top_w[1]} {top_n[0]},{top_n[1]}" '
        f'fill="{color}" stroke="#000" stroke-opacity="0.15" stroke-width="0.6"/>'
    )
    # right face (south)
    parts.append(
        f'<polygon points="{tx_w},{ty_w} {tx_s},{ty_s} {top_s[0]},{top_s[1]} {top_w[0]},{top_w[1]}" '
        f'fill="{accent}" stroke="#000" stroke-opacity="0.18" stroke-width="0.6"/>'
    )
    # top
    parts.append(
        f'<polygon points="{top_n[0]},{top_n[1]} {top_e[0]},{top_e[1]} {top_s[0]},{top_s[1]} {top_w[0]},{top_w[1]}" '
        f'fill="{color}" opacity="0.92" stroke="#000" stroke-opacity="0.12" stroke-width="0.5"/>'
    )

    # Windows (small bright squares on south face)
    if height > 60:
        for floor in range(2, max(2, height // 30)):
            wy = ty_w - floor * 28
            for col_idx in range(2):
                wx = tx_w + 14 + col_idx * 24
                parts.append(
                    f'<rect x="{wx}" y="{wy - 4}" width="6" height="8" fill="#FFE9B0" opacity="0.45"/>'
                )

    # Roof variant
    if roof == "peaked":
        ridge_x = (top_n[0] + top_s[0]) / 2
        ridge_y = (top_n[1] + top_s[1]) / 2 - 18
        parts.append(
            f'<polygon points="{top_n[0]},{top_n[1]} {top_e[0]},{top_e[1]} {ridge_x},{ridge_y}" '
            f'fill="{accent}" opacity="0.85"/>'
        )
        parts.append(
            f'<polygon points="{top_w[0]},{top_w[1]} {top_s[0]},{top_s[1]} {ridge_x},{ridge_y}" '
            f'fill="{color}" opacity="0.75"/>'
        )

    return "\n".join(parts)


def _tree(col: float, row: float, scale: float, color: str, shadow: str) -> str:
    """Render an isometric tree (canopy + trunk shadow)."""
    x, y = _iso_point(col, row)
    canopy_r = 14 * scale
    return f"""
    <ellipse cx="{x + 4}" cy="{y + 4}" rx="{canopy_r * 0.9}" ry="{canopy_r * 0.35}" fill="{shadow}" opacity="0.35"/>
    <rect x="{x - 2}" y="{y - 12}" width="3" height="14" fill="#3A2A20" opacity="0.85"/>
    <circle cx="{x - 1}" cy="{y - 22}" r="{canopy_r}" fill="{color}" opacity="0.92"/>
    <circle cx="{x + 8}" cy="{y - 28}" r="{canopy_r * 0.7}" fill="{color}" opacity="0.8"/>
    <circle cx="{x - 8}" cy="{y - 28}" r="{canopy_r * 0.65}" fill="{color}" opacity="0.7"/>
    """


def _road(start_col: float, start_row: float, end_col: float, end_row: float, color: str) -> str:
    """A thin isometric road segment."""
    x1, y1 = _iso_point(start_col, start_row)
    x2, y2 = _iso_point(end_col, end_row)
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="14" opacity="0.55" stroke-linecap="round"/>'


def _streetlamp(col: float, row: float, color: str) -> str:
    x, y = _iso_point(col, row)
    return f"""
    <rect x="{x - 1}" y="{y - 36}" width="2" height="36" fill="#2A2A2A" opacity="0.85"/>
    <circle cx="{x}" cy="{y - 38}" r="3.5" fill="#FFE6A0" opacity="0.95"/>
    <circle cx="{x}" cy="{y - 38}" r="11" fill="#FFE6A0" opacity="0.15"/>
    """


def _fog_band(world: World) -> str:
    p = world.palette
    color = p[2] if len(p) > 2 else p[1]
    return (
        f'<rect x="0" y="{HORIZON - 20}" width="{W}" height="40" fill="{color}" opacity="0.35"/>'
        f'<rect x="0" y="{HORIZON}" width="{W}" height="14" fill="{p[3] if len(p) > 3 else color}" opacity="0.25"/>'
    )


def _grain_overlay(world: World) -> str:
    return f'<rect x="0" y="0" width="{W}" height="{H}" filter="url(#grain-{world.id})"/>'


def _signature(world: World) -> str:
    text_color = world.palette[4] if len(world.palette) > 4 else "#FFFFFF"
    coords = world.coords_lat_lng or (0.0, 0.0)
    coord_str = f"{coords[0]:.4f}, {coords[1]:.4f}" if world.coords_lat_lng else "—"
    return f"""
    <g font-family="Inter, Helvetica, sans-serif">
      <text x="60" y="60" font-size="14" fill="{text_color}" opacity="0.7" letter-spacing="4">GENESIS · {world.id}</text>
      <text x="60" y="86" font-size="34" fill="{text_color}" opacity="0.95" letter-spacing="6">{world.name.upper()}</text>
      <text x="60" y="112" font-size="11" fill="{text_color}" opacity="0.55" letter-spacing="2">{world.region}</text>
      <text x="60" y="{H - 60}" font-size="10" fill="{text_color}" opacity="0.55" letter-spacing="2">{coord_str}</text>
      <text x="60" y="{H - 42}" font-size="12" fill="{text_color}" opacity="0.7" letter-spacing="1.5" font-style="italic">"{world.parable}"</text>
    </g>
    """


def _biome_scene(world: World) -> str:
    """Build the world body — buildings, trees, roads — based on biome."""
    rng = random.Random(_seed_for(world))
    p = world.palette
    parts: list[str] = []

    # Building palette: a mid-tone and an accent
    bldg_main = p[1] if len(p) > 1 else "#444"
    bldg_accent = p[2] if len(p) > 2 else bldg_main
    tree_color = p[2] if len(p) > 2 else "#88A37B"
    tree_shadow = p[1] if len(p) > 1 else "#222"
    road_color = p[0]

    biome = world.biome

    # Different layouts per biome
    if biome == "cedar-forest":
        # Mostly trees, very few low structures
        for _ in range(120):
            c = rng.uniform(-2, GRID_COLS + 2)
            r = rng.uniform(-2, GRID_ROWS + 2)
            scale = rng.uniform(1.4, 2.6)
            parts.append(_tree(c, r, scale, tree_color, tree_shadow))
        # one shrine
        parts.append(_building(9, 5, 48, bldg_main, bldg_accent, "peaked"))

    elif biome == "desert-sand":
        # Sparse low blocks, almost no trees
        for col in range(2, GRID_COLS, 4):
            for row in range(2, GRID_ROWS, 3):
                if rng.random() < 0.45:
                    height = rng.randint(20, 50)
                    parts.append(_building(col, row, height, bldg_main, bldg_accent, "flat"))
        for _ in range(8):
            c = rng.uniform(0, GRID_COLS)
            r = rng.uniform(0, GRID_ROWS)
            parts.append(_tree(c, r, 0.8, tree_color, tree_shadow))

    elif biome == "marble-city":
        # Dense, tall, marble-pale blocks with peaked roofs
        for col in range(0, GRID_COLS, 2):
            for row in range(0, GRID_ROWS, 2):
                if rng.random() < 0.7:
                    height = rng.randint(80, 180)
                    roof = "peaked" if rng.random() < 0.4 else "flat"
                    parts.append(_building(col, row, height, bldg_main, bldg_accent, roof))

    elif biome == "concrete-suburb":
        # DMV / Scarborough / South London — orthogonal blocks, lots of streetlamps
        # Roads
        parts.append(_road(0, GRID_ROWS / 2, GRID_COLS, GRID_ROWS / 2, road_color))
        parts.append(_road(GRID_COLS / 2, 0, GRID_COLS / 2, GRID_ROWS, road_color))
        for col in range(1, GRID_COLS, 3):
            for row in range(1, GRID_ROWS, 3):
                if abs(col - GRID_COLS / 2) < 0.5 or abs(row - GRID_ROWS / 2) < 0.5:
                    continue  # skip road tiles
                if rng.random() < 0.75:
                    height = rng.randint(40, 130)
                    roof = "peaked" if rng.random() < 0.3 else "flat"
                    parts.append(_building(col, row, height, bldg_main, bldg_accent, roof))
        for _ in range(18):
            c = rng.uniform(0, GRID_COLS)
            r = rng.uniform(0, GRID_ROWS)
            parts.append(_tree(c, r, 1.1, tree_color, tree_shadow))
        for col in range(1, GRID_COLS, 2):
            parts.append(_streetlamp(col, GRID_ROWS / 2 - 0.3, "#FFE6A0"))

    elif biome == "snow-mountain":
        # Sparse, jagged peaks (built from tall narrow buildings with peaked roofs)
        for _ in range(14):
            c = rng.uniform(0, GRID_COLS)
            r = rng.uniform(0, GRID_ROWS)
            h = rng.randint(140, 280)
            parts.append(_building(c, r, h, bldg_main, bldg_accent, "peaked"))

    elif biome == "olive-grove":
        # Rows of olive trees in regular grid
        for col in range(1, GRID_COLS, 2):
            for row in range(1, GRID_ROWS, 2):
                parts.append(_tree(col, row, 1.5, tree_color, tree_shadow))

    elif biome == "coastal-pier":
        # Pier extending out, low coastal buildings, water reflection
        # Water band (already in ground gradient)
        for col in range(2, GRID_COLS - 2, 3):
            row = 2
            parts.append(_building(col, row, rng.randint(30, 70), bldg_main, bldg_accent, "flat"))
        # Pier
        for col in range(int(GRID_COLS / 2) - 4, int(GRID_COLS / 2) + 4):
            parts.append(_building(col, GRID_ROWS - 3, 6, p[3] if len(p) > 3 else bldg_main, bldg_accent, "flat"))
        # Boats / lamps
        for _ in range(6):
            c = rng.uniform(0, GRID_COLS)
            parts.append(_streetlamp(c, GRID_ROWS - 1, "#FFE6A0"))

    elif biome == "river-valley":
        # Maryland — Chesapeake watershed
        # River as diagonal road
        parts.append(_road(-2, 4, GRID_COLS + 2, 8, "#3A5C66"))
        parts.append(_road(-2, 4.5, GRID_COLS + 2, 8.5, "#456A75"))
        for _ in range(40):
            c = rng.uniform(0, GRID_COLS)
            r = rng.uniform(0, GRID_ROWS)
            if abs(r - (4 + (c / GRID_COLS) * 4)) < 1.5:
                continue
            scale = rng.uniform(0.9, 1.4)
            parts.append(_tree(c, r, scale, tree_color, tree_shadow))
        for col in range(2, GRID_COLS, 5):
            row = 9
            parts.append(_building(col, row, rng.randint(35, 75), bldg_main, bldg_accent, "peaked"))

    elif biome == "vineyard":
        for col in range(1, GRID_COLS, 1):
            for row in range(1, GRID_ROWS, 2):
                parts.append(_tree(col, row, 0.7, tree_color, tree_shadow))

    elif biome == "wheat-field":
        # Tiny vertical strokes for wheat
        for _ in range(900):
            c = rng.uniform(0, GRID_COLS)
            r = rng.uniform(0, GRID_ROWS)
            x, y = _iso_point(c, r)
            parts.append(f'<rect x="{x}" y="{y - 6}" width="0.6" height="6" fill="{tree_color}" opacity="0.7"/>')

    elif biome == "rooftop-garden":
        # Brooklyn — brownstone roofs with planters
        for col in range(0, GRID_COLS, 2):
            for row in range(0, GRID_ROWS, 2):
                if rng.random() < 0.8:
                    parts.append(_building(col, row, rng.randint(70, 150), bldg_main, bldg_accent, "flat"))
                    # planter on roof
                    if rng.random() < 0.5:
                        parts.append(_tree(col + 0.6, row + 0.6, 0.7, tree_color, tree_shadow))

    elif biome == "stone-courtyard":
        # Bethlehem — low stone walls, central well
        for col in range(2, GRID_COLS, 4):
            for row in range(2, GRID_ROWS, 4):
                parts.append(_building(col, row, rng.randint(20, 45), bldg_main, bldg_accent, "flat"))
        # Central well
        cx, cy = _iso_point(GRID_COLS / 2, GRID_ROWS / 2)
        parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="22" ry="9" fill="{p[1]}" stroke="{p[0]}" stroke-width="2"/>')

    return "\n".join(parts)


def render_world(world: World) -> str:
    """Return a self-contained SVG for one world tile."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  {_sky_gradient(world)}
  {_sky_and_horizon(world)}
  {_fog_band(world)}
  {_biome_scene(world)}
  {_grain_overlay(world)}
  {_signature(world)}
</svg>
"""


def generate_all(out_dir: Path, worlds: Iterable[World] = ALL_WORLDS) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for world in worlds:
        svg = render_world(world)
        path = out_dir / f"{world.id}-{world.name.lower().replace(' ', '-')}.svg"
        path.write_text(svg)
        paths.append(path)
    return paths


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent.parent / "artifacts" / "game" / "genesis" / "worlds"
    paths = generate_all(out)
    print(f"Generated {len(paths)} world tiles in {out}")
    for p in paths:
        print(" -", p.name)
