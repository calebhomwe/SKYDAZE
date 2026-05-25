"""FTC Color Theory Engine.

Mission: produce restrained, luxury-grade palettes inspired by Itten + Munsell,
with explicit brand bias toward earth/monochrome/ash (Section 1, 2 of master
context). LV uses two-square logo palettes; FTC plays in 2-3 squares, never
more than 5 hex.

All palettes are deterministic from a seed so a design can always be
reproduced exactly.
"""

from __future__ import annotations

import colorsys
import hashlib
import random
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Curated brand-locked base hues (HSV; H is degrees / 360).
# These are the only hues that ship by default. Anything outside this set is
# considered off-brand and requires a manual flag.
# ---------------------------------------------------------------------------

BRAND_HUES: dict[str, float] = {
    # name           : hue in [0,1)
    "ink":            0.62,   # deep cool near-black blue
    "stone":          0.08,   # warm grey
    "ash":            0.05,   # cool grey
    "bone":           0.10,   # off-white warm
    "oat":            0.09,   # cream
    "rust":           0.04,   # oxidized red-brown
    "ember":          0.03,   # banked-fire orange-brown
    "moss":           0.27,   # deep low-chroma green
    "slate":          0.60,   # cool blue-grey
    "sand":           0.10,   # warm light
    "walnut":         0.07,   # mid brown
    "obsidian":       0.66,   # near-black violet
}

NEUTRALS: list[str] = ["ink", "stone", "ash", "bone", "oat", "slate", "obsidian"]
EARTHS: list[str] = ["rust", "ember", "moss", "sand", "walnut", "stone", "oat"]


def _hex(r: float, g: float, b: float) -> str:
    return f"#{max(0, min(255, round(r * 255))):02X}{max(0, min(255, round(g * 255))):02X}{max(0, min(255, round(b * 255))):02X}"


def _value_curve(value_step: float) -> float:
    """Munsell-inspired value clamp; brand caps lightness."""
    return max(0.08, min(0.94, value_step))


def _saturation_cap(chroma: float) -> float:
    """Brand cap: never above 0.55 saturation (Section 1: no neon)."""
    return max(0.02, min(0.55, chroma))


def _hsv_to_hex(h: float, s: float, v: float) -> str:
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, _saturation_cap(s), _value_curve(v))
    return _hex(r, g, b)


@dataclass(frozen=True)
class Palette:
    name: str
    family: str
    hexes: tuple[str, ...]
    weights: tuple[float, ...]   # 60-30-10 style; sums to ~1.0
    contrast_score: float        # 0..1 spread between lightest and darkest
    rationale: str

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "family": self.family,
            "hex": list(self.hexes),
            "weights": list(self.weights),
            "contrast_score": round(self.contrast_score, 3),
            "rationale": self.rationale,
        }


# ---------------------------------------------------------------------------
# Palette families — each returns a (hexes, weights, rationale, contrast).
# All functions take an rng + 1-3 base hue names and produce a brand-safe
# palette.
# ---------------------------------------------------------------------------

def _values_from_hue(hue: float, rng: random.Random) -> tuple[float, float, float]:
    """Three Munsell-stepped values for a single hue."""
    dark = rng.uniform(0.10, 0.22)
    mid = rng.uniform(0.42, 0.58)
    light = rng.uniform(0.78, 0.92)
    return dark, mid, light


def monochrome(rng: random.Random, hue_name: str) -> Palette:
    hue = BRAND_HUES[hue_name]
    sat = rng.uniform(0.05, 0.18)
    dark, mid, light = _values_from_hue(hue, rng)
    hexes = (
        _hsv_to_hex(hue, sat * 0.4, dark),
        _hsv_to_hex(hue, sat, mid),
        _hsv_to_hex(hue, sat * 0.6, light),
    )
    return Palette(
        name=f"{hue_name}-monochrome",
        family="monochrome",
        hexes=hexes,
        weights=(0.60, 0.30, 0.10),
        contrast_score=abs(light - dark),
        rationale=f"Single-hue {hue_name}; Munsell-stepped value, chroma capped at {sat:.2f}.",
    )


