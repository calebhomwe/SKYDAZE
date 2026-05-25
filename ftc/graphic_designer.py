"""Print-ready graphic design SVG generator for FTC FULL TIME CHRISTIAN.

Each design is a standalone, self-contained SVG intended for direct application
to any product (t-shirt, hat, hoodie, tote). Designs are 2400×2400 at 96dpi
equivalent — sufficient for DTG/screen print at up to 12" diameter.

Design taxonomy:
  - typography  : text-dominant compositions (wordmarks, quotes, stacked type)
  - symbol      : mark-dominant (abstract geometry, sacred motifs)
  - combined    : typography + symbol layered compositions
  - texture     : surface-treatment-focused (distressed, noise, halftone)

Combinatorial axis:
  layout × typography_style × symbol_family × palette × treatment
  → ~1 000 unique, deterministic designs from a seed.
"""

from __future__ import annotations

import hashlib
import math
import random
import re
from dataclasses import dataclass
from typing import Callable


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _rng(seed: str) -> random.Random:
    digest = int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8], "big")
    return random.Random(digest)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _luminance(h: str) -> float:
    r, g, b = (_c / 255 for _c in _hex_to_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast_color(bg: str) -> str:
    return "#F5F0E8" if _luminance(bg) < 0.4 else "#1A1814"


# ---------------------------------------------------------------------------
# Brand color palettes  (earth-neutral, monochrome, triadic-restrained)
# ---------------------------------------------------------------------------

PALETTES: list[dict] = [
    # ---- monochrome --------------------------------------------------------
    {"name": "obsidian-bone",     "bg": "#111111", "fg": "#EDE8DF", "accent": "#888880", "family": "mono"},
    {"name": "ash-white",         "bg": "#1C1C1C", "fg": "#F0EDE6", "accent": "#7A7A78", "family": "mono"},
    {"name": "slate-cream",       "bg": "#2A2E32", "fg": "#F3EFE7", "accent": "#9EA4AA", "family": "mono"},
    {"name": "bone-ink",          "bg": "#F0EBE1", "fg": "#1A1714", "accent": "#8C8880", "family": "mono"},
    {"name": "oat-charcoal",      "bg": "#E8E2D8", "fg": "#232220", "accent": "#7A776E", "family": "mono"},
    {"name": "white-graphite",    "bg": "#FAFAF8", "fg": "#222222", "accent": "#8A8A8A", "family": "mono"},
    # ---- earth-neutral -----------------------------------------------------
    {"name": "rust-bone",         "bg": "#3D1F12", "fg": "#EDE4D2", "accent": "#B5623E", "family": "earth"},
    {"name": "ember-ash",         "bg": "#2E1C0A", "fg": "#E8D9C2", "accent": "#C47A3A", "family": "earth"},
    {"name": "moss-oat",          "bg": "#1A2318", "fg": "#E5E0D2", "accent": "#4A6840", "family": "earth"},
    {"name": "walnut-cream",      "bg": "#261810", "fg": "#EDE4D6", "accent": "#8C5E38", "family": "earth"},
    {"name": "sand-ink",          "bg": "#D8CAB0", "fg": "#1A1410", "accent": "#826C50", "family": "earth"},
    {"name": "stone-ember",       "bg": "#3A3430", "fg": "#E2DDD4", "accent": "#A87B5A", "family": "earth"},
    # ---- triadic-restrained ------------------------------------------------
    {"name": "navy-rust-bone",    "bg": "#0D1525", "fg": "#E8E2D4", "accent": "#9E4A2A", "family": "triadic"},
    {"name": "forest-sand-ink",   "bg": "#152418", "fg": "#E0DAC8", "accent": "#9E8050", "family": "triadic"},
    {"name": "plum-gold-cream",   "bg": "#1E1025", "fg": "#EDE5D2", "accent": "#B0943A", "family": "triadic"},
    {"name": "teal-rust-stone",   "bg": "#0D2222", "fg": "#E2DDD2", "accent": "#B05A30", "family": "triadic"},
]


# ---------------------------------------------------------------------------
# Typography styles
# ---------------------------------------------------------------------------

FONTS: list[dict] = [
    {"name": "grotesque",      "family": "Arial Black, Impact, sans-serif",       "weight": "900", "tracking": "0.08em"},
    {"name": "condensed",      "family": "'Arial Narrow', Arial, sans-serif",     "weight": "700", "tracking": "0.06em"},
    {"name": "mono",           "family": "'Courier New', Courier, monospace",     "weight": "700", "tracking": "0.12em"},
    {"name": "humanist-serif", "family": "Georgia, 'Times New Roman', serif",     "weight": "700", "tracking": "0.04em"},
    {"name": "display-caps",   "family": "Impact, 'Arial Black', sans-serif",     "weight": "900", "tracking": "0.15em"},
    {"name": "editorial",      "family": "Georgia, 'Times New Roman', serif",     "weight": "400", "tracking": "0.20em"},
    {"name": "block",          "family": "'Arial Black', Arial, sans-serif",      "weight": "900", "tracking": "0.02em"},
    {"name": "fine",           "family": "Georgia, serif",                        "weight": "300", "tracking": "0.25em"},
]


# ---------------------------------------------------------------------------
# Symbol library (all SVG path data, centered around 0,0 for easy placement)
# ---------------------------------------------------------------------------

def _cross(size: float = 60, thin: float = 0.22) -> str:
    """Latin cross — FTC primary sacred mark."""
    v = size
    h = size * thin
    return (
        f"M {-h/2} {-v} L {h/2} {-v} L {h/2} {-h/2} "
        f"L {v*0.35} {-h/2} L {v*0.35} {h/2} L {h/2} {h/2} "
        f"L {h/2} {v} L {-h/2} {v} L {-h/2} {h/2} "
        f"L {-v*0.35} {h/2} L {-v*0.35} {-h/2} L {-h/2} {-h/2} Z"
    )


def _anchor(size: float = 60) -> str:
    """Anchor — hope / foundational metaphor."""
    s = size
    return (
        f"M 0 {-s} L 0 {s} "
        f"M {-s*0.5} {s*0.5} L {s*0.5} {s*0.5} "
        f"M 0 {-s} C {-s*0.4} {-s*0.4} {-s*0.4} {-s*0.1} {-s*0.55} {0} "
        f"C {-s*0.4} {s*0.2} {-s*0.35} {s*0.35} {0} {s*0.35} "
        f"C {s*0.35} {s*0.35} {s*0.4} {s*0.2} {s*0.55} {0} "
        f"C {s*0.4} {-s*0.1} {s*0.4} {-s*0.4} {0} {-s} Z"
    )


def _cornerstone(size: float = 60) -> str:
    """Cornerstone / foundation block — architectural metaphor."""
    s = size * 0.9
    return (
        f"M {-s} {-s*0.4} L {0} {-s*0.75} L {s} {-s*0.4} "
        f"L {s} {s*0.55} L {0} {s*0.55} L {0} {s*0.05} "
        f"L {-s} {s*0.05} Z "
        f"M {0} {-s*0.75} L {0} {s*0.05}"
    )


def _flame(size: float = 60) -> str:
    """Flame — Spirit / refining fire."""
    s = size
    return (
        f"M 0 {-s} C {-s*0.1} {-s*0.6} {-s*0.5} {-s*0.4} {-s*0.3} {0} "
        f"C {-s*0.45} {-s*0.1} {-s*0.5} {s*0.3} {0} {s} "
        f"C {s*0.5} {s*0.3} {s*0.45} {-s*0.1} {s*0.3} {0} "
        f"C {s*0.5} {-s*0.4} {s*0.1} {-s*0.6} {0} {-s} Z"
    )


def _dove(size: float = 60) -> str:
    """Dove silhouette — peace / Spirit."""
    s = size
    return (
        f"M {-s*0.8} {s*0.1} C {-s*0.6} {-s*0.2} {-s*0.2} {-s*0.5} {0} {-s*0.3} "
        f"C {s*0.3} {-s*0.55} {s*0.7} {-s*0.4} {s*0.85} {0} "
        f"C {s*0.6} {s*0.1} {s*0.3} {s*0.05} {s*0.1} {s*0.3} "
        f"C {-s*0.1} {s*0.5} {-s*0.5} {s*0.5} {-s*0.7} {s*0.2} "
        f"C {-s*0.9} {s*0.1} {-s*0.85} {-s*0.05} {-s*0.8} {s*0.1} Z "
        f"M {s*0.1} {s*0.3} L {-s*0.1} {s*0.7}"
    )


def _triangle(size: float = 60) -> str:
    """Equilateral triangle — Trinity / mountain."""
    s = size
    h = s * math.sqrt(3) / 2
    return f"M 0 {-h*0.67} L {s*0.5} {h*0.33} L {-s*0.5} {h*0.33} Z"


def _circle_ring(size: float = 60, stroke_w: float = 6) -> str:
    """Circle / ring — wholeness, eternal."""
    r = size - stroke_w
    return f"M {r} 0 A {r} {r} 0 1 0 {-r} 0 A {r} {r} 0 1 0 {r} 0"


def _eye(size: float = 60) -> str:
    """Eye of providence — all-seeing / awareness."""
    s = size
    iris = s * 0.28
    return (
        f"M {-s} 0 C {-s*0.5} {-s*0.5} {s*0.5} {-s*0.5} {s} 0 "
        f"C {s*0.5} {s*0.5} {-s*0.5} {s*0.5} {-s} 0 Z "
        f"M {iris} 0 A {iris} {iris} 0 1 0 {-iris} 0 A {iris} {iris} 0 1 0 {iris} 0"
    )


def _infinity(size: float = 60) -> str:
    """Infinity / eternity loop."""
    s = size * 0.6
    r = s * 0.45
    return (
        f"M {-s} 0 C {-s} {-r} {-r} {-r} 0 0 "
        f"C {r} {r} {s} {r} {s} 0 "
        f"C {s} {-r} {r} {-r} 0 0 "
        f"C {-r} {r} {-s} {r} {-s} 0 Z"
    )


def _wheat(size: float = 60) -> str:
    """Wheat stalk — harvest / abundance."""
    s = size
    return (
        f"M 0 {-s} L 0 {s*0.5} "
        f"M 0 {-s*0.5} C {-s*0.3} {-s*0.7} {-s*0.4} {-s*0.3} {-s*0.15} {-s*0.15} "
        f"M 0 {-s*0.5} C {s*0.3} {-s*0.7} {s*0.4} {-s*0.3} {s*0.15} {-s*0.15} "
        f"M 0 {-s*0.15} C {-s*0.3} {-s*0.35} {-s*0.4} {0} {-s*0.15} {s*0.1} "
        f"M 0 {-s*0.15} C {s*0.3} {-s*0.35} {s*0.4} {0} {s*0.15} {s*0.1}"
    )


def _key(size: float = 60) -> str:
    """Key — access / authority."""
    s = size
    head_r = s * 0.35
    return (
        f"M {-s*0.05} {s*0.05} L {-s*0.05} {s*0.85} "
        f"L {s*0.15} {s*0.85} L {s*0.15} {s*0.65} L {s*0.25} {s*0.65} L {s*0.25} {s*0.5} L {s*0.15} {s*0.5} "
        f"L {s*0.05} {s*0.05} "
        f"M 0 {-s*0.1} A {head_r} {head_r} 0 1 0 {head_r*0.7} {-head_r*0.7}"
    )


def _water_drop(size: float = 60) -> str:
    """Water drop — Living Water / baptism."""
    s = size
    return (
        f"M 0 {-s} C {s*0.5} {-s*0.2} {s*0.65} {s*0.3} {s*0.4} {s*0.55} "
        f"C {s*0.2} {s*0.85} {-s*0.2} {s*0.85} {-s*0.4} {s*0.55} "
        f"C {-s*0.65} {s*0.3} {-s*0.5} {-s*0.2} {0} {-s} Z"
    )


def _shield(size: float = 60) -> str:
    """Shield — faith / protection."""
    s = size
    return (
        f"M {-s*0.8} {-s*0.7} L {s*0.8} {-s*0.7} "
        f"L {s*0.8} {s*0.1} C {s*0.8} {s*0.6} {0} {s} {0} {s} "
        f"C {0} {s} {-s*0.8} {s*0.6} {-s*0.8} {s*0.1} Z"
    )


def _wave(size: float = 60, periods: int = 2) -> str:
    """Wave — grace / tide / Spirit movement."""
    s = size
    step = (s * 2) / (periods * 4)
    pts = []
    x = -s
    pts.append(f"M {-s} 0")
    for i in range(periods * 2):
        cx1 = x + step
        cy1 = -s * 0.5 if i % 2 == 0 else s * 0.5
        cx2 = x + step * 2
        cy2 = -s * 0.5 if i % 2 == 0 else s * 0.5
        x2 = x + step * 2
        pts.append(f"C {cx1} {cy1} {cx2} {cy2} {x2} 0")
        x = x2
    return " ".join(pts)


def _star_of_david(size: float = 60) -> str:
    """Star of David — heritage / covenant."""
    s = size * 0.9
    pts1 = []
    pts2 = []
    for i in range(3):
        angle = math.pi / 2 + i * (2 * math.pi / 3)
        x, y = s * math.cos(angle), s * math.sin(angle)
        pts1.append(f"{x:.2f},{y:.2f}")
    for i in range(3):
        angle = -math.pi / 2 + i * (2 * math.pi / 3)
        x, y = s * math.cos(angle), s * math.sin(angle)
        pts2.append(f"{x:.2f},{y:.2f}")
    return f"M {pts1[0]} L {pts1[1]} L {pts1[2]} Z M {pts2[0]} L {pts2[1]} L {pts2[2]} Z"


def _pillar(size: float = 60) -> str:
    """Column / pillar — strength / foundation."""
    s = size
    w = s * 0.35
    return (
        f"M {-w} {-s} L {w} {-s} L {w} {s} L {-w} {s} Z "
        f"M {-s*0.55} {-s} L {s*0.55} {-s} L {s*0.55} {-s*0.82} L {-s*0.55} {-s*0.82} Z "
        f"M {-s*0.55} {s} L {s*0.55} {s} L {s*0.55} {s*0.82} L {-s*0.55} {s*0.82} Z"
    )


def _chi_rho(size: float = 60) -> str:
    """Chi-Rho — early Christian monogram."""
    s = size
    r = s * 0.4
    loop_r = s * 0.22
    return (
        f"M {-s*0.55} {-s*0.55} L {s*0.55} {s*0.55} "
        f"M {s*0.55} {-s*0.55} L {-s*0.55} {s*0.55} "
        f"M 0 {-s} L 0 {s*0.2} "
        f"M {-loop_r} {-s*0.25} A {loop_r} {loop_r} 0 1 1 {loop_r} {-s*0.25}"
    )


def _arch(size: float = 60) -> str:
    """Gothic arch — cathedral / sacred architecture."""
    s = size
    w = s * 0.7
    return (
        f"M {-w} {s} L {-w} 0 "
        f"C {-w} {-s} {w} {-s} {w} {0} "
        f"L {w} {s}"
    )


SYMBOLS: list[dict] = [
    {"name": "cross",         "path_fn": _cross,        "stroke_width": 0,   "filled": True},
    {"name": "anchor",        "path_fn": _anchor,       "stroke_width": 4,   "filled": False},
    {"name": "cornerstone",   "path_fn": _cornerstone,  "stroke_width": 3,   "filled": True},
    {"name": "flame",         "path_fn": _flame,        "stroke_width": 0,   "filled": True},
    {"name": "dove",          "path_fn": _dove,         "stroke_width": 0,   "filled": True},
    {"name": "triangle",      "path_fn": _triangle,     "stroke_width": 0,   "filled": True},
    {"name": "circle-ring",   "path_fn": _circle_ring,  "stroke_width": 6,   "filled": False},
    {"name": "eye",           "path_fn": _eye,          "stroke_width": 0,   "filled": True},
    {"name": "infinity",      "path_fn": _infinity,     "stroke_width": 0,   "filled": True},
    {"name": "wheat",         "path_fn": _wheat,        "stroke_width": 3,   "filled": False},
    {"name": "key",           "path_fn": _key,          "stroke_width": 3,   "filled": False},
    {"name": "water-drop",    "path_fn": _water_drop,   "stroke_width": 0,   "filled": True},
    {"name": "shield",        "path_fn": _shield,       "stroke_width": 0,   "filled": True},
    {"name": "wave",          "path_fn": _wave,         "stroke_width": 3,   "filled": False},
    {"name": "star-of-david", "path_fn": _star_of_david,"stroke_width": 0,   "filled": True},
    {"name": "pillar",        "path_fn": _pillar,       "stroke_width": 0,   "filled": True},
    {"name": "chi-rho",       "path_fn": _chi_rho,      "stroke_width": 3.5, "filled": False},
    {"name": "arch",          "path_fn": _arch,         "stroke_width": 4,   "filled": False},
]


# ---------------------------------------------------------------------------
# Brand wordmarks and text lines
# ---------------------------------------------------------------------------

BRAND_LINES: list[str] = [
    "FULL TIME CHRISTIAN",
    "FTC",
    "FULL TIME",
    "CHRISTIAN",
]

HEADLINE_WORDS: list[str] = [
    "CORNERSTONE", "VIGIL", "VEIL", "EMBER", "THRESHOLD",
    "CLOISTER", "VESPERS", "MATINS", "LECTIONARY", "SOJOURN",
    "ANCHOR", "REFUGE", "WITNESS", "INHERITANCE", "WAYFARER",
    "HEWN", "SOWN", "BORNE", "MENDED", "YOKE",
    "LIGHTHOUSE", "STILLWATER", "TABERNACLE", "CANTOR", "LINTEL",
    "PLUMBLINE", "ANTIPHON", "COMPLINE", "SALT", "LINEN",
    "FOUNDLING", "LAMPBLACK", "HYMNAL", "GARRISON", "ECHO",
    "QUIET HOUR", "DRAWN WATER", "FIELD MARKER", "BELL TOWER", "OPEN HAND",
    "CLOTH AND VOW", "INNER ROOM", "LIVING WATER", "ASH TUESDAY", "WHEATFIELD",
]

THEOLOGICAL_LINES: list[str] = [
    "WHAT ENDURES IS WHAT LEARNED TO WAIT",
    "THE WELL DOES NOT ARGUE — IT OVERFLOWS",
    "BREAD BROKEN IS STILL BREAD",
    "IRON DOES NOT FORGET THE FORGE",
    "SALT IS THE PATIENCE OF FIRE",
    "RIVERS DO NOT MEASURE THEIR OWN DEPTH",
    "A DOOR KNOWS BOTH ROOMS",
    "WHAT THE BUILDERS REFUSED",
    "LIGHT REVEALS WHAT SHADOW AGREES TO RELEASE",
    "MERCY KEEPS A KEY THE LOCK CANNOT REMEMBER",
    "EVERY THRESHOLD IS A VOW",
    "THE UNWRITTEN LETTER IS THE CLEANEST ANSWER",
    "FOUNDATIONS ARGUE LAST",
    "A VIGIL KEEPS ITS OWN WARMTH",
    "DUST DOES NOT NEGOTIATE — IT RETURNS",
    "LINEN KNOWS THE PRAYER",
    "SILENCE IS A HELD INSTRUMENT",
    "A PSALM DOES NOT NEED TO LEAVE THE THROAT",
    "WHAT YOU CARRY SHAPES THE ROOMS YOU ENTER",
    "THE GARDEN REMEMBERS THE GARDENER",
]

SUBTITLE_LINES: list[str] = [
    "EST. IN FAITH", "LUXURY STREETWEAR", "MADE IN GRACE",
    "SINCE THE BEGINNING", "FOR THE CALLED", "WALK IN TRUTH",
    "GARMENT WASHED", "HEAVYWEIGHT COTTON", "THEOLOGY IN FABRIC",
    "BORN OF FIRE", "REFINED BY GRACE", "CARRY THE WEIGHT",
    "QUIET ARCHITECTURE", "DIVINE RESTRAINT", "SACRED GEOMETRY",
    "SCRIPTURE-GROUNDED", "PATTERN OF GRACE", "THE NARROW WAY",
]


# ---------------------------------------------------------------------------
# Layout engines: each returns partial SVG content
# ---------------------------------------------------------------------------

CANVAS = 2400
CENTER = CANVAS // 2


def _svg_header(bg: str, title: str) -> str:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {CANVAS} {CANVAS}" width="{CANVAS}" height="{CANVAS}" '
        f'role="img" aria-label="{title}">\n'
        f'  <rect width="{CANVAS}" height="{CANVAS}" fill="{bg}"/>\n'
    )


