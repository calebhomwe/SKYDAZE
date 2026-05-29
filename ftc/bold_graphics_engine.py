"""Bold graphic-tee generator — hip-hop graphic vocabulary, Christian content.

Procedurally generates SVG graphic tees across 5 intensity tiers
(Whisper → Speak → Statement → Sermon → Shout) using 15 styles drawn from
the hip-hop graphic design canon (Cey Adams, Eric Haze, Sk8thing, CPFM,
Verdy, Brain Dead, Heron Preston, Awake NY). Christian content via fragment.

Playbook: research/CHRISTIAN_HIP_HOP_DESIGN_PLAYBOOK.md
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .colors import Palette, best_text_color, palette_for

# 4:5 garment-shot aspect ratio
VIEWBOX = "0 0 1200 1500"
W, H = 1200, 1500

Style = Literal[
    "stacked-text",
    "big-word-block",
    "hand-drawn-marker",
    "wheatpaste",
    "album-cover-emblem",
    "layered-reference",
    "spray-tag",
    "photo-halftone",
    "type-burst",
    "manuscript-marginalia",
    "tour-merch-bootleg",
    "three-line-stack",
    "halftone-portrait",
    "naive-drawing",
    "all-over-pattern",
]

ALL_STYLES: tuple[Style, ...] = (
    "stacked-text", "big-word-block", "hand-drawn-marker", "wheatpaste",
    "album-cover-emblem", "layered-reference", "spray-tag", "photo-halftone",
    "type-burst", "manuscript-marginalia", "tour-merch-bootleg",
    "three-line-stack", "halftone-portrait", "naive-drawing", "all-over-pattern",
)

# Intensity tier per style — Tier 3 (Statement), Tier 4 (Sermon), Tier 5 (Shout)
STYLE_TIER: dict[Style, int] = {
    "stacked-text": 3,
    "big-word-block": 3,
    "hand-drawn-marker": 4,
    "wheatpaste": 4,
    "album-cover-emblem": 3,
    "layered-reference": 4,
    "spray-tag": 4,
    "photo-halftone": 4,
    "type-burst": 3,
    "manuscript-marginalia": 5,
    "tour-merch-bootleg": 4,
    "three-line-stack": 3,
    "halftone-portrait": 5,
    "naive-drawing": 4,
    "all-over-pattern": 5,
}

# Content wells — fragments only. Never full verse citations. Never preachy.
HYMN_FRAGMENTS = [
    "COME / THOU / FOUNT", "BE / THOU / MY / VISION",
    "STREAMS / OF / MERCY", "HOLY / HOLY / HOLY",
    "WONDROUS / CROSS", "TUNE / MY / HEART",
    "TEACH / ME / SOME / MELODIOUS / SONNET",
    "HERE / I / RAISE", "BROAD / SHOULDERS / HOLDING",
]

AUGUSTINE_FRAGMENTS = [
    "LATE / HAVE / I / LOVED / THEE", "OUR / HEART / RESTLESS",
    "TOLLE LEGE", "RESTLESS UNTIL", "THOU / WERT / WITHIN",
    "I / WAS / OUTSIDE", "TOO / LATE / I / LOVED / THEE",
    "MAKE / ME / CHASTE",
]

GREEK_WORDS = ["ΑΓΑΠΗ", "ΛΟΓΟΣ", "ΧΑΡΙΣ", "ΕΚΚΛΗΣΙΑ", "ΕΙΡΗΝΗ", "ΑΛΗΘΕΙΑ", "ΦΩΣ"]
GREEK_TRANSLITERATED = ["AGAPE", "LOGOS", "CHARIS", "EKKLESIA", "EIRENE", "ALETHEIA", "PHOS"]

HEBREW_WORDS = ["שׁלום", "חסד", "אמונה", "צדק", "רחמים"]
HEBREW_TRANSLITERATED = ["SHALOM", "CHESED", "EMUNAH", "TZEDEK", "RACHAMIM"]

LATIN_PHRASES = [
    "SOLI DEO GLORIA", "LUX MUNDI", "CARITAS",
    "AD MAIOREM DEI GLORIAM", "PAX VOBISCUM", "CREDO",
    "MEMENTO MORI", "TOLLE LEGE",
]

DIASPORA_PLACES = [
    "DMV", "BROOKLYN", "SCARBOROUGH", "PERTH", "MARYLAND",
    "PECKHAM", "LAGOS", "HOWARD",
]

HISTORICAL_FIGURES = [
    "AUGUSTINE", "BONHOEFFER", "TUBMAN", "DAY",
    "THURMAN", "WESLEY", "JULIAN OF NORWICH", "BROTHER LAWRENCE",
]

TRINITY_STACKS = [
    "FATHER / SON / SPIRIT",
    "ONE / IN / THREE",
    "PROMISE / PROCESS / PRESENCE",
    "WORD / WATER / WIND",
    "MERCY / GRACE / PEACE",
    "FAITH / HOPE / LOVE",
]


@dataclass
class BoldSpec:
    style: Style
    palette: Palette
    seed: int
    content: str
    secondary: str = ""
    background: Literal["bone", "onyx"] = "bone"


def _rng(seed: int) -> random.Random:
    return random.Random(seed)


def _bg_color(spec: BoldSpec) -> str:
    if spec.background == "bone":
        return spec.palette.hexes[-1] if len(spec.palette.hexes) > 3 else "#EFE9D8"
    return spec.palette.hexes[0]


def _ink_color(spec: BoldSpec) -> str:
    """The 'ink' color — high contrast with the background."""
    if spec.background == "bone":
        return spec.palette.hexes[0]
    return spec.palette.hexes[-1] if len(spec.palette.hexes) > 3 else "#EFE9D8"


def _accent_color(spec: BoldSpec) -> str:
    if len(spec.palette.hexes) > 2:
        return spec.palette.hexes[2]
    return spec.palette.hexes[-1]


def _grain(spec: BoldSpec, opacity: float = 0.03) -> str:
    return f"""
    <filter id="grain-{spec.seed}" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.95" numOctaves="2" seed="{spec.seed}"/>
      <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {opacity} 0"/>
    </filter>
    <rect x="0" y="0" width="{W}" height="{H}" filter="url(#grain-{spec.seed})"/>
    """


# ---------------------------------------------------------------------------
# Style renderers
# ---------------------------------------------------------------------------


def _stacked_text(spec: BoldSpec) -> str:
    """Eric Haze 3-line stack. Tight tracking, heavy weight."""
    ink = _ink_color(spec)
    lines = spec.content.split(" / ")
    parts = []
    cy = 600
    line_h = 130
    parts.append(f'<g font-family="Helvetica Neue, Arial Black, sans-serif" font-weight="900" fill="{ink}" text-anchor="middle">')
    for i, line in enumerate(lines):
        size = 140 if len(line) <= 6 else (110 if len(line) <= 9 else 80)
        y = cy + i * line_h
        parts.append(f'<text x="{W//2}" y="{y}" font-size="{size}" letter-spacing="-4">{line}</text>')
    parts.append("</g>")
    return "\n".join(parts)


def _big_word_block(spec: BoldSpec) -> str:
    """Cey Adams. One word. Maximum weight."""
    ink = _ink_color(spec)
    accent = _accent_color(spec)
    word = spec.content.split(" / ")[0] if " / " in spec.content else spec.content
    size = 280 if len(word) <= 4 else (200 if len(word) <= 6 else 150)
    return f"""
    <rect x="120" y="600" width="{W-240}" height="280" fill="{accent}" opacity="0.18"/>
    <text x="{W//2}" y="800" font-family="Helvetica Neue, Arial Black, sans-serif"
          font-weight="900" font-size="{size}" letter-spacing="-8"
          fill="{ink}" text-anchor="middle">{word}</text>
    """


def _hand_drawn_marker(spec: BoldSpec) -> str:
    """CPFM. Wonky baseline, mixed case, marker-feel."""
    ink = _ink_color(spec)
    rng = _rng(spec.seed)
    words = spec.content.replace(" / ", " ").split(" ")
    parts = ['<g font-family="Comic Sans MS, Marker Felt, Bradley Hand, cursive" fill="{ink}" font-weight="700">'.format(ink=ink)]
    cy = 700
    for i, word in enumerate(words):
        size = rng.randint(80, 140)
        rotation = rng.randint(-5, 5)
        x_offset = rng.randint(-30, 30)
        y_offset = (i - len(words) / 2) * 130
        x = W // 2 + x_offset
        y = cy + y_offset
        parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle" '
            f'transform="rotate({rotation} {x} {y})">{word}</text>'
        )
    parts.append("</g>")
    # Add some scribble marks for marker feel
    for _ in range(rng.randint(3, 6)):
        x1 = rng.randint(150, W - 150)
        y1 = rng.randint(500, H - 300)
        x2 = x1 + rng.randint(-40, 40)
        y2 = y1 + rng.randint(-15, 15)
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ink}" stroke-width="3" opacity="0.7" stroke-linecap="round"/>')
    return "\n".join(parts)


def _wheatpaste(spec: BoldSpec) -> str:
    """Heron Preston wheatpaste energy. Vertical type panel, sticker feel."""
    ink = _ink_color(spec)
    accent = _accent_color(spec)
    rng = _rng(spec.seed)
    word = spec.content.split(" / ")[0] if " / " in spec.content else spec.content
    # The paste rectangle
    angle = rng.randint(-6, 6)
    parts = [
        f'<g transform="rotate({angle} {W//2} 800)">',
        f'<rect x="240" y="450" width="{W-480}" height="700" fill="{accent}" opacity="0.92"/>',
        f'<rect x="240" y="450" width="{W-480}" height="700" fill="none" stroke="{ink}" stroke-width="3" opacity="0.55"/>',
        f'<text x="{W//2}" y="850" font-family="Impact, Haettenschweiler, Arial Black, sans-serif" font-weight="900" font-size="180" letter-spacing="2" fill="{ink}" text-anchor="middle">{word}</text>',
        f'<text x="{W//2}" y="970" font-family="Helvetica Neue, sans-serif" font-weight="700" font-size="36" letter-spacing="6" fill="{ink}" text-anchor="middle" opacity="0.7">{spec.secondary or "FTC · FULL TIME"}</text>',
        "</g>",
    ]
    # Torn-edge marks
    for _ in range(8):
        x = rng.randint(200, W - 200)
        y_top = rng.randint(440, 470)
        y_btm = rng.randint(1140, 1170)
        parts.append(f'<line x1="{x}" y1="{y_top}" x2="{x+5}" y2="{y_top+15}" stroke="{ink}" stroke-width="1" opacity="0.3"/>')
        parts.append(f'<line x1="{x}" y1="{y_btm}" x2="{x+5}" y2="{y_btm-15}" stroke="{ink}" stroke-width="1" opacity="0.3"/>')
    return "\n".join(parts)


def _album_cover_emblem(spec: BoldSpec) -> str:
    """Sk8thing / BAPE album cover energy. Circular emblem with wrapping type."""
    ink = _ink_color(spec)
    accent = _accent_color(spec)
    word = spec.content.split(" / ")[0] if " / " in spec.content else spec.content
    return f"""
    <circle cx="{W//2}" cy="780" r="320" fill="none" stroke="{ink}" stroke-width="6"/>
    <circle cx="{W//2}" cy="780" r="280" fill="{accent}" opacity="0.18"/>
    <circle cx="{W//2}" cy="780" r="240" fill="none" stroke="{ink}" stroke-width="2"/>
    <text x="{W//2}" y="820" font-family="Trajan Pro, Cinzel, Georgia, serif"
          font-size="120" font-weight="700" letter-spacing="2"
          fill="{ink}" text-anchor="middle">{word}</text>
    <defs>
      <path id="emblem-arc-{spec.seed}" d="M {W//2 - 290},780 A 290,290 0 0,1 {W//2 + 290},780"/>
    </defs>
    <text font-family="Helvetica Neue, sans-serif" font-size="32" letter-spacing="14" fill="{ink}">
      <textPath href="#emblem-arc-{spec.seed}" startOffset="50%" text-anchor="middle">
        FTC · FULL TIME CHRISTIAN · MMXXVI
      </textPath>
    </text>
    """


def _layered_reference(spec: BoldSpec) -> str:
    """Brain Dead density. Stack: place + fragment + ornament."""
    ink = _ink_color(spec)
    accent = _accent_color(spec)
    rng = _rng(spec.seed)
    place = spec.secondary or "BROOKLYN"
    fragment = spec.content
    parts = []
    # Background halftone
    for _ in range(80):
        x = rng.randint(120, W - 120)
        y = rng.randint(400, H - 200)
        r = rng.uniform(2, 5)
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{accent}" opacity="0.35"/>')
    # Large fragment text
    parts.append(f'<text x="{W//2}" y="640" font-family="Trajan Pro, Cinzel, Georgia, serif" font-size="98" font-weight="700" letter-spacing="2" fill="{ink}" text-anchor="middle">{fragment.split(" / ")[0]}</text>')
    if " / " in fragment and len(fragment.split(" / ")) > 1:
        parts.append(f'<text x="{W//2}" y="740" font-family="Trajan Pro, Cinzel, Georgia, serif" font-size="98" font-weight="700" letter-spacing="2" fill="{ink}" text-anchor="middle">{fragment.split(" / ")[1]}</text>')
    # Place anchor at bottom
    parts.append(f'<line x1="200" y1="1180" x2="{W-200}" y2="1180" stroke="{ink}" stroke-width="2"/>')
    parts.append(f'<text x="{W//2}" y="1240" font-family="Helvetica Neue, sans-serif" font-weight="900" font-size="64" letter-spacing="14" fill="{ink}" text-anchor="middle">{place}</text>')
    parts.append(f'<text x="{W//2}" y="1290" font-family="Helvetica Neue, sans-serif" font-size="22" letter-spacing="4" fill="{ink}" text-anchor="middle" opacity="0.7">FULL TIME CHRISTIAN</text>')
    return "\n".join(parts)


def _spray_tag(spec: BoldSpec) -> str:
    """Eric Haze graffiti energy without literal graffiti."""
    ink = _ink_color(spec)
    rng = _rng(spec.seed)
    word = spec.content.split(" / ")[0] if " / " in spec.content else spec.content
    angle = rng.randint(-4, 4)
    # Drips
    parts = [f'<g transform="rotate({angle} {W//2} 780)">']
    parts.append(f'<text x="{W//2}" y="800" font-family="Impact, Haettenschweiler, sans-serif" font-weight="900" font-size="240" letter-spacing="-6" fill="{ink}" text-anchor="middle">{word}</text>')
    parts.append("</g>")
    # Drip marks under the type
    for _ in range(rng.randint(4, 8)):
        x = rng.randint(280, W - 280)
        y_start = 820
        y_end = y_start + rng.randint(20, 90)
        parts.append(f'<rect x="{x}" y="{y_start}" width="3" height="{y_end - y_start}" fill="{ink}" opacity="0.85"/>')
        parts.append(f'<circle cx="{x + 1}" cy="{y_end}" r="3" fill="{ink}" opacity="0.85"/>')
    return "\n".join(parts)


def _photo_halftone(spec: BoldSpec) -> str:
    """Brain Dead halftone-print energy."""
    ink = _ink_color(spec)
    accent = _accent_color(spec)
    rng = _rng(spec.seed)
    parts = []
    # Halftone dot field — varying density to suggest a photograph
    for x in range(180, W - 180, 22):
        for y in range(360, H - 320, 22):
            cy_mid = 800
            dist = abs(y - cy_mid)
            density_factor = max(0.2, 1 - dist / 500)
            r = rng.uniform(1, 7) * density_factor
            parts.append(f'<circle cx="{x + rng.randint(-3,3)}" cy="{y + rng.randint(-3,3)}" r="{r:.2f}" fill="{accent}" opacity="0.55"/>')
    # Title bar
    parts.append(f'<rect x="120" y="640" width="{W-240}" height="80" fill="{ink}"/>')
    parts.append(f'<text x="{W//2}" y="700" font-family="Trajan Pro, Cinzel, Georgia, serif" font-size="50" font-weight="700" letter-spacing="6" fill="{_bg_color(spec)}" text-anchor="middle">{spec.content.split(" / ")[0]}</text>')
    parts.append(f'<rect x="120" y="900" width="{W-240}" height="50" fill="{ink}" opacity="0.85"/>')
    parts.append(f'<text x="{W//2}" y="938" font-family="Helvetica Neue, sans-serif" font-size="28" letter-spacing="8" fill="{_bg_color(spec)}" text-anchor="middle">{spec.secondary or "MMXXVI"}</text>')
    return "\n".join(parts)


def _type_burst(spec: BoldSpec) -> str:
    """Heron Preston radial type. Word repeated around a center."""
    ink = _ink_color(spec)
    word = spec.content.split(" / ")[0] if " / " in spec.content else spec.content
    parts = []
    n = 12
    for i in range(n):
        angle = (360 / n) * i
        parts.append(
            f'<text x="{W//2}" y="780" font-family="Helvetica Neue, sans-serif" '
            f'font-weight="900" font-size="46" letter-spacing="6" '
            f'fill="{ink}" text-anchor="middle" opacity="0.85" '
            f'transform="rotate({angle} {W//2} 780) translate(0 -300)">{word}</text>'
        )
    parts.append(f'<circle cx="{W//2}" cy="780" r="60" fill="{ink}"/>')
    parts.append(f'<text x="{W//2}" y="800" font-family="Trajan Pro, serif" font-size="40" font-weight="700" fill="{_bg_color(spec)}" text-anchor="middle">FTC</text>')
    return "\n".join(parts)


def _manuscript_marginalia(spec: BoldSpec) -> str:
    """Illuminated-manuscript reference. Centered Trajan body + decorative border."""
    ink = _ink_color(spec)
    accent = _accent_color(spec)
    parts = []
    # Border
    parts.append(f'<rect x="180" y="350" width="{W-360}" height="900" fill="none" stroke="{ink}" stroke-width="3"/>')
    parts.append(f'<rect x="200" y="370" width="{W-400}" height="860" fill="none" stroke="{ink}" stroke-width="1" opacity="0.5"/>')
    # Decorative corner flourishes
    for cx, cy in [(180, 350), (W-180, 350), (180, 1250), (W-180, 1250)]:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="14" fill="none" stroke="{ink}" stroke-width="2"/>')
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{accent}"/>')
    # Illuminated capital
    fragment = spec.content
    first = fragment[0] if fragment else "I"
    rest = fragment[1:] if len(fragment) > 1 else ""
    parts.append(f'<rect x="280" y="500" width="180" height="180" fill="{accent}" opacity="0.6"/>')
    parts.append(f'<text x="370" y="640" font-family="Cinzel, Trajan Pro, serif" font-weight="900" font-size="180" fill="{ink}" text-anchor="middle">{first}</text>')
    # Body
    parts.append(f'<text x="{W//2}" y="780" font-family="Cinzel, Trajan Pro, serif" font-size="58" font-weight="700" letter-spacing="4" fill="{ink}" text-anchor="middle">{rest.strip().split(" / ")[0]}</text>')
    if " / " in rest:
        for i, line in enumerate(rest.split(" / ")[1:4]):
            parts.append(f'<text x="{W//2}" y="{870 + i*80}" font-family="Cinzel, Trajan Pro, serif" font-size="58" font-weight="700" letter-spacing="4" fill="{ink}" text-anchor="middle">{line}</text>')
    # Caption
    parts.append(f'<text x="{W//2}" y="1180" font-family="Helvetica Neue, sans-serif" font-size="22" letter-spacing="8" fill="{ink}" text-anchor="middle" opacity="0.75">FTC · {spec.secondary or "MMXXVI"}</text>')
    return "\n".join(parts)


def _tour_merch_bootleg(spec: BoldSpec) -> str:
    """Awake NY tour-poster energy — concert merch layout."""
    ink = _ink_color(spec)
    accent = _accent_color(spec)
    parts = []
    parts.append(f'<text x="{W//2}" y="540" font-family="Trajan Pro, Cinzel, Georgia, serif" font-weight="900" font-size="68" letter-spacing="14" fill="{ink}" text-anchor="middle">FULL TIME CHRISTIAN</text>')
    parts.append(f'<line x1="220" y1="580" x2="{W-220}" y2="580" stroke="{ink}" stroke-width="2"/>')
    parts.append(f'<text x="{W//2}" y="720" font-family="Impact, Haettenschweiler, sans-serif" font-weight="900" font-size="180" letter-spacing="-2" fill="{ink}" text-anchor="middle">{spec.content.split(" / ")[0]}</text>')
    if " / " in spec.content:
        parts.append(f'<text x="{W//2}" y="880" font-family="Impact, Haettenschweiler, sans-serif" font-weight="900" font-size="180" letter-spacing="-2" fill="{accent}" text-anchor="middle">{spec.content.split(" / ")[1]}</text>')
    parts.append(f'<line x1="220" y1="950" x2="{W-220}" y2="950" stroke="{ink}" stroke-width="2"/>')
    # Tour dates
    cities = ["DMV", "BROOKLYN", "PECKHAM", "LAGOS", "PERTH", "SCARBOROUGH"]
    for i, city in enumerate(cities):
        y = 1010 + i * 36
        parts.append(f'<text x="{W//2}" y="{y}" font-family="Helvetica Neue, sans-serif" font-weight="700" font-size="26" letter-spacing="8" fill="{ink}" text-anchor="middle" opacity="0.85">MMXXVI · {city}</text>')
    return "\n".join(parts)


def _three_line_stack(spec: BoldSpec) -> str:
    """Cey Adams trinitarian stack. 3 lines, equal weight."""
    ink = _ink_color(spec)
    lines = spec.content.split(" / ")[:3]
    if len(lines) < 3:
        lines = lines + ["·"] * (3 - len(lines))
    parts = ['<g font-family="Helvetica Neue, Arial Black, sans-serif" font-weight="900" fill="{ink}" text-anchor="middle">'.format(ink=ink)]
    cy = 620
    sizes = [110, 110, 110]
    for i, line in enumerate(lines):
        size = sizes[i]
        if len(line) > 8:
            size = 80
        y = cy + i * 150
        parts.append(f'<text x="{W//2}" y="{y}" font-size="{size}" letter-spacing="2">{line}</text>')
    parts.append("</g>")
    # Anchor mark
    parts.append(f'<rect x="{W//2 - 100}" y="{cy + 3*150 + 30}" width="200" height="3" fill="{ink}"/>')
    parts.append(f'<text x="{W//2}" y="{cy + 3*150 + 90}" font-family="Helvetica Neue, sans-serif" font-size="22" letter-spacing="10" fill="{ink}" text-anchor="middle" opacity="0.7">FTC · MMXXVI</text>')
    return "\n".join(parts)


def _halftone_portrait(spec: BoldSpec) -> str:
    """Pyer Moss historical-essay tee. Halftone 'portrait' field + name."""
    ink = _ink_color(spec)
    accent = _accent_color(spec)
    rng = _rng(spec.seed)
    parts = []
    # Halftone field that suggests a portrait
    cx, cy = W // 2, 700
    for ring_idx in range(40):
        r = 60 + ring_idx * 12
        n_dots = max(8, ring_idx * 6)
        for j in range(n_dots):
            theta = (2 * math.pi / n_dots) * j + rng.uniform(-0.05, 0.05)
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta) * 0.85  # squash slightly
            if y < 350 or y > 1050:
                continue
            dot_r = rng.uniform(2, 6) * (1 - ring_idx / 50)
            if dot_r > 1:
                parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{dot_r:.2f}" fill="{accent}" opacity="0.75"/>')
    # Name at bottom
    parts.append(f'<rect x="220" y="1140" width="{W-440}" height="4" fill="{ink}"/>')
    parts.append(f'<text x="{W//2}" y="1230" font-family="Trajan Pro, Cinzel, Georgia, serif" font-weight="900" font-size="86" letter-spacing="14" fill="{ink}" text-anchor="middle">{spec.content.split(" / ")[0]}</text>')
    parts.append(f'<text x="{W//2}" y="1290" font-family="Helvetica Neue, sans-serif" font-size="22" letter-spacing="8" fill="{ink}" text-anchor="middle" opacity="0.7">FTC · {spec.secondary or "FULL TIME CHRISTIAN"}</text>')
    return "\n".join(parts)


def _naive_drawing(spec: BoldSpec) -> str:
    """CPFM-grade single naive drawing. The simplicity does the work."""
    ink = _ink_color(spec)
    accent = _accent_color(spec)
    rng = _rng(spec.seed)
    cx, cy = W // 2, 700
    parts = []
    # Determine which biblical motif this is
    fragment_first = spec.content.split(" / ")[0].lower()
    motif = "lamp"
    if "vine" in fragment_first or "harvest" in fragment_first:
        motif = "vine"
    elif "water" in fragment_first or "river" in fragment_first or "still" in fragment_first:
        motif = "water"
    elif "stone" in fragment_first or "rock" in fragment_first:
        motif = "stone"
    elif "olive" in fragment_first or "sprig" in fragment_first:
        motif = "olive"
    elif "lamp" in fragment_first or "light" in fragment_first or "phos" in fragment_first:
        motif = "lamp"

    if motif == "vine":
        path = "M 400 900 Q 500 700 600 800 Q 700 900 800 700 Q 900 500 800 400"
        parts.append(f'<path d="{path}" fill="none" stroke="{ink}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>')
        for pos in [(500, 750), (650, 800), (750, 650), (820, 480)]:
            parts.append(f'<ellipse cx="{pos[0]}" cy="{pos[1]}" rx="32" ry="18" fill="{accent}" stroke="{ink}" stroke-width="6" transform="rotate({rng.randint(-20,20)} {pos[0]} {pos[1]})"/>')
    elif motif == "water":
        for i, y in enumerate([550, 650, 750, 850, 950]):
            parts.append(f'<path d="M 300 {y} Q 500 {y - 20} 700 {y} Q 900 {y + 20} 1100 {y}" fill="none" stroke="{ink}" stroke-width="{12 - i*1.5}" stroke-linecap="round" opacity="{1 - i*0.12}"/>')
    elif motif == "stone":
        parts.append(f'<polygon points="{cx-180},{cy+150} {cx-90},{cy-100} {cx+100},{cy-120} {cx+200},{cy+50} {cx+130},{cy+200} {cx-110},{cy+180}" fill="{accent}" stroke="{ink}" stroke-width="10" stroke-linejoin="round"/>')
        parts.append(f'<line x1="{cx-80}" y1="{cy}" x2="{cx+60}" y2="{cy-30}" stroke="{ink}" stroke-width="4" opacity="0.6"/>')
        parts.append(f'<line x1="{cx-60}" y1="{cy+60}" x2="{cx+80}" y2="{cy+40}" stroke="{ink}" stroke-width="4" opacity="0.6"/>')
    elif motif == "olive":
        # Branch with leaves
        parts.append(f'<line x1="{cx-200}" y1="{cy+100}" x2="{cx+200}" y2="{cy-100}" stroke="{ink}" stroke-width="10" stroke-linecap="round"/>')
        for i in range(8):
            t = i / 7.0
            lx = cx - 200 + t * 400
            ly = cy + 100 + t * (-200)
            angle = -45 + i * 12
            parts.append(f'<ellipse cx="{lx}" cy="{ly}" rx="40" ry="14" fill="{accent}" stroke="{ink}" stroke-width="4" transform="rotate({angle} {lx} {ly})"/>')
    else:  # lamp
        parts.append(f'<rect x="{cx-100}" y="{cy-50}" width="200" height="180" rx="20" fill="{accent}" stroke="{ink}" stroke-width="10"/>')
        parts.append(f'<rect x="{cx-130}" y="{cy-110}" width="260" height="40" rx="8" fill="{ink}"/>')
        parts.append(f'<path d="M {cx} {cy-180} L {cx} {cy-120}" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
        # Flame
        parts.append(f'<path d="M {cx} {cy-260} Q {cx-40} {cy-200} {cx} {cy-180} Q {cx+40} {cy-200} {cx} {cy-260}" fill="{accent}" stroke="{ink}" stroke-width="6"/>')

    # Label
    parts.append(f'<text x="{W//2}" y="1180" font-family="Comic Sans MS, Marker Felt, cursive" font-size="48" font-weight="700" fill="{ink}" text-anchor="middle">{spec.content}</text>')
    parts.append(f'<text x="{W//2}" y="1240" font-family="Helvetica Neue, sans-serif" font-size="20" letter-spacing="8" fill="{ink}" text-anchor="middle" opacity="0.6">FTC · MMXXVI</text>')
    return "\n".join(parts)


def _all_over_pattern(spec: BoldSpec) -> str:
    """Heron Preston all-over repeated text."""
    ink = _ink_color(spec)
    word = spec.content.split(" / ")[0] if " / " in spec.content else spec.content
    parts = []
    rng = _rng(spec.seed)
    rows = 9
    cols = 5
    for r in range(rows):
        offset_x = 60 if r % 2 == 0 else 0
        for c in range(cols):
            x = 80 + c * 240 + offset_x
            y = 240 + r * 140
            rotation = rng.randint(-3, 3)
            opacity = 0.35 + rng.uniform(0, 0.45)
            parts.append(
                f'<text x="{x}" y="{y}" font-family="Helvetica Neue, sans-serif" '
                f'font-weight="900" font-size="56" letter-spacing="4" '
                f'fill="{ink}" opacity="{opacity:.2f}" '
                f'transform="rotate({rotation} {x} {y})">{word}</text>'
            )
    # Hero block on top
    parts.append(f'<rect x="{W//2 - 280}" y="700" width="560" height="200" fill="{_bg_color(spec)}"/>')
    parts.append(f'<rect x="{W//2 - 280}" y="700" width="560" height="200" fill="none" stroke="{ink}" stroke-width="3"/>')
    parts.append(f'<text x="{W//2}" y="830" font-family="Trajan Pro, Cinzel, Georgia, serif" font-weight="900" font-size="80" letter-spacing="8" fill="{ink}" text-anchor="middle">FTC</text>')
    return "\n".join(parts)


STYLE_RENDERERS = {
    "stacked-text": _stacked_text,
    "big-word-block": _big_word_block,
    "hand-drawn-marker": _hand_drawn_marker,
    "wheatpaste": _wheatpaste,
    "album-cover-emblem": _album_cover_emblem,
    "layered-reference": _layered_reference,
    "spray-tag": _spray_tag,
    "photo-halftone": _photo_halftone,
    "type-burst": _type_burst,
    "manuscript-marginalia": _manuscript_marginalia,
    "tour-merch-bootleg": _tour_merch_bootleg,
    "three-line-stack": _three_line_stack,
    "halftone-portrait": _halftone_portrait,
    "naive-drawing": _naive_drawing,
    "all-over-pattern": _all_over_pattern,
}


# ---------------------------------------------------------------------------
# Content selection
# ---------------------------------------------------------------------------


def _content_for(style: Style, rng: random.Random) -> tuple[str, str]:
    """Return (primary, secondary) content fragments appropriate to style."""
    if style == "stacked-text":
        return rng.choice(HYMN_FRAGMENTS), ""
    if style == "big-word-block":
        return rng.choice(GREEK_TRANSLITERATED + HEBREW_TRANSLITERATED), ""
    if style == "hand-drawn-marker":
        return rng.choice(AUGUSTINE_FRAGMENTS), ""
    if style == "wheatpaste":
        return rng.choice(HISTORICAL_FIGURES), rng.choice(["1700", "1850", "1940", "MMXXVI"])
    if style == "album-cover-emblem":
        return rng.choice(DIASPORA_PLACES), ""
    if style == "layered-reference":
        return rng.choice(AUGUSTINE_FRAGMENTS + HYMN_FRAGMENTS), rng.choice(DIASPORA_PLACES)
    if style == "spray-tag":
        return rng.choice(HEBREW_TRANSLITERATED + GREEK_TRANSLITERATED), ""
    if style == "photo-halftone":
        return rng.choice(LATIN_PHRASES), rng.choice(["MMXXVI", "VOL I", "VOL II"])
    if style == "type-burst":
        return rng.choice(LATIN_PHRASES), ""
    if style == "manuscript-marginalia":
        return rng.choice(AUGUSTINE_FRAGMENTS), "MMXXVI"
    if style == "tour-merch-bootleg":
        return rng.choice(HYMN_FRAGMENTS), ""
    if style == "three-line-stack":
        return rng.choice(TRINITY_STACKS), ""
    if style == "halftone-portrait":
        return rng.choice(HISTORICAL_FIGURES), rng.choice(["AUGUSTINIAN", "METHODIST", "MYSTIC", "RESISTANCE"])
    if style == "naive-drawing":
        return rng.choice(["LAMP", "VINE", "STONE", "OLIVE", "STILL WATERS"]), ""
    if style == "all-over-pattern":
        return rng.choice(GREEK_TRANSLITERATED + HEBREW_TRANSLITERATED), ""
    return "FTC", ""


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


def render_bold(spec: BoldSpec) -> str:
    body = STYLE_RENDERERS[spec.style](spec)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}" width="{W}" height="{H}">
  <defs>{_grain(spec)}</defs>
  <rect x="0" y="0" width="{W}" height="{H}" fill="{_bg_color(spec)}"/>
  {body}
</svg>
"""