def analogous(rng: random.Random, hue_names: tuple[str, str, str]) -> Palette:
    hues = [BRAND_HUES[n] for n in hue_names]
    sats = [rng.uniform(0.08, 0.22) for _ in hues]
    values = sorted([rng.uniform(0.20, 0.35), rng.uniform(0.45, 0.60), rng.uniform(0.78, 0.90)])
    hexes = tuple(_hsv_to_hex(h, s, v) for h, s, v in zip(hues, sats, values, strict=False))
    return Palette(
        name=f"{'+'.join(hue_names)}-analogous",
        family="analogous",
        hexes=hexes,
        weights=(0.55, 0.30, 0.15),
        contrast_score=values[-1] - values[0],
        rationale=f"Adjacent low-chroma hues {hue_names}; restrained analogous.",
    )


def earth_neutral(rng: random.Random) -> Palette:
    names = rng.sample(EARTHS, 3)
    hues = [BRAND_HUES[n] for n in names]
    sats = [rng.uniform(0.10, 0.28), rng.uniform(0.06, 0.18), rng.uniform(0.03, 0.10)]
    vals = sorted([rng.uniform(0.18, 0.30), rng.uniform(0.45, 0.60), rng.uniform(0.78, 0.92)])
    hexes = tuple(_hsv_to_hex(h, s, v) for h, s, v in zip(hues, sats, vals, strict=False))
    return Palette(
        name=f"{'+'.join(names)}-earth",
        family="earth-neutral",
        hexes=hexes,
        weights=(0.50, 0.35, 0.15),
        contrast_score=vals[-1] - vals[0],
        rationale=f"Earth-tone triad of {names}; weighted to dominant rich base.",
    )


def split_complementary(rng: random.Random, base_hue_name: str) -> Palette:
    """Rare: small chroma accent over neutral base. Accent at <= 10% weight."""
    base = BRAND_HUES[base_hue_name]
    acc1 = (base + 0.5 - 0.083) % 1.0
    acc2 = (base + 0.5 + 0.083) % 1.0
    hexes = (
        _hsv_to_hex(base, rng.uniform(0.04, 0.10), rng.uniform(0.78, 0.90)),  # light base
        _hsv_to_hex(base, rng.uniform(0.10, 0.20), rng.uniform(0.18, 0.30)),  # dark base
        _hsv_to_hex(rng.choice([acc1, acc2]), rng.uniform(0.18, 0.32), rng.uniform(0.40, 0.55)),  # accent
    )
    return Palette(
        name=f"{base_hue_name}-split-complementary",
        family="split-complementary",
        hexes=hexes,
        weights=(0.60, 0.30, 0.10),
        contrast_score=0.65,
        rationale=f"Neutral base {base_hue_name} with small chroma accent on split-complement.",
    )


def high_contrast_mono(rng: random.Random) -> Palette:
    """Bone + ink — the FTC house palette."""
    bone = _hsv_to_hex(BRAND_HUES["bone"], 0.05, rng.uniform(0.88, 0.94))
    ink = _hsv_to_hex(BRAND_HUES["ink"], 0.12, rng.uniform(0.08, 0.14))
    return Palette(
        name="bone+ink-housepair",
        family="high-contrast-mono",
        hexes=(bone, ink),
        weights=(0.70, 0.30),
        contrast_score=0.80,
        rationale="The two-square house pair. LV-cadence; Lemaire-temperature.",
    )


def two_square_lv_style(rng: random.Random, base_name: str, accent_name: str) -> Palette:
    """LV-style two-square: a body + a foil. FTC: bone/walnut, ash/oat, etc."""
    body = _hsv_to_hex(BRAND_HUES[base_name], rng.uniform(0.08, 0.18), rng.uniform(0.20, 0.35))
    foil = _hsv_to_hex(BRAND_HUES[accent_name], rng.uniform(0.06, 0.16), rng.uniform(0.70, 0.86))
    return Palette(
        name=f"{base_name}+{accent_name}-two-square",
        family="two-square",
        hexes=(body, foil),
        weights=(0.65, 0.35),
        contrast_score=0.55,
        rationale=f"Two-square LV-cadence: {base_name} body + {accent_name} foil.",
    )


