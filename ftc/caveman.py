"""Caveman token-compression integration for FTC pipeline LLM calls.

Caveman (https://github.com/JuliusBrussee/caveman, MIT) is a slash-command
skill for AI coding agents. Its rule sets also work as system-prompt
prefixes that instruct any LLM to compress output ~65-75%.

Enable per-process:
    export FTC_CAVEMAN=lite     # default level, gentle compression
    export FTC_CAVEMAN=full     # fragment-based
    export FTC_CAVEMAN=ultra    # maximum

When FTC_CAVEMAN is unset or "off", behavior is unchanged.

The schema validator (`ftc/schema.py`) still enforces correctness, so
even ultra-compressed JSON responses must remain valid Section-4 payloads.
"""

from __future__ import annotations

import os
from typing import Literal

Level = Literal["off", "lite", "full", "ultra"]

_RULES: dict[str, str] = {
    "lite": (
        "Output rules:\n"
        "- Drop articles where meaning survives (a, an, the).\n"
        "- One adjective per noun max.\n"
        "- Cut filler: 'in order to', 'as a matter of fact', 'it should be noted that'.\n"
        "- Prefer numbers and symbols to words.\n"
        "- Keep JSON keys and required fields exact.\n"
        "- No prose preamble before JSON.\n"
    ),
    "full": (
        "Output rules:\n"
        "- Fragment-style. No subject pronouns where meaning is clear.\n"
        "- Cut all filler, hedges, and self-reference.\n"
        "- Adjectives only when load-bearing.\n"
        "- Numbers/symbols over words.\n"
        "- JSON keys and required fields exact, no prose.\n"
    ),
    "ultra": (
        "Output rules (ULTRA COMPRESSION):\n"
        "- Telegraphic. Verb stems where unambiguous.\n"
        "- Drop articles, copulas, hedges.\n"
        "- Prefer single tokens to phrases.\n"
        "- JSON only. No surrounding prose at all.\n"
        "- Schema correctness over verbosity in any case.\n"
    ),
}


def level() -> Level:
    raw = (os.getenv("FTC_CAVEMAN") or "").strip().lower()
    if raw in {"lite", "full", "ultra"}:
        return raw  # type: ignore[return-value]
    return "off"


def system_suffix() -> str:
    """Return the rule block to append to any LLM system prompt, or ''."""
    lvl = level()
    if lvl == "off":
        return ""
    return f"\n\n[caveman:{lvl}]\n{_RULES[lvl]}"


def apply(system_prompt: str) -> str:
    """Append the caveman rule block to an existing system prompt."""
    return system_prompt + system_suffix()
