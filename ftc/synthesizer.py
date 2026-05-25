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
        }
        for token, count in top
    ]

    synthesis = {
        "clusters": clusters,
        "totals": {
            "sources": len({r.url for r in results}),
            "tokens": sum(token_counter.values()),
            "unique_tokens": len(token_counter),
        },
        "samples": [r.to_dict() for r in results[:20]],
    }

    out = artifact_path("scrapes", "reference_synthesis.json")
    out.write_text(json.dumps(synthesis, indent=2))
    return synthesis