def triadic_restrained(rng: random.Random, hue_name: str) -> Palette:
    """Triadic on the wheel, but every hue is desaturated and value-stepped."""
    base = BRAND_HUES[hue_name]
    triad = [base, (base + 1 / 3) % 1.0, (base + 2 / 3) % 1.0]
    sats = [rng.uniform(0.05, 0.12) for _ in triad]
    vals = sorted([rng.uniform(0.18, 0.28), rng.uniform(0.48, 0.60), rng.uniform(0.80, 0.92)])
    hexes = tuple(_hsv_to_hex(h, s, v) for h, s, v in zip(triad, sats, vals, strict=False))
    return Palette(
        name=f"{hue_name}-triadic-restrained",
        family="triadic-restrained",
        hexes=hexes,
        weights=(0.55, 0.30, 0.15),
        contrast_score=vals[-1] - vals[0],
        rationale=f"Triadic from {hue_name}, every hue desaturated to <0.12 sat.",
    )


# ---------------------------------------------------------------------------
# Public entry: deterministic palette for a (section, index) pair.
# ---------------------------------------------------------------------------

def palette_for(section: str, index: int, seed: str = "FTC") -> Palette:
    """Pick a palette family appropriate to the section, deterministically."""
    h = hashlib.sha256(f"{seed}|{section}|{index}".encode()).digest()
    rng = random.Random(int.from_bytes(h[:8], "big"))

    section_bias = {
        "tracksuit": [
            ("high_contrast_mono", 0.18),
            ("monochrome", 0.22),
            ("two_square", 0.22),
            ("earth_neutral", 0.18),
            ("analogous", 0.10),
            ("triadic_restrained", 0.06),
            ("split_complementary", 0.04),
        ],
        "outerwear": [
            ("monochrome", 0.20),
            ("earth_neutral", 0.30),
            ("two_square", 0.18),
            ("analogous", 0.16),
            ("high_contrast_mono", 0.10),
            ("triadic_restrained", 0.06),
        ],
        "tee": [
            ("high_contrast_mono", 0.20),
            ("monochrome", 0.30),
            ("two_square", 0.20),
            ("earth_neutral", 0.18),
            ("analogous", 0.08),
            ("split_complementary", 0.04),
        ],
        "accessory": [
            ("high_contrast_mono", 0.30),
            ("monochrome", 0.30),
            ("two_square", 0.25),
            ("earth_neutral", 0.10),
            ("triadic_restrained", 0.05),
        ],
    }

    families = section_bias.get(section, section_bias["tee"])
    family = rng.choices([f for f, _ in families], weights=[w for _, w in families])[0]

    if family == "monochrome":
        return monochrome(rng, rng.choice(NEUTRALS + EARTHS))
    if family == "analogous":
        # pick three adjacent-feeling hue names
        triplets = [
            ("bone", "oat", "sand"),
            ("ink", "obsidian", "slate"),
            ("stone", "ash", "walnut"),
            ("rust", "ember", "walnut"),
            ("moss", "stone", "oat"),
        ]
        return analogous(rng, rng.choice(triplets))
    if family == "earth_neutral":
        return earth_neutral(rng)
    if family == "split_complementary":
        return split_complementary(rng, rng.choice(NEUTRALS))
    if family == "high_contrast_mono":
        return high_contrast_mono(rng)
    if family == "two_square":
        body = rng.choice(["ink", "obsidian", "walnut", "rust", "stone"])
        foil = rng.choice(["bone", "oat", "sand", "ash"])
        return two_square_lv_style(rng, body, foil)
    if family == "triadic_restrained":
        return triadic_restrained(rng, rng.choice(NEUTRALS))

    return high_contrast_mono(rng)


def relative_luminance(hexcode: str) -> float:
    r = int(hexcode[1:3], 16) / 255
    g = int(hexcode[3:5], 16) / 255
    b = int(hexcode[5:7], 16) / 255
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def best_text_color(bg_hex: str) -> str:
    return "#0E0D0C" if relative_luminance(bg_hex) > 0.55 else "#E8E2D3"
