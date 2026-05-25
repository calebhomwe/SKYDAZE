"""Section 1 forbidden-term scanner. One hit, instant kill."""

from __future__ import annotations

import re

FORBIDDEN_PATTERNS: dict[str, str] = {
    "skull": r"\bskulls?\b",
    "clipart_religion": r"\b(clipart|stock\s+religious|royalty[-\s]free\s+cross)\b",
    "cheap_typography": r"\b(comic\s*sans|papyrus|impact\b|brush\s*script)\b",
    "overt_proselytizing": r"\b(repent|get\s+saved|hell\s*awaits|sinner|believe\s+or\s+burn)\b",
    "neon_saturation": r"\b(neon|hi[-\s]?vis|fluoro|day[-\s]?glo)\b",
    "literal_biblical_scene": r"\b(crucifixion\s+scene|garden\s+of\s+eden\s+illustration|jesus\s+illustrated)\b",
    "cross_as_prop": r"\b(cross[-\s]?as[-\s]?prop|wooden\s+cross\s+held|crucifix\s+as\s+accessory)\b",
    "cartoon_aesthetic": r"\b(cartoon|chibi|anime\s+style|disney[-\s]?style)\b",
    "fast_fashion_silhouette": r"\b(fast\s+fashion|shein|temu|h\s*&\s*m\s+cut)\b",
    "generic_worship_lyric": r"\b(blessed\s+up|god\s+is\s+good\s+all\s+the\s+time|jesus\s+loves\s+you\s+sweater)\b",
}

_COMPILED = {name: re.compile(pat, re.IGNORECASE) for name, pat in FORBIDDEN_PATTERNS.items()}


def scan(text: str) -> list[str]:
    """Return the list of forbidden categories present in `text`."""
    if not text:
        return []
    return [name for name, pat in _COMPILED.items() if pat.search(text)]


def scan_concept(concept: dict) -> list[tuple[str, str]]:
    """Walk every string field; return (field, category) for each hit."""
    hits: list[tuple[str, str]] = []
    for key, value in concept.items():
        if isinstance(value, str):
            for cat in scan(value):
                hits.append((key, cat))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, str):
                    for cat in scan(item):
                        hits.append((f"{key}[{i}]", cat))
    return hits
