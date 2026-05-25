"""Configuration management following Section 6 security protocol."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class PipelineConfig:
    """All credentials loaded via environment variables — never hardcoded."""

    openrouter_api_key: str = ""
    fal_ai_api_key: str = ""
    firecrawl_api_key: str = ""
    novita_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    fal_ai_base_url: str = "https://fal.run"

    # Quality gate thresholds from Section 5
    luxury_score_threshold: float = 0.82
    theology_depth_threshold: float = 0.75
    auto_kill_threshold: float = 0.60


def load_config(env_path: Path | None = None) -> PipelineConfig:
    """Load pipeline config from .env file and environment variables."""
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    return PipelineConfig(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        fal_ai_api_key=os.getenv("FAL_AI_API_KEY", ""),
        firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY", ""),
        novita_api_key=os.getenv("NOVITA_API_KEY", ""),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        fal_ai_base_url=os.getenv("FAL_AI_BASE_URL", "https://fal.run"),
    )


# Forbidden terms from Section 1
FORBIDDEN_TERMS: frozenset[str] = frozenset(
    {
        "skull",
        "skulls",
        "clipart",
        "neon",
        "cartoon",
        "generic worship",
        "fast fashion",
        "crosses-as-props",
    }
)


def validate_no_forbidden(text: str) -> list[str]:
    """Check text against the forbidden list. Returns any violations found."""
    lower = text.lower()
    return [term for term in FORBIDDEN_TERMS if term in lower]
