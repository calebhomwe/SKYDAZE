"""YouTube intelligence module — transcript harvesting and style synthesis.

Tier 16 agents consume this module to extract luxury Christian streetwear
style signals from curated YouTube channels. Dry-run returns stub data.
Real mode requires no API key (youtube-transcript-api is public).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .config import RUN_MODE, artifact_path

# Curated channels and playlists for luxury / Christian streetwear reference.
# Organized by signal type so the synthesizer can weight appropriately.
YOUTUBE_TARGETS: dict[str, list[dict[str, str]]] = {
    "luxury_streetwear_aesthetics": [
        {"channel": "SSENSE", "query": "editorial lookbook luxury streetwear"},
        {"channel": "Fear of God", "query": "fear of god collection lookbook"},
        {"channel": "Highsnobiety", "query": "luxury streetwear trend report"},
        {"channel": "Complex", "query": "best dressed streetwear fits"},
        {"channel": "GQ", "query": "luxury streetwear styling guide"},
        {"channel": "Vogue", "query": "editorial fashion streetwear"},
    ],
    "christian_culture_signals": [
        {"channel": "Lecrae Official", "query": "lecrae fashion style faith culture"},
        {"channel": "NF Music", "query": "nf christian hip hop aesthetic"},
        {"channel": "Andy Mineo", "query": "andy mineo fashion faith"},
        {"channel": "Propaganda Official", "query": "propaganda rapper fashion"},
        {"channel": "Trip Lee Music", "query": "trip lee christian streetwear"},
        {"channel": "Social Club Misfits", "query": "christian streetwear artists"},
    ],
    "trap_cinematic_references": [
        {"channel": "Young Thug VEVO", "query": "young thug fashion editorial"},
        {"channel": "Gunna VEVO", "query": "gunna fashion drip aesthetic"},
        {"channel": "Travis Scott", "query": "travis scott fashion cactus jack"},
        {"channel": "ASAP Mob", "query": "asap mob fashion editorial"},
    ],
    "streetwear_culture": [
        {"channel": "Hypebeast", "query": "luxury streetwear collection 2025"},
        {"channel": "Sneaker Shopping", "query": "streetwear fashion interview"},
        {"channel": "StockX", "query": "streetwear resale culture drops"},
        {"channel": "Sole Collector", "query": "sneaker streetwear lifestyle"},
    ],
    "garment_craft": [
        {"channel": "BoohooMAN", "query": "boohooman photoshoot editorial"},
        {"channel": "ASOS", "query": "fashion editorial menswear photography"},
        {"channel": "Zara Man", "query": "zara man editorial lookbook"},
    ],
}

# Specific video IDs to always harvest (manually curated high-signal references).
# These are publicly available videos with auto-generated or community transcripts.
PRIORITY_VIDEO_IDS: list[str] = [
    # Add high-signal video IDs here as the brand curates them.
    # Format: standard YouTube 11-char video ID.
]

_STUB_SYNTHESIS: dict[str, Any] = {
    "source": "stub",
    "total_transcripts": 5,
    "style_tokens": {
        "silhouette": ["oversized", "drop-shoulder", "boxy-fit", "elongated-torso"],
        "material": ["heavyweight-cotton", "300gsm-fleece", "garment-washed", "tonal-texture"],
        "color_language": ["bone", "ink", "slate", "oxidized-rust", "ash"],
        "typography_register": ["sparse", "humanist-serif", "grotesque", "no-logo-dominance"],
        "mood": ["monastic", "slow", "weight", "restraint", "quiet-luxury"],
        "christian_aesthetic": [
            "abstract-faith",
            "hidden-scripture",
            "geometry-over-literal",
            "silence-as-statement",
        ],
        "cultural_reference": [
            "trap-influenced-youth",
            "campus-church-adjacent",
            "gospel-rap-aligned",
            "faith-without-cringe",
        ],
    },
    "anti_signals": [
        "neon-bright-colors",
        "cross-as-prop",
        "bible-verse-literal",
        "fast-fashion-silhouette",
        "cartoon-faith",
        "loud-logo-worship",
    ],
    "drop_direction": (
        "The target customer moves between Sunday service and the city. "
        "They want fabric that speaks quietly — heavyweight enough to feel intentional, "
        "muted enough to survive the gallery. Faith lives in the construction, not the slogan."
    ),
    "recommended_palette_families": ["earth-neutral", "high-contrast-mono", "two-square-lv-style"],
    "recommended_print_techniques": ["tonal-embroidery", "deboss", "discharge"],
}


def fetch_transcript(video_id: str) -> str | None:
    """Return cleaned transcript text for a YouTube video ID, or None on failure."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable
    except ImportError:
        return None

    try:
        entries = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        return " ".join(e["text"] for e in entries).strip()
    except (NoTranscriptFound, VideoUnavailable, Exception):
        return None