def _svg_footer() -> str:
    return "</svg>"


def _symbol_element(
    sym: dict,
    cx: float,
    cy: float,
    size: float,
    color: str,
    opacity: float = 1.0,
    stroke_scale: float = 1.0,
) -> str:
    path_d = sym["path_fn"](size)
    sw = sym["stroke_width"] * stroke_scale * (size / 60)
    if sym["filled"] and sw == 0:
        return (
            f'  <path d="{path_d}" fill="{color}" opacity="{opacity:.2f}" '
            f'transform="translate({cx:.1f},{cy:.1f})"/>\n'
        )
    elif sym["filled"]:
        return (
            f'  <path d="{path_d}" fill="{color}" stroke="{color}" '
            f'stroke-width="{sw:.1f}" opacity="{opacity:.2f}" '
            f'transform="translate({cx:.1f},{cy:.1f})"/>\n'
        )
    else:
        return (
            f'  <path d="{path_d}" fill="none" stroke="{color}" '
            f'stroke-width="{sw:.1f}" stroke-linecap="round" stroke-linejoin="round" '
            f'opacity="{opacity:.2f}" '
            f'transform="translate({cx:.1f},{cy:.1f})"/>\n'
        )


def _text_element(
    text: str,
    x: float,
    y: float,
    font: dict,
    size: float,
    color: str,
    anchor: str = "middle",
    opacity: float = 1.0,
    rotation: float = 0.0,
) -> str:
    transform = f'transform="rotate({rotation:.1f},{x:.1f},{y:.1f})"' if rotation else ""
    return (
        f'  <text x="{x:.1f}" y="{y:.1f}" '
        f'font-family="{font["family"]}" '
        f'font-size="{size:.1f}" '
        f'font-weight="{font["weight"]}" '
        f'letter-spacing="{font["tracking"]}" '
        f'fill="{color}" '
        f'text-anchor="{anchor}" '
        f'dominant-baseline="middle" '
        f'opacity="{opacity:.2f}" '
        f'{transform}>'
        f'{text}'
        f'</text>\n'
    )


