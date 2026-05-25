"""Reference Synthesizer (agent FTC-056).

Clusters raw scrape tokens into <= 10 Section-2 reference clusters with
attribution. Pure-Python clustering by token co-occurrence; no LLM call.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict

from .config import artifact_path
from .scrapers import ScrapeResult

MAX_CLUSTERS = 10

TREND_APPLICATIONS: dict[str, str] = {
    "chrome text": "Use chrome as a restrained outline or shadow treatment, not a glossy full-raster effect.",
    "vintage": "Keep vintage cues in badge framing, faded ink, and worn spacing instead of borrowed logos.",
    "badge": "Build compact marks that survive on caps, labels, and pocket prints.",
    "wordmark": "Favor short stacked lockups with wide tracking and strong silhouette at thumbnail size.",
    "typography": "Treat type as the graphic. Every text asset needs hierarchy, spacing, and production contrast.",
    "negative space": "Let blank space do the work so designs do not become poster art.",
    "vector": "Keep the master artwork scalable, transparent, and free of embedded raster images.",
    "hat": "Avoid detail thinner than embroidery can hold on a curved cap front.",
    "cap": "Use compact geometry and fewer words for cap placement.",
    "community": "Design variants should invite feedback: clear first read, enough detail for a second look.",
    "screen print": "Prefer one or two inks with clean separations.",
    "puff": "Reserve puff for bold lines and short wordmarks.",
    "embroidery": "Use embroidery on small marks and tonal badges.",
}


def synthesize(results: list[ScrapeResult]) -> dict:
    if not results:
        return {"clusters": [], "totals": {"sources": 0, "tokens": 0}}

    token_to_sources: dict[str, list[str]] = defaultdict(list)
    token_counter: Counter = Counter()

    for r in results:
        for t in r.tokens:
            token_to_sources[t].append(r.url)
            token_counter[t] += 1

    top = token_counter.most_common(MAX_CLUSTERS)
    clusters = [
        {
            "token": token,
            "frequency": count,
            "sources": sorted(set(token_to_sources[token])),
            "application": TREND_APPLICATIONS.get(token, "Use as a low-volume cue inside the FTC restraint rules."),
        }
        for token, count in top
    ]

    trend_brief = [
        "Primary output should be standalone scalable artwork, not model imagery.",
        "Keep marks portable across tees, caps, hoodies, totes, and labels.",
        "Use bold typography, badge geometry, and restrained chrome or vintage cues.",
        "Keep palettes muted. Use monochrome, earth tones, and high-contrast bone plus ink.",
        "Avoid people, literal scenes, novelty fonts, borrowed logos, skulls, and noisy poster layouts.",
    ]

    synthesis = {
        "clusters": clusters,
        "totals": {
            "sources": len({r.url for r in results}),
            "tokens": sum(token_counter.values()),
            "unique_tokens": len(token_counter),
        },
        "trend_brief": trend_brief,
        "samples": [r.to_dict() for r in results[:20]],
    }

    out = artifact_path("scrapes", "reference_synthesis.json")
    out.write_text(json.dumps(synthesis, indent=2))
    return synthesis
