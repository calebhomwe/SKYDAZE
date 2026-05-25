"""Quality gates (Section 5).

Two scorers run on every concept:
  - luxury_score        (0..1, threshold 0.82)
  - theology_depth      (0..1, threshold 0.75)

Real mode calls an LLM judge. Dry-run/mock returns deterministic stub scores
derived from concept text so the rest of the pipeline can be exercised without
a key.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass

from .config import RUN_MODE, require


@dataclass(frozen=True)
class Score:
    luxury_score: float
    theology_depth: float
    rationale: str

    def passes(self) -> bool:
        return self.luxury_score >= 0.82 and self.theology_depth >= 0.75

    def is_flagged(self) -> bool:
        return 0.75 <= self.luxury_score < 0.82


def _stub_score(concept: dict) -> Score:
    """Deterministic non-LLM score for dry-run."""
    blob = json.dumps(concept, sort_keys=True).encode()
    digest = hashlib.sha256(blob).digest()
    lux = 0.70 + (digest[0] / 255) * 0.25
    theo = 0.65 + (digest[1] / 255) * 0.30
    return Score(
        luxury_score=round(lux, 3),
        theology_depth=round(theo, 3),
        rationale="dry-run stub score (deterministic from concept hash)",
    )


_JUDGE_PROMPT = """You are the Luxury Score Auditor and Theology Depth Auditor for FTC FULL TIME CHRISTIAN.

Read the concept JSON below. Score on two axes:

1. luxury_score (0.0-1.0): Would this sit on the SSENSE or Dover Street Market wall?
   Benchmarks: Fear of God, Lemaire, Off-White at their best. 1.0 = inevitable on
   that wall. 0.5 = generic streetwear. 0.0 = mall merch.

2. theology_depth (0.0-1.0): Is the theology FELT, not READ? 1.0 = Tarkovsky meets
   Augustine. 0.75 = abstract metaphor a thoughtful viewer decodes. 0.5 = vague
   spiritual mood. 0.0 = "blessed up" tee.

Auto-zero if any FORBIDDEN term is present (Section 1 of FTC_MASTER_CONTEXT.md).

Return ONLY a JSON object: {"luxury_score": float, "theology_depth": float, "rationale": str}
"""


def score_concept(concept: dict) -> Score:
    if RUN_MODE in {"dry-run", "mock"} or not os.getenv("ANTHROPIC_API_KEY"):
        return _stub_score(concept)

    from anthropic import Anthropic  # local import keeps dry-run dep-free

    client = Anthropic(api_key=require("anthropic"))
    msg = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        system=_JUDGE_PROMPT,
        messages=[{"role": "user", "content": json.dumps(concept, indent=2)}],
    )
    text = "".join(block.text for block in msg.content if hasattr(block, "text")).strip()
    data = json.loads(text)
    return Score(
        luxury_score=float(data["luxury_score"]),
        theology_depth=float(data["theology_depth"]),
        rationale=str(data.get("rationale", "")),
    )
