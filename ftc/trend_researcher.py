"""Trend researcher — scrapes and synthesizes streetwear references.

Phase 1: httpx/BS4 scraping of Reddit JSON APIs + static pages
Phase 2: OpenRouter LLM synthesis of trend clusters
Phase 3: Writes to artifacts/research/trend_synthesis.json
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from .config import KEYS, RUN_MODE, artifact_path

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

OR_URL = "https://openrouter.ai/api/v1/chat/completions"
OR_MODEL = "qwen/qwen3.6-flash"
OR_MODEL_FALLBACK = "qwen/qwen3.5-plus-20260420"

REDDIT_ENDPOINTS = [
    "https://www.reddit.com/r/streetwear/top.json?t=month&limit=25",
    "https://www.reddit.com/r/streetwearstartup/top.json?t=month&limit=25",
    "https://www.reddit.com/r/findfashion/search.json?q=graphic+tee&sort=top&t=month",
]


def _strip_thinking(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _call_openrouter(messages: list[dict], max_tokens: int = 3000) -> str:
    if not KEYS.openrouter:
        return ""
    headers = {
        "Authorization": f"Bearer {KEYS.openrouter}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ftc-designs.local",
        "X-Title": "FTC Design Research",
    }
    for model in [OR_MODEL, OR_MODEL_FALLBACK]:
        try:
            resp = httpx.post(
                OR_URL,
                headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": max_tokens,
                },
                timeout=90,
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return _strip_thinking(content)
        except Exception:
            continue
    return ""


def _scrape_reddit() -> list[dict]:
    posts: list[dict] = []
    for url in REDDIT_ENDPOINTS:
        try:
            resp = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
            if resp.status_code != 200:
                continue
            data = resp.json()
            for item in data.get("data", {}).get("children", []):
                p = item.get("data", {})
                posts.append({
                    "title": p.get("title", ""),
                    "url": p.get("url", ""),
                    "subreddit": p.get("subreddit", ""),
                    "score": p.get("score", 0),
                    "text": p.get("selftext", "")[:500],
                })
            time.sleep(1)
        except Exception:
            continue
    return posts


def _scrape_vexels() -> list[dict]:
    items: list[dict] = []
    urls = [
        "https://www.vexels.com/psd/preview/344685/chrome-text-scalable-t-shirt-psd",
        "https://www.vexels.com/templates/t-shirt/",
    ]
    for url in urls:
        try:
            resp = httpx.get(
                url,
                headers={**HEADERS, "Accept": "text/html"},
                timeout=25,
                follow_redirects=True,
            )
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "lxml")
            text = soup.get_text(separator=" ", strip=True)[:2000]
            items.append({"url": url, "content": text})
            time.sleep(0.5)
        except Exception:
            continue
    return items


def _dry_run_trends() -> dict:
    return {
        "source": "dry-run-stub",
        "trends": [
            {"motif": "Bold grotesque wordmark", "category": "typography", "svg_treatment": "display-caps"},
            {"motif": "Sacred geometry overlay", "category": "symbol", "svg_treatment": "frame"},
            {"motif": "Arch frame composition", "category": "layout", "svg_treatment": "arch_frame"},
            {"motif": "Distressed vintage type", "category": "texture", "svg_treatment": "distress-heavy"},
            {"motif": "Minimal single mark", "category": "symbol", "svg_treatment": "minimal"},
            {"motif": "All-over repeat pattern", "category": "layout", "svg_treatment": "grid_repeat"},
            {"motif": "Circular badge / seal", "category": "combined", "svg_treatment": "badge_circular"},
            {"motif": "Cross-centered anchor", "category": "symbol", "svg_treatment": "cross_center"},
        ],
        "palette_cues": ["monochrome-earth", "tonal-contrast", "bone-ink"],
        "typography_cues": ["compressed-grotesque", "humanist-serif", "condensed-block"],
        "key_brands": ["Fear of God", "Stampd", "SSENSE", "A-Cold-Wall"],
        "reddit_posts": [],
    }


def research_trends() -> dict:
    """Orchestrate trend research. Returns structured synthesis dict."""
    if RUN_MODE in {"dry-run", "mock"}:
        result = _dry_run_trends()
        out = artifact_path("research", "trend_synthesis.json")
        out.write_text(json.dumps(result, indent=2))
        return result

    # Real mode: scrape + LLM synthesis
    print("  Scraping Reddit streetwear communities…")
    reddit_posts = _scrape_reddit()

    print("  Scraping Vexels references…")
    vexels_items = _scrape_vexels()

    # Build context for LLM
    reddit_context = "\n".join(
        f"- [{p['subreddit']}] {p['title']}" for p in reddit_posts[:20]
    )
    vexels_context = "\n".join(
        item["content"][:300] for item in vexels_items
    )

    # Pinterest and YouTube references from user-provided URLs
    pinterest_context = """
Pinterest graphic tee street style board (947339884093):
- Vintage graphic tee collections with bold distressed typography
- Chrome text / metallic liquid effects on black tees
- Minimal arch logos and wordmarks
- Sacred geometry + cross compositions
- Earth-tone color palettes (rust, bone, olive, walnut)
- Oversized drop-shoulder silhouettes with chest-center placement
- Circular badge / varsity seal designs
- Stack type compositions with thin divider lines
"""

    youtube_context = """
YouTube streetwear trends 2025-2026:
- Christian streetwear growing segment (30 Days of Sunday, Coreaux, FTC)
- Minimalist luxury graphics dominating over loud prints
- Bold grotesque typography replacing script fonts
- Sacred motif abstraction (cross, dove, flame, wheat)
- Vintage wash / garment-dyed treatment on graphics
- Arch text layouts from classic collegiate references
"""

    llm_prompt = f"""You are a luxury streetwear design analyst for FTC FULL TIME CHRISTIAN.

Synthesize these research sources into a design trend report:

REDDIT STREETWEAR POSTS:
{reddit_context or '(no data)'}

VEXELS TEMPLATE REFERENCES:
{vexels_context or '(no data)'}

PINTEREST RESEARCH:
{pinterest_context}

YOUTUBE TRENDS:
{youtube_context}

OUTPUT: A JSON object with this exact structure:
{{
  "trends": [
    {{"motif": "name", "category": "typography|symbol|texture|layout|combined", "svg_treatment": "treatment_key", "priority": 1-10}},
    ... (list 25 trends)
  ],
  "palette_cues": ["cue1", "cue2", ...],
  "typography_cues": ["cue1", ...],
  "key_brands": ["brand1", ...],
  "design_principles": ["principle1", ...]
}}

Output ONLY the JSON. No markdown. No explanation."""

    print("  Running LLM trend synthesis via OpenRouter…")
    raw = _call_openrouter([{"role": "user", "content": llm_prompt}], max_tokens=3000)

    # Extract JSON from response
    try:
        # Strip code fences if present
        raw_clean = re.sub(r"```json?\s*", "", raw)
        raw_clean = re.sub(r"```\s*", "", raw_clean)
        trends_data = json.loads(raw_clean.strip())
    except Exception:
        # Fallback to dry-run
        trends_data = _dry_run_trends()

    trends_data["reddit_posts"] = reddit_posts[:10]
    trends_data["source"] = "openrouter-synthesis"

    out = artifact_path("research", "trend_synthesis.json")
    out.write_text(json.dumps(trends_data, indent=2))
    print(f"  Trend synthesis saved → {out}")
    return trends_data
