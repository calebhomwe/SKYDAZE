"""Reference scraping (tier-6).

Primary: Firecrawl (JS-rendered).
Fallback: httpx + BeautifulSoup (static).

Honors robots.txt, rate-limits per host, persists raw + parsed output.
Dry-run mode writes a synthesized fixture so the pipeline can be exercised
without paying for a Firecrawl call.
"""

from __future__ import annotations

import json
import time
import urllib.robotparser
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import KEYS, RUN_MODE, artifact_path


@dataclass
class ScrapeResult:
    url: str
    source: str  # "firecrawl" | "bs4" | "dry-run-stub"
    title: str
    text: str
    tokens: list[str] = field(default_factory=list)
    raw_path: Path | None = None

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "source": self.source,
            "title": self.title,
            "text": self.text[:4000],
            "tokens": self.tokens,
            "raw_path": str(self.raw_path) if self.raw_path else None,
        }


def _host(url: str) -> str:
    return urlparse(url).netloc


def _robots_allows(url: str, user_agent: str) -> bool:
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{urlparse(url).scheme}://{_host(url)}/robots.txt")
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True  # if robots.txt unreachable, default to allow but stay polite


def _extract_tokens(text: str) -> list[str]:
    """Cheap token surface — clusters are built downstream in synthesizer.py."""
    keywords = [
        "tonal", "embroidery", "puff", "deboss", "discharge", "garment-washed",
        "heavyweight", "drop-shoulder", "minimalist", "monochrome", "earth-tone",
        "negative space", "matte hardware", "sacred geometry", "architectural",
        "monastic", "editorial", "luxury", "restraint", "graphic tee",
        "streetwear", "vintage", "chrome text", "badge", "wordmark", "typography",
        "oversized", "distressed", "halftone", "bootleg", "y2k", "racing",
        "tribal", "metallic", "scalable", "vector", "mockup", "hat", "cap",
        "community", "feedback", "drop", "screen print", "dtg", "heat press",
    ]
    lower = text.lower()
    return [k for k in keywords if k in lower]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=16))
def _firecrawl(url: str) -> dict:
    api_key = KEYS.firecrawl
    if not api_key:
        raise RuntimeError("FIRECRAWL_API_KEY missing")
    resp = httpx.post(
        "https://api.firecrawl.dev/v1/scrape",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"url": url, "formats": ["markdown", "html"]},
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=16))
def _bs4_fetch(url: str, user_agent: str) -> str:
    resp = httpx.get(url, headers={"User-Agent": user_agent}, timeout=30.0, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def _dry_run_stub(url: str, category: str) -> ScrapeResult:
    """Synthetic but believable scrape fixture for offline development."""
    stub_text = (
        f"[DRY-RUN STUB] {category} reference from {url}. "
        "Heavyweight cotton, tonal embroidery, garment-washed finish, "
        "drop-shoulder silhouette, matte hardware, monochrome palette, "
        "architectural negative space, streetwear graphic tee typography, "
        "chrome text, vintage badge systems, scalable vector marks, and "
        "community feedback loops for drops."
    )
    return ScrapeResult(
        url=url,
        source="dry-run-stub",
        title=f"{category} stub",
        text=stub_text,
        tokens=_extract_tokens(stub_text),
    )


def scrape_url(
    url: str,
    category: str,
    user_agent: str = "FTC-ReferenceBot/0.1",
    respect_robots: bool = True,
) -> ScrapeResult:
    if RUN_MODE in {"dry-run", "mock"}:
        return _dry_run_stub(url, category)

    if respect_robots and not _robots_allows(url, user_agent):
        return ScrapeResult(
            url=url, source="skipped", title="robots-blocked",
            text="", tokens=[],
        )

    if KEYS.firecrawl:
        try:
            data = _firecrawl(url)
            text = (data.get("data") or {}).get("markdown") or ""
            title = (data.get("data") or {}).get("metadata", {}).get("title", "")
            raw_path = artifact_path("scrapes", "raw", _host(url), f"{int(time.time())}.json")
            raw_path.write_text(json.dumps(data, indent=2))
            return ScrapeResult(
                url=url, source="firecrawl", title=title, text=text,
                tokens=_extract_tokens(text), raw_path=raw_path,
            )
        except Exception:
            pass  # fall through to bs4

    try:
        html = _bs4_fetch(url, user_agent)
        soup = BeautifulSoup(html, "lxml")
        title = (soup.title.string if soup.title else "") or ""
        text = soup.get_text(separator="\n", strip=True)
        return ScrapeResult(
            url=url, source="bs4", title=title.strip(), text=text,
            tokens=_extract_tokens(text),
        )
    except Exception as exc:
        return ScrapeResult(
            url=url, source="error", title=str(exc)[:80], text="", tokens=[],
        )