def _divider_line(x1: float, y1: float, x2: float, y2: float, color: str, width: float = 3, opacity: float = 0.6) -> str:
    return (
        f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{width:.1f}" opacity="{opacity:.2f}"/>\n'
    )


def _rect_element(x: float, y: float, w: float, h: float, color: str, opacity: float = 1.0, fill: bool = True, stroke_w: float = 3) -> str:
    if fill:
        return f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{color}" opacity="{opacity:.2f}"/>\n'
    return (
        f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'fill="none" stroke="{color}" stroke-width="{stroke_w:.1f}" opacity="{opacity:.2f}"/>\n'
    )


def _circle_element(cx: float, cy: float, r: float, color: str, opacity: float = 1.0, fill: bool = True, stroke_w: float = 3) -> str:
    if fill:
        return f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}" opacity="{opacity:.2f}"/>\n'
    return (
        f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
        f'fill="none" stroke="{color}" stroke-width="{stroke_w:.1f}" opacity="{opacity:.2f}"/>\n'
    )


def _noise_filter(seed_val: int = 42) -> str:
    """SVG filter for subtle vintage noise/grain texture."""
    return (
        f'  <filter id="grain" x="0" y="0" width="100%" height="100%" color-interpolation-filters="linearRGB">\n'
        f'    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" seed="{seed_val}" result="noise"/>\n'
        f'    <feColorMatrix in="noise" type="saturate" values="0" result="grayNoise"/>\n'
        f'    <feBlend in="SourceGraphic" in2="grayNoise" mode="multiply" result="blended"/>\n'
        f'    <feComponentTransfer in="blended">\n'
        f'      <feFuncA type="linear" slope="0.9"/>\n'
        f'    </feComponentTransfer>\n'
        f'  </filter>\n'
        f'  <rect width="{CANVAS}" height="{CANVAS}" filter="url(#grain)" opacity="0.08" fill="white"/>\n'
    )


