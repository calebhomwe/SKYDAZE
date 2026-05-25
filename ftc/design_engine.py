"""Combinatorial design engine.

Produces N brand-locked designs across sections, deterministically from a
seed. Each design carries:
  - id, section, silhouette, title
  - palette (full Palette object + hex array)
  - print technique + placement
  - theological core (drawn from curated themes)
  - typography treatment
  - hardware/finish detail
  - pricing tier + MSRP + estimated COGS + target margin
  - Section-4-compliant concept JSON
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from .colors import Palette, palette_for
from .silhouettes import SECTION_SILHOUETTES

# -- curated source pools (everything brand-locked) --

THEOLOGICAL_CORES: list[str] = [
    "What the builders refused becomes the angle that holds the wall.",
    "Light reveals only what shadow has agreed to release.",
    "The well does not argue; it overflows.",
    "What remains after the fire is heavier than what burned.",
    "A door knows both rooms; it belongs to neither.",
    "Stillness is the loudest answer the river ever gives the stone.",
    "What is hidden is still wearing the room.",
    "A small bell carries a longer silence than a horn.",
    "The map and the road forgive each other slowly.",
    "Mercy keeps a key the lock cannot remember.",
    "Bread does not boast about the wheat.",
    "Every threshold is a vow with two faces.",
    "The hand that releases is the one that was carrying.",
    "A vow is a doorway you walk through twice.",
    "Dust does not negotiate; it returns.",
    "What endures is what learned to wait.",
    "The garden remembers the gardener longer than the harvest.",
    "Silence is not absence; it is a held instrument.",
    "A psalm in the throat does not need to leave the throat.",
    "Foundations argue last; cornerstones never argue.",
    "Rivers do not measure their own depth.",
    "Salt is the patience of fire.",
    "Linen knows the prayer better than the lectern.",
    "The pilgrim's shoe writes the only autobiography the road accepts.",
    "Iron does not forget the forge.",
    "Bread broken is still bread.",
    "Mercy and gravity move at the same speed.",
    "A vigil keeps its own warmth.",
    "The unwritten letter is sometimes the cleanest answer.",
    "What you carry shapes the rooms you enter.",
]

TITLES: list[str] = [
    "Cornerstone", "Veil", "Living Water", "Ember", "Threshold",
    "Vigil", "Cloister", "Cantor", "Vestibule", "Lintel",
    "Plummet", "Quiet Hour", "Foundling", "Ash Tuesday", "Wheatfield",
    "Hewn", "Mended", "Unfastened", "Garrison", "Plumbline",
    "Anchor", "Antiphon", "Vespers", "Compline", "Matins",
    "Lectionary", "Sojourn", "Salt and Linen", "Witness", "Hymnal",
    "Refuge", "Drawn Water", "Borne", "Sown", "Yoke",
    "Lampblack", "Echo Stone", "Quiet Field", "Field Marker", "Wayfarer",
    "Inheritance", "Threshold Stone", "Open Hand", "Lighthouse", "Stillwater",
    "Bell Tower", "Cloth and Vow", "Vespering", "Inner Room", "Tabernacle",
]

PRINT_TECHNIQUES: list[tuple[str, list[str]]] = [
    ("Tonal embroidery", ["chest-center", "chest-left", "sleeve-left", "hem-back"]),
    ("Puff", ["chest-center", "sleeve-left"]),
    ("Deboss", ["chest-left", "pocket"]),
    ("Screen", ["chest-center", "hood-interior"]),
    ("Discharge", ["chest-center", "side-seam"]),
    ("Woven label", ["side-seam", "hood-interior"]),
]

TYPOGRAPHY_TREATMENTS: list[str] = [
    "Worn humanist serif, 12pt tonal embroidery, hidden interior placement",
    "Display grotesque, 9pt deboss",
    "Mono with humanist hand-feel, 10pt embroidery, hem inside-out",
    "Geometric sans, 14pt screen, single colorway",
    "Bone-thin serif, woven label only",
    "All-caps grotesque, 11pt puff, single mark",
    "No typography; geometric mark only",
    "Hand-set wordmark from archival type",
]

HARDWARE_DETAILS: list[str] = [
    "Matte black snap closures; cornerstone metaphor noted in spec",
    "Bone-toned woven label; interior placement",
    "Dark walnut horn buttons; archival shape",
    "Matte gunmetal eyelets; subtle drape weight cue",
    "No external hardware; tonal twin-needle stitching only",
    "Brass-tone YKK Excella zipper, dyed matte",
    "Custom drawcord with cast pewter tip",
]

# Section taxonomy + sizing
SECTION_PLAN: dict[str, dict] = {
    "tee": {
        "count": 1000,
        "msrp_band": (80, 160),
        "cogs_band": (18, 36),
        "fit_families": ["relaxed", "boxy", "dropped-shoulder"],
    },
}


@dataclass
class Design:
    id: str
    section: str
    silhouette: str
    title: str
    theological_core: str
    typography_layout: str
    palette: Palette
    print_technique: str
    print_placement: str
    hardware_detail: str
    fit_family: str
    msrp_usd: int
    estimated_cogs_usd: int
    margin_pct: float
    aesthetic_direction: str
    fal_ai_visual_prompt: str
    novita_video_prompt: str
    nano_banana_mockup_prompt: str
    reference_source_tags: list[str]
    promo_hook: str

    def as_concept_json(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "theological_core": self.theological_core,
            "aesthetic_direction": self.aesthetic_direction,
            "typography_layout": self.typography_layout,
            "color_palette": list(self.palette.hexes)[:5],
            "print_technique": self.print_technique,
            "fal_ai_visual_prompt": self.fal_ai_visual_prompt,
            "novita_video_prompt": self.novita_video_prompt,
            "nano_banana_mockup_prompt": self.nano_banana_mockup_prompt,
            "reference_source_tags": self.reference_source_tags,
            "promo_hook": self.promo_hook,
        }

    def as_catalog_row(self) -> dict:
        return {
            "id": self.id,
            "section": self.section,
            "silhouette": self.silhouette,
            "title": self.title,
            "palette_name": self.palette.name,
            "palette_family": self.palette.family,
            "palette_hex": list(self.palette.hexes),
            "print_technique": self.print_technique,
            "print_placement": self.print_placement,
            "hardware_detail": self.hardware_detail,
            "fit_family": self.fit_family,
            "msrp_usd": self.msrp_usd,
            "estimated_cogs_usd": self.estimated_cogs_usd,
            "margin_pct": round(self.margin_pct, 1),
            "theological_core": self.theological_core,
        }


def _seeded(seed: str) -> random.Random:
    return random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8], "big"))


def _msrp_for(section: str, palette: Palette, technique: str, rng: random.Random) -> int:
    lo, hi = SECTION_PLAN[section]["msrp_band"]
    base = rng.randint(lo, hi)
    # Bump price for premium techniques
    if technique in {"Tonal embroidery", "Deboss"}:
        base = int(base * 1.10)
    if palette.family in {"earth-neutral", "triadic-restrained"}:
        base = int(base * 1.05)
    return min(hi + 20, base)


def _cogs_for(section: str, technique: str, rng: random.Random) -> int:
    lo, hi = SECTION_PLAN[section]["cogs_band"]
    base = rng.randint(lo, hi)
    if technique in {"Tonal embroidery", "Deboss", "Discharge"}:
        base = int(base * 1.15)
    return base


def _generate_one(section: str, idx: int, seed: str) -> Design:
    fid = f"FTC-{section[:2].upper()}-{idx:04d}"
    rng = _seeded(f"{seed}|{section}|{idx}|content")

    silhouette = rng.choice([s for s, _ in SECTION_SILHOUETTES[section]])
    palette = palette_for(section, idx, seed=seed)
    technique, placements = rng.choice(PRINT_TECHNIQUES)
    placement = rng.choice(placements)
    title = rng.choice(TITLES)
    theological_core = rng.choice(THEOLOGICAL_CORES)
    typography = rng.choice(TYPOGRAPHY_TREATMENTS)
    hardware = rng.choice(HARDWARE_DETAILS)
    fit_family = rng.choice(SECTION_PLAN[section]["fit_families"])
    msrp = _msrp_for(section, palette, technique, rng)
    cogs = _cogs_for(section, technique, rng)
    margin = (msrp - cogs) / msrp * 100

    aesthetic = (
        f"Standalone vector graphic built for tee, hat, hoodie, tote, and label use; "
        f"{palette.hexes[0]} field with {palette.hexes[1] if len(palette.hexes)>1 else palette.hexes[0]} accent; "
        f"{technique.lower()} production mark at {placement}; quiet architecture, chrome-text restraint, "
        f"badge geometry, and negative space carry the composition."
    )
    fal_prompt = (
        f"High-definition product mockup of standalone FTC vector artwork applied to a 300gsm "
        f"garment-washed cotton {silhouette.replace('-', ' ')} in {palette.hexes[0]}, "
        f"subtle {technique.lower()} mark at {placement}, no people, no portrait, no illustration scene, "
        f"north window light, plaster backdrop, 4:5 aspect ratio, luxury streetwear, Lemaire restraint"
    )
    novita_prompt = (
        f"7s clip: slow tilt across a draped {silhouette.replace('-', ' ')} in {palette.hexes[0]}, "
        f"north-window light shifts to ember; fabric settles into stillness"
    )
    nano_prompt = (
        f"Apply {technique.lower()} ({'40wt thread' if 'embroidery' in technique.lower() else 'matte'}) "
        f"to {silhouette} template in {palette.hexes[0]}; accent {palette.hexes[1] if len(palette.hexes)>1 else palette.hexes[0]}; "
        f"{placement} placement"
    )

    tags = [
        palette.family,
        technique.lower().replace(" ", "_"),
        section,
        fit_family,
        "pinterest_graphic_tee",
        "reddit_streetwearstartup",
        "youtube_print_design",
    ]
    promo_hook = (
        f"Caption: museum-label cadence, <= 35 words. "
        f"Reel with sub-bass drone or single field recording."
    )

    return Design(
        id=fid,
        section=section,
        silhouette=silhouette,
        title=title,
        theological_core=theological_core,
        typography_layout=typography,
        palette=palette,
        print_technique=technique,
        print_placement=placement,
        hardware_detail=hardware,
        fit_family=fit_family,
        msrp_usd=msrp,
        estimated_cogs_usd=cogs,
        margin_pct=margin,
        aesthetic_direction=aesthetic,
        fal_ai_visual_prompt=fal_prompt,
        novita_video_prompt=novita_prompt,
        nano_banana_mockup_prompt=nano_prompt,
        reference_source_tags=tags,
        promo_hook=promo_hook,
    )


def generate_collection(seed: str = "FTC-COLLECTION-V1") -> list[Design]:
    out: list[Design] = []
    for section, plan in SECTION_PLAN.items():
        for i in range(plan["count"]):
            out.append(_generate_one(section, i + 1, seed))
    return out
