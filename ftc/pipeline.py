"""Core pipeline orchestration for the FTC design generation flow."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from ftc.config import PipelineConfig, validate_no_forbidden
from ftc.models import DesignConcept, QualityScore

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Raised when a pipeline step fails."""


class ConceptGenerator:
    """Generates design concepts via OpenRouter (DeepSeek-V3 / Qwen-Max)."""

    SYSTEM_PROMPT = (
        "You are a luxury Christian streetwear concept generator for FTC FULL TIME CHRISTIAN. "
        "Generate design concepts that embody quiet elegance meets theological edge. "
        "Output MUST be valid JSON matching the DesignConcept schema."
    )

    def __init__(self, config: PipelineConfig, model: str = "deepseek/deepseek-chat"):
        self.config = config
        self.model = model

    async def generate(self, prompt: str) -> dict[str, Any]:
        """Generate a design concept from a creative prompt."""
        if not self.config.openrouter_api_key:
            raise PipelineError("OPENROUTER_API_KEY not configured")

        violations = validate_no_forbidden(prompt)
        if violations:
            raise PipelineError(f"Prompt contains forbidden terms: {violations}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return json.loads(content)

    def validate_concept(self, raw: dict[str, Any]) -> DesignConcept:
        """Parse and validate a raw concept dict against the schema."""
        return DesignConcept.model_validate(raw)

    @staticmethod
    def score_concept(concept: DesignConcept) -> QualityScore:
        """Placeholder scoring — real scoring requires LLM evaluation."""
        has_theology = bool(concept.theological_core.strip())
        has_palette = len(concept.color_palette) >= 2
        has_technique = bool(concept.print_technique.strip())

        luxury = 0.85 if (has_palette and has_technique) else 0.70
        theology = 0.80 if has_theology else 0.50

        return QualityScore(luxury_score=luxury, theology_depth=theology)


class ReferenceScraper:
    """Scrapes design references via Firecrawl API with BeautifulSoup fallback."""

    def __init__(self, config: PipelineConfig):
        self.config = config

    async def scrape(self, url: str) -> dict[str, Any]:
        """Scrape a URL for design references."""
        if self.config.firecrawl_api_key:
            return await self._scrape_firecrawl(url)
        return await self._scrape_fallback(url)

    async def _scrape_firecrawl(self, url: str) -> dict[str, Any]:
        """Scrape via Firecrawl API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={"Authorization": f"Bearer {self.config.firecrawl_api_key}"},
                json={"url": url, "formats": ["markdown"]},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def _scrape_fallback(self, url: str) -> dict[str, Any]:
        """Fallback: fetch raw HTML and parse with BeautifulSoup."""
        from bs4 import BeautifulSoup

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0, follow_redirects=True)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        return {
            "title": soup.title.string if soup.title else "",
            "text": soup.get_text(separator="\n", strip=True)[:5000],
            "source": url,
        }