# ---------------------------------------------------------------------------
# Layout functions — each takes rng + palette + font + symbol → SVG body
# ---------------------------------------------------------------------------

def _layout_wordmark_stacked(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Large stacked wordmark — primary brand identity."""
    fg, accent = pal["fg"], pal["accent"]
    parts: list[str] = []

    main_size = rng.randint(160, 240)
    sub_size = int(main_size * 0.28)

    headline = rng.choice(HEADLINE_WORDS)
    subtitle = rng.choice(SUBTITLE_LINES)
    brand = "FULL TIME CHRISTIAN"

    y_brand = CENTER - int(main_size * 1.1)
    y_headline = CENTER
    y_sub = CENTER + int(main_size * 0.8)

    parts.append(_text_element(brand, CENTER, y_brand, font, main_size * 0.38, accent))
    parts.append(_divider_line(CENTER - 500, y_brand + 60, CENTER + 500, y_brand + 60, fg, 2, 0.5))
    parts.append(_text_element(headline, CENTER, y_headline, font, main_size, fg))
    parts.append(_divider_line(CENTER - 500, y_sub - 50, CENTER + 500, y_sub - 50, fg, 2, 0.5))
    parts.append(_text_element(subtitle, CENTER, y_sub, font, sub_size, accent))
    return "".join(parts)


def _layout_symbol_dominant(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Large central symbol with minimal text."""
    fg, accent = pal["fg"], pal["accent"]
    parts: list[str] = []

    sym_size = rng.randint(500, 750)
    label_size = rng.randint(60, 100)

    parts.append(_symbol_element(sym, CENTER, CENTER - 100, sym_size, fg, 0.95))

    if rng.random() > 0.4:
        parts.append(_circle_element(CENTER, CENTER - 100, sym_size + 80, fg, 0.08, True))

    brand = rng.choice(["FTC", "FULL TIME CHRISTIAN"])
    parts.append(_text_element(brand, CENTER, CENTER + sym_size + 150, font, label_size, accent))

    if rng.random() > 0.5:
        subtitle = rng.choice(SUBTITLE_LINES)
        parts.append(_text_element(subtitle, CENTER, CENTER + sym_size + 260, font, int(label_size * 0.55), fg, opacity=0.7))

    return "".join(parts)


def _layout_typographic_poster(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Full-canvas typographic composition — editorial poster style."""
    fg, accent = pal["fg"], pal["accent"]
    parts: list[str] = []

    quote = rng.choice(THEOLOGICAL_LINES)
    words = quote.split()
    lines: list[str] = []
    current: list[str] = []
    target_lines = rng.randint(2, 4)
    per_line = max(1, len(words) // target_lines)
    for i, w in enumerate(words):
        current.append(w)
        if len(current) >= per_line and i < len(words) - 1:
            lines.append(" ".join(current))
            current = []
    if current:
        lines.append(" ".join(current))

    total = len(lines)
    line_size = max(80, min(220, int(1600 / (max(len(l) for l in lines) * 0.55))))
    line_height = int(line_size * 1.2)
    y_start = CENTER - (total * line_height) // 2

    for i, line in enumerate(lines):
        y = y_start + i * line_height
        opacity = 1.0 - i * 0.03
        parts.append(_text_element(line, CENTER, y, font, line_size, fg, opacity=opacity))

    # decorative accent bar
    bar_y = y_start - 80
    parts.append(_rect_element(CENTER - 200, bar_y, 400, 8, accent))
    bar_y2 = y_start + total * line_height + 40
    parts.append(_rect_element(CENTER - 200, bar_y2, 400, 8, accent))

    brand = "FTC"
    parts.append(_text_element(brand, CENTER, bar_y2 + 100, font, 80, accent))

    return "".join(parts)


def _layout_arch_frame(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Gothic arch frame containing symbol + text."""
    fg, accent = pal["fg"], pal["accent"]
    parts: list[str] = []

    frame_h = int(CANVAS * 0.72)
    frame_w = int(CANVAS * 0.52)
    arch_x = CENTER - frame_w // 2
    arch_y = int(CANVAS * 0.14)

    # arch shape as a path
    bx, by = arch_x, arch_y
    bw, bh = frame_w, frame_h
    arch_path = (
        f"M {bx} {by + bh} L {bx} {by + bh * 0.4} "
        f"C {bx} {by} {bx + bw} {by} {bx + bw} {by + bh * 0.4} "
        f"L {bx + bw} {by + bh}"
    )
    sw = rng.randint(6, 12)
    parts.append(f'  <path d="{arch_path}" fill="none" stroke="{fg}" stroke-width="{sw}" opacity="0.85"/>\n')

    # inner symbol
    sym_size = int(min(frame_w, frame_h * 0.4) * 0.55)
    parts.append(_symbol_element(sym, CENTER, by + frame_h * 0.38, sym_size, fg))

    # divider
    div_y = by + frame_h * 0.62
    parts.append(_divider_line(bx + 60, div_y, bx + bw - 60, div_y, accent, 2))

    headline = rng.choice(HEADLINE_WORDS)
    sub_text = rng.choice(SUBTITLE_LINES)
    parts.append(_text_element(headline, CENTER, div_y + 100, font, 140, fg))
    parts.append(_text_element(sub_text, CENTER, div_y + 230, font, 65, accent))
    parts.append(_text_element("FULL TIME CHRISTIAN", CENTER, by + bh + 130, font, 75, fg))

    return "".join(parts)


def _layout_badge_circular(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Circular badge / seal — classic varsity streetwear."""
    fg, accent = pal["fg"], pal["accent"]
    parts: list[str] = []

    outer_r = 860
    inner_r = 720
    mid_r = (outer_r + inner_r) // 2

    parts.append(_circle_element(CENTER, CENTER, outer_r, fg, 0.12, True))
    parts.append(_circle_element(CENTER, CENTER, outer_r, fg, 0.9, False, stroke_w=8))
    parts.append(_circle_element(CENTER, CENTER, inner_r, fg, 0.7, False, stroke_w=3))

    sym_size = 300
    parts.append(_symbol_element(sym, CENTER, CENTER, sym_size, fg, 0.95))

    brand = "FULL TIME CHRISTIAN"
    headline = rng.choice(HEADLINE_WORDS)
    year_text = rng.choice(["EST. MMXXV", "EST. MMXXIII", "A.D. MMXXVI"])

    font_size = 90

    # Circular text approximation using letter positioning
    chars_top = list(brand)
    arc_radius = mid_r
    total_chars = len(chars_top)
    char_angle_step = math.pi / (total_chars + 1)
    start_angle = -math.pi / 2 - (total_chars / 2) * char_angle_step

    for i, ch in enumerate(chars_top):
        angle = start_angle + (i + 0.5) * char_angle_step - math.pi * 0.01
        cx = CENTER + arc_radius * math.cos(angle)
        cy = CENTER + arc_radius * math.sin(angle)
        rotation = math.degrees(angle) + 90
        parts.append(
            f'  <text x="{cx:.1f}" y="{cy:.1f}" '
            f'font-family="{font["family"]}" font-size="{font_size}" '
            f'font-weight="{font["weight"]}" fill="{fg}" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'transform="rotate({rotation:.1f},{cx:.1f},{cy:.1f})">'
            f'{ch}</text>\n'
        )

    # Bottom arc text
    chars_bot = list(year_text)
    total_bot = len(chars_bot)
    bot_step = math.pi / (total_bot + 1)
    for i, ch in enumerate(chars_bot):
        angle = math.pi / 2 + (i + 1) * bot_step - math.pi * 0.5
        cx = CENTER + arc_radius * math.cos(math.pi / 2 + (i - total_bot / 2) * bot_step)
        cy = CENTER + arc_radius * math.sin(math.pi / 2 + (i - total_bot / 2) * bot_step)
        rotation = math.degrees(math.pi / 2 + (i - total_bot / 2) * bot_step) - 90
        parts.append(
            f'  <text x="{cx:.1f}" y="{cy:.1f}" '
            f'font-family="{font["family"]}" font-size="{font_size}" '
            f'font-weight="{font["weight"]}" fill="{accent}" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'transform="rotate({rotation:.1f},{cx:.1f},{cy:.1f})">'
            f'{ch}</text>\n'
        )

    parts.append(_text_element(headline, CENTER, CENTER + 450, font, 120, fg))

    return "".join(parts)


def _layout_minimal_mark(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Hyper-minimal single mark + wordmark — Fear of God / Lemaire register."""
    fg, accent = pal["fg"], pal["accent"]
    parts: list[str] = []

    sym_size = rng.randint(280, 480)
    label_size = rng.randint(72, 120)

    # Off-center asymmetric composition
    offset_x = rng.randint(-120, 120)
    offset_y = rng.randint(-200, 0)

    parts.append(_symbol_element(sym, CENTER + offset_x, CENTER + offset_y, sym_size, fg, 1.0))

    brand_y = CENTER + offset_y + sym_size + int(label_size * 1.5)
    brand = rng.choice(["FTC", "FULL TIME CHRISTIAN"])
    parts.append(_text_element(brand, CENTER + offset_x, brand_y, font, label_size, fg))

    if rng.random() > 0.5:
        sub = rng.choice(SUBTITLE_LINES)
        parts.append(_text_element(sub, CENTER + offset_x, brand_y + int(label_size * 1.2), font, int(label_size * 0.45), accent))

    return "".join(parts)


def _layout_varsity_block(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Athletic varsity-style composition with block letter."""
    fg, accent, bg = pal["fg"], pal["accent"], pal["bg"]
    parts: list[str] = []

    letter = rng.choice(["F", "T", "C", "FTC"])
    letter_size = rng.randint(800, 1100) if len(letter) == 1 else rng.randint(400, 600)

    # background fill block
    block_h = int(CANVAS * 0.58)
    block_y = int(CANVAS * 0.21)
    parts.append(_rect_element(0, block_y, CANVAS, block_h, fg, 1.0, True))

    # Letter in contrast
    contrast = _contrast_color(fg)
    parts.append(_text_element(letter, CENTER, CENTER + 40, font, letter_size, contrast, opacity=0.15))
    parts.append(_text_element(letter, CENTER, CENTER + 40, font, letter_size, bg))

    # top brand
    parts.append(_text_element("FULL TIME", CENTER, block_y - 100, font, 160, fg))
    parts.append(_text_element("CHRISTIAN", CENTER, block_y - 100 + 180, font, 160, fg))

    # bottom sub
    sub = rng.choice(SUBTITLE_LINES)
    parts.append(_text_element(sub, CENTER, block_y + block_h + 100, font, 80, accent))

    # sym overlay
    if rng.random() > 0.4:
        sym_size = 180
        parts.append(_symbol_element(sym, CENTER + 400, block_y + block_h - 200, sym_size, accent, 0.85))

    return "".join(parts)


def _layout_quote_banner(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Oversized quote / scripture fragment with banner accent."""
    fg, accent = pal["fg"], pal["accent"]
    parts: list[str] = []

    quote = rng.choice(THEOLOGICAL_LINES)
    headline = rng.choice(HEADLINE_WORDS)

    # Accent banner bar
    banner_h = 160
    banner_y = int(CANVAS * 0.28)
    parts.append(_rect_element(0, banner_y, CANVAS, banner_h, accent, 1.0, True))
    parts.append(_text_element(headline, CENTER, banner_y + banner_h // 2, font, 120, _contrast_color(accent)))

    # Quote below
    words = quote.split()
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        cur.append(w)
        if len(cur) >= 3:
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))

    y_q = banner_y + banner_h + 120
    q_size = 95
    for i, line in enumerate(lines):
        parts.append(_text_element(line, CENTER, y_q + i * 115, font, q_size, fg))

    # Small symbol
    sym_size = 100
    parts.append(_symbol_element(sym, CENTER, y_q + len(lines) * 115 + 160, sym_size, accent))

    # brand footer
    parts.append(_text_element("FULL TIME CHRISTIAN", CENTER, CANVAS - 200, font, 80, fg, opacity=0.8))
    parts.append(_text_element("FTC", CENTER, CANVAS - 100, font, 55, accent))

    return "".join(parts)


def _layout_grid_repeat(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Grid of repeated symbols — all-over print / pattern tile."""
    fg, accent = pal["fg"], pal["accent"]
    parts: list[str] = []

    rows = rng.randint(4, 6)
    cols = rng.randint(4, 6)
    cell_w = CANVAS / cols
    cell_h = CANVAS / rows
    sym_size = min(cell_w, cell_h) * 0.32

    for r in range(rows):
        for c in range(cols):
            cx = cell_w * (c + 0.5)
            cy = cell_h * (r + 0.5)
            opacity = 0.6 + rng.uniform(-0.15, 0.25)
            color = fg if rng.random() > 0.3 else accent
            parts.append(_symbol_element(sym, cx, cy, sym_size, color, opacity))

    # Central text overlay
    headline = rng.choice(HEADLINE_WORDS)
    parts.append(_text_element(headline, CENTER, CENTER, font, 200, pal["bg"], opacity=0.92))
    parts.append(_text_element("FULL TIME CHRISTIAN", CENTER, CENTER + 230, font, 80, pal["bg"], opacity=0.85))

    return "".join(parts)


def _layout_diagonal_stack(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Diagonal text stack — dynamic energy."""
    fg, accent = pal["fg"], pal["accent"]
    parts: list[str] = []

    rotation = rng.choice([-15, -10, -8, 8, 10, 15])
    sizes = [rng.randint(180, 320), rng.randint(120, 200), rng.randint(80, 140)]
    words = ["FULL", "TIME", "CHRISTIAN"]

    y_positions = [CENTER - 280, CENTER, CENTER + 280]
    for i, (word, size, y) in enumerate(zip(words, sizes, y_positions)):
        opacity = 1.0 - i * 0.08
        rot = rotation * (0.5 + i * 0.25)
        parts.append(_text_element(word, CENTER, y, font, size, fg if i % 2 == 0 else accent, rotation=rot, opacity=opacity))

    if rng.random() > 0.4:
        sym_size = 160
        parts.append(_symbol_element(sym, CENTER + 500, CENTER - 400, sym_size, accent, 0.6))

    sub = rng.choice(SUBTITLE_LINES)
    parts.append(_text_element(sub, CENTER, CANVAS - 180, font, 70, accent))

    return "".join(parts)


def _layout_cross_center(rng: random.Random, pal: dict, font: dict, sym: dict) -> str:
    """Cross-centered composition — brand anchor."""
    fg, accent = pal["fg"], pal["accent"]
    parts: list[str] = []

    # Large bold cross always centered
    cross_size = rng.randint(550, 750)
    cross_sym = next(s for s in SYMBOLS if s["name"] == "cross")
    parts.append(_symbol_element(cross_sym, CENTER, CENTER, cross_size, fg, 0.9))

    # text flanking
    parts.append(_text_element("FULL", CENTER - cross_size * 0.65 - 200, CENTER - 100, font, 110, fg))
    parts.append(_text_element("TIME", CENTER - cross_size * 0.65 - 200, CENTER + 100, font, 110, fg))
    parts.append(_text_element("CHRISTIAN", CENTER + cross_size * 0.65 + 220, CENTER, font, 90, fg, rotation=90))

    headline = rng.choice(HEADLINE_WORDS)
    parts.append(_text_element(headline, CENTER, CANVAS - 180, font, 95, accent))

    return "".join(parts)


LAYOUT_FUNCTIONS: list[Callable] = [
    _layout_wordmark_stacked,
    _layout_symbol_dominant,
    _layout_typographic_poster,
    _layout_arch_frame,
    _layout_badge_circular,
    _layout_minimal_mark,
    _layout_varsity_block,
    _layout_quote_banner,
    _layout_grid_repeat,
    _layout_diagonal_stack,
    _layout_cross_center,
]


# ---------------------------------------------------------------------------
# Treatment modifiers (post-composition effects)
# ---------------------------------------------------------------------------

def _apply_distress(svg: str, intensity: float = 0.5) -> str:
    """Add a vintage grain overlay filter to the whole SVG."""
    seed_val = int(intensity * 999)
    grain = (
        f'  <filter id="vgrain" x="0" y="0" width="100%" height="100%">\n'
        f'    <feTurbulence type="fractalNoise" baseFrequency="{0.5 + intensity*0.3:.2f}" numOctaves="4" seed="{seed_val}" result="n"/>\n'
        f'    <feColorMatrix in="n" type="saturate" values="0" result="gn"/>\n'
        f'    <feBlend in="SourceGraphic" in2="gn" mode="multiply" result="bl"/>\n'
        f'    <feComponentTransfer>\n'
        f'      <feFuncA type="linear" slope="0.95"/>\n'
        f'    </feComponentTransfer>\n'
        f'  </filter>\n'
        f'  <rect width="{CANVAS}" height="{CANVAS}" filter="url(#vgrain)" opacity="{intensity * 0.15:.2f}" fill="white"/>\n'
    )
    return svg.replace("</svg>", grain + "</svg>")


def _apply_halftone_accent(svg: str, accent: str, intensity: float = 0.4) -> str:
    """Subtle halftone dot pattern overlay."""
    spacing = int(40 + intensity * 20)
    pattern = (
        f'  <defs>\n'
        f'    <pattern id="halftone" x="0" y="0" width="{spacing}" height="{spacing}" patternUnits="userSpaceOnUse">\n'
        f'      <circle cx="{spacing//2}" cy="{spacing//2}" r="{spacing*0.2:.1f}" fill="{accent}" opacity="0.15"/>\n'
        f'    </pattern>\n'
        f'  </defs>\n'
        f'  <rect width="{CANVAS}" height="{CANVAS}" fill="url(#halftone)"/>\n'
    )
    return svg.replace("</svg>", pattern + "</svg>")


def _apply_outline_stroke(svg: str, fg: str) -> str:
    """Add a thin border frame."""
    margin = 80
    frame = (
        f'  <rect x="{margin}" y="{margin}" '
        f'width="{CANVAS - 2*margin}" height="{CANVAS - 2*margin}" '
        f'fill="none" stroke="{fg}" stroke-width="4" opacity="0.4"/>\n'
    )
    return svg.replace("</svg>", frame + "</svg>")


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

@dataclass
class GraphicDesign:
    id: str
    section: str
    layout: str
    palette_name: str
    font_name: str
    symbol_name: str
    treatment: str
    title: str
    svg: str
    bg_color: str
    fg_color: str

    def svg_filename(self) -> str:
        safe_id = self.id.replace(" ", "_")
        return f"{safe_id}.svg"


_TREATMENTS = ["clean", "distress-light", "distress-heavy", "halftone", "frame", "clean"]


def generate_graphic_design(design_id: str, section: str, seed: str) -> GraphicDesign:
    """Generate one deterministic print-ready graphic design SVG."""
    rng = _rng(f"{seed}|{design_id}|{section}|graphic")

    palette = rng.choice(PALETTES)
    font = rng.choice(FONTS)
    sym = rng.choice(SYMBOLS)
    layout_fn = rng.choice(LAYOUT_FUNCTIONS)
    treatment = rng.choice(_TREATMENTS)
    title_word = rng.choice(HEADLINE_WORDS)

    svg_body = _svg_header(palette["bg"], f"{design_id} {title_word}")
    svg_body += layout_fn(rng, palette, font, sym)
    svg_body += _svg_footer()

    # Apply treatment
    if treatment == "distress-light":
        svg_body = _apply_distress(svg_body, 0.35)
    elif treatment == "distress-heavy":
        svg_body = _apply_distress(svg_body, 0.65)
    elif treatment == "halftone":
        svg_body = _apply_halftone_accent(svg_body, palette["accent"], 0.5)
    elif treatment == "frame":
        svg_body = _apply_outline_stroke(svg_body, palette["fg"])

    return GraphicDesign(
        id=design_id,
        section=section,
        layout=layout_fn.__name__.replace("_layout_", ""),
        palette_name=palette["name"],
        font_name=font["name"],
        symbol_name=sym["name"],
        treatment=treatment,
        title=title_word,
        svg=svg_body,
        bg_color=palette["bg"],
        fg_color=palette["fg"],
    )


def generate_collection_svgs(
    n: int = 1000,
    seed: str = "FTC-GRAPHIC-COLLECTION-V1",
    sections: list[str] | None = None,
) -> list[GraphicDesign]:
    """Generate the full collection of N graphic designs."""
    if sections is None:
        sections = ["tee", "hat", "hoodie", "all-over"]

    designs: list[GraphicDesign] = []
    per_section = n // len(sections)
    remainder = n % len(sections)

    for s_idx, section in enumerate(sections):
        count = per_section + (1 if s_idx < remainder else 0)
        for i in range(count):
            design_id = f"FTC-GFX-{section[:3].upper()}-{i+1:04d}"
            designs.append(generate_graphic_design(design_id, section, seed))

    return designs