def _seed_for(style: Style, idx: int) -> int:
    h = hashlib.sha256(f"bold:{style}:{idx}".encode()).hexdigest()
    return int(h[:8], 16)


def generate_bold_collection(out_dir: Path, count: int = 30) -> list[Path]:
    """Generate `count` bold graphic tee SVGs across all styles + tiers."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    sections = ("tee", "tracksuit", "outerwear", "accessory")

    for i in range(count):
        style = ALL_STYLES[i % len(ALL_STYLES)]
        section = sections[i % len(sections)]
        palette = palette_for(section, i, seed=f"FTC-BOLD-{i:03d}")
        # Alternate bone / onyx backgrounds per section per playbook
        background: Literal["bone", "onyx"] = "bone" if (i // len(ALL_STYLES)) % 2 == 0 else "onyx"
        seed = _seed_for(style, i)
        rng = _rng(seed)
        primary, secondary = _content_for(style, rng)
        spec = BoldSpec(
            style=style,
            palette=palette,
            seed=seed,
            content=primary,
            secondary=secondary,
            background=background,
        )
        svg = render_bold(spec)
        tier = STYLE_TIER[style]
        slug = primary.lower().replace(" / ", "-").replace(" ", "-").replace(".", "")[:30]
        filename = f"ftc-bold-{i:03d}-t{tier}-{style}-{slug}.svg"
        path = out_dir / filename
        path.write_text(svg)
        paths.append(path)
    return paths


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "artifacts" / "graphics-bold"
    paths = generate_bold_collection(out, count=30)
    print(f"Generated {len(paths)} bold graphic tees into {out}")
    for p in paths[:6]:
        print(" -", p.name)
