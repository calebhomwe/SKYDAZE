"""Environment + path config. All secrets via os.getenv per Section 6."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER_CONTEXT = REPO_ROOT / "FTC_MASTER_CONTEXT.md"
REGISTRY = REPO_ROOT / "agents" / "REGISTRY.yaml"
TARGETS = REPO_ROOT / "scrape_targets.yaml"
ARTIFACTS = REPO_ROOT / "artifacts"

RUN_MODE = os.getenv("FTC_RUN_MODE", "dry-run").lower()
DAILY_BUDGET_USD = float(os.getenv("FTC_DAILY_BUDGET_USD", "50"))

# DeepSeek Flash v4 via OpenRouter. Override with DEEPSEEK_MODEL env var if
# OpenRouter updates the slug. Current cheapest fast model for concept generation.
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek/deepseek-chat")
DEEPSEEK_FLASH_MODEL = os.getenv("DEEPSEEK_FLASH_MODEL", "deepseek/deepseek-chat")


@dataclass(frozen=True)
class Keys:
    openrouter: str | None = os.getenv("OPENROUTER_API_KEY")
    fal: str | None = os.getenv("FAL_KEY")
    novita: str | None = os.getenv("NOVITA_API_KEY")
    nano_banana: str | None = os.getenv("NANO_BANANA_API_KEY")
    firecrawl: str | None = os.getenv("FIRECRAWL_API_KEY")
    anthropic: str | None = os.getenv("ANTHROPIC_API_KEY")
    shopify_domain: str | None = os.getenv("SHOPIFY_STORE_DOMAIN")
    shopify_token: str | None = os.getenv("SHOPIFY_ADMIN_TOKEN")
    youtube_api: str | None = os.getenv("YOUTUBE_API_KEY")


KEYS = Keys()


def require(key_name: str) -> str:
    """Read a key by attribute name; raise if absent (unless dry-run/mock)."""
    value = getattr(KEYS, key_name)
    if value:
        return value
    if RUN_MODE in {"dry-run", "mock"}:
        return f"<missing:{key_name}>"
    raise RuntimeError(
        f"Required key {key_name!r} is not set. "
        "Add it to .env (copy from .env.example) or set FTC_RUN_MODE=dry-run."
    )


def artifact_path(*parts: str) -> Path:
    path = ARTIFACTS.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