def search_and_fetch(query: str, max_results: int = 3) -> list[dict[str, str]]:
    """Search YouTube for query and return transcripts. Requires yt-dlp."""
    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        return []

    import subprocess
    import shutil

    if not shutil.which("yt-dlp"):
        return []

    cmd = [
        "yt-dlp",
        f"ytsearch{max_results}:{query}",
        "--get-id",
        "--quiet",
        "--no-warnings",
        "--flat-playlist",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        video_ids = [vid.strip() for vid in result.stdout.strip().splitlines() if vid.strip()]
    except Exception:
        return []

    results = []
    for vid_id in video_ids[:max_results]:
        transcript = fetch_transcript(vid_id)
        if transcript:
            results.append({"video_id": vid_id, "transcript": transcript, "query": query})
    return results


def _extract_style_tokens(transcripts: list[str]) -> dict[str, list[str]]:
    """Pull style signals from raw transcript text using keyword matching."""
    combined = " ".join(transcripts).lower()

    silhouette_terms = [
        "oversized", "boxy", "drop shoulder", "elongated", "wide leg",
        "relaxed fit", "slim", "structured", "minimal",
    ]
    material_terms = [
        "heavyweight", "fleece", "cotton", "linen", "denim", "wool",
        "garment washed", "tonal", "texture", "weight",
    ]
    color_terms = [
        "bone", "cream", "slate", "ash", "sand", "olive", "ink", "navy",
        "rust", "ecru", "charcoal", "stone", "camel", "chocolate",
    ]
    mood_terms = [
        "quiet", "subtle", "restrained", "minimal", "clean", "intentional",
        "elevated", "premium", "quality", "craft", "slow",
    ]
    faith_terms = [
        "faith", "god", "christian", "spiritual", "prayer", "church",
        "gospel", "worship", "scripture", "blessed", "grace",
    ]

    def _find(terms: list[str]) -> list[str]:
        return [t for t in terms if t in combined]

    return {
        "silhouette": _find(silhouette_terms) or ["oversized", "relaxed-fit"],
        "material": _find(material_terms) or ["heavyweight-cotton", "garment-washed"],
        "color_language": _find(color_terms) or ["bone", "ash", "slate"],
        "mood": _find(mood_terms) or ["restrained", "minimal"],
        "faith_signals": _find(faith_terms) or ["faith", "grace"],
    }


def _clean_transcript(raw: str) -> str:
    raw = re.sub(r"\[.*?\]", "", raw)
    raw = re.sub(r"\s+", " ", raw)
    return raw.strip()


def synthesize(transcripts: list[dict[str, str]]) -> dict[str, Any]:
    """Distill harvested transcripts into brand-relevant style tokens."""
    if not transcripts:
        return _STUB_SYNTHESIS

    raw_texts = [_clean_transcript(t.get("transcript", "")) for t in transcripts]
    tokens = _extract_style_tokens(raw_texts)

    return {
        "source": "youtube_harvest",
        "total_transcripts": len(transcripts),
        "style_tokens": {
            **tokens,
            "typography_register": ["sparse", "humanist-serif", "no-logo-dominance"],
            "christian_aesthetic": [
                "abstract-faith",
                "hidden-scripture",
                "geometry-over-literal",
            ],
            "cultural_reference": ["trap-influenced-youth", "faith-without-cringe"],
        },
        "anti_signals": [
            "neon-bright-colors",
            "cross-as-prop",
            "bible-verse-literal",
            "fast-fashion-silhouette",
        ],
        "drop_direction": _build_drop_direction(tokens),
        "recommended_palette_families": ["earth-neutral", "high-contrast-mono"],
        "recommended_print_techniques": ["tonal-embroidery", "deboss", "discharge"],
    }


def _build_drop_direction(tokens: dict[str, list[str]]) -> str:
    palette = ", ".join(tokens.get("color_language", ["bone", "ash"])[:3])
    mood = ", ".join(tokens.get("mood", ["restrained"])[:2])
    silhouette = ", ".join(tokens.get("silhouette", ["oversized"])[:2])
    return (
        f"YouTube intelligence signals: {mood} mood, {silhouette} silhouette, "
        f"{palette} palette family. Faith lives in the construction, not the slogan."
    )


def run_harvest(
    categories: list[str] | None = None,
    max_per_query: int = 2,
    save: bool = True,
) -> dict[str, Any]:
    """Harvest transcripts across target categories and return synthesis.

    In dry-run mode returns stub data without any network calls.
    """
    if RUN_MODE in {"dry-run", "mock"}:
        return _STUB_SYNTHESIS

    targets = categories or list(YOUTUBE_TARGETS.keys())
    all_transcripts: list[dict[str, str]] = []

    # Priority video IDs first.
    for vid_id in PRIORITY_VIDEO_IDS:
        transcript = fetch_transcript(vid_id)
        if transcript:
            all_transcripts.append({"video_id": vid_id, "transcript": transcript, "query": "priority"})

    # Search-based harvest.
    for category in targets:
        for target in YOUTUBE_TARGETS.get(category, []):
            query = target["query"]
            results = search_and_fetch(query, max_results=max_per_query)
            all_transcripts.extend(results)

    synthesis = synthesize(all_transcripts)

    if save:
        out = artifact_path("research", "youtube_synthesis.json")
        out.write_text(json.dumps(synthesis, indent=2))

    return synthesis


if __name__ == "__main__":
    import sys
    dry = "--real" not in sys.argv
    if dry:
        os.environ.setdefault("FTC_RUN_MODE", "dry-run")
    result = run_harvest()
    print(json.dumps(result, indent=2))
