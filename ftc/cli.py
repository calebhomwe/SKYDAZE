"""CLI entry point for the FTC design pipeline."""

import argparse
import json
import logging
import sys

from ftc import __version__
from ftc.config import load_config, validate_no_forbidden
from ftc.models import DesignConcept

logger = logging.getLogger("ftc")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ftc-pipeline",
        description="FTC FULL TIME CHRISTIAN — AI-powered luxury streetwear design pipeline",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show pipeline status and config health")
    validate_parser = sub.add_parser("validate", help="Validate a concept JSON file")
    validate_parser.add_argument("file", help="Path to concept JSON file")
    sub.add_parser("check-env", help="Verify environment variable configuration")

    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")

    if args.command == "status":
        return cmd_status()
    elif args.command == "validate":
        return cmd_validate(args.file)
    elif args.command == "check-env":
        return cmd_check_env()
    else:
        parser.print_help()
        return 0


def cmd_status() -> int:
    """Show pipeline status."""
    config = load_config()
    print(f"FTC Pipeline v{__version__}")
    print("─" * 40)
    print(f"  OpenRouter API key: {'✓ configured' if config.openrouter_api_key else '✗ missing'}")
    print(f"  Fal.ai API key:     {'✓ configured' if config.fal_ai_api_key else '✗ missing'}")
    print(f"  Firecrawl API key:  {'✓ configured' if config.firecrawl_api_key else '✗ missing'}")
    print(f"  Novita API key:     {'✓ configured' if config.novita_api_key else '✗ missing'}")
    print("─" * 40)
    print("Pipeline phases:")
    print("  Reference Scraping:  ⏳ Pending")
    print("  Test Batch (5):      ⏳ Pending")
    print("  Full Generation:     🔒 Locked")
    print("  Shopify Integration: 🔒 Locked")
    print("  Social Scheduler:    🔒 Locked")
    return 0


def cmd_validate(filepath: str) -> int:
    """Validate a concept JSON file against the schema."""
    try:
        with open(filepath) as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return 1

    items = raw if isinstance(raw, list) else [raw]
    errors = 0

    for i, item in enumerate(items):
        try:
            concept = DesignConcept.model_validate(item)
            violations = validate_no_forbidden(
                f"{concept.title} {concept.theological_core} {concept.aesthetic_direction}"
            )
            if violations:
                print(f"  [{concept.id}] FORBIDDEN terms: {violations}")
                errors += 1
            else:
                print(f'  [{concept.id}] ✓ valid — "{concept.title}"')
        except Exception as e:
            print(f"  [item {i}] ✗ invalid — {e}", file=sys.stderr)
            errors += 1

    return 1 if errors else 0


def cmd_check_env() -> int:
    """Verify environment configuration."""
    config = load_config()
    all_ok = True

    keys = {
        "OPENROUTER_API_KEY": config.openrouter_api_key,
        "FAL_AI_API_KEY": config.fal_ai_api_key,
        "FIRECRAWL_API_KEY": config.firecrawl_api_key,
        "NOVITA_API_KEY": config.novita_api_key,
    }

    for name, val in keys.items():
        status = "✓ set" if val else "✗ NOT SET"
        if not val:
            all_ok = False
        print(f"  {name}: {status}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
