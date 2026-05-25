"""Bundle artifacts/collection_v1/{catalog.html + svg/*} into a single
self-contained HTML file with every SVG inlined as a data URI.

Result: one .html you can email, drop into Slack, or open offline.

Run:
    python package_catalog.py [--limit 1000]
"""
from __future__ import annotations

import argparse
import base64
import re
from pathlib import Path

from ftc.config import ARTIFACTS

ROOT = ARTIFACTS / "collection_v1"
CATALOG = ROOT / "catalog.html"
SVG_DIR = ROOT / "svg"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None,
                        help="Inline only the first N cards (others removed). "
                             "Default: all 1000.")
    parser.add_argument("--out", type=str, default=str(ROOT / "catalog_standalone.html"))
    args = parser.parse_args()

    html = CATALOG.read_text()

    if args.limit:
        # Keep only the first N cards by chopping the .card divs after limit.
        cards = re.findall(r'(<div class="card"[\s\S]*?</div>\s*</div>)', html)
        if len(cards) > args.limit:
            keep = cards[:args.limit]
            grid_re = re.search(r'(<div class="grid">)([\s\S]*?)(</div>\s*<div id="modal")', html)
            if grid_re:
                new_grid_inner = "\n".join(keep)
                html = html[:grid_re.start(2)] + new_grid_inner + html[grid_re.end(2):]

    # Replace <img src="svg/FTC-XX-NNNN.svg"...> with inlined SVG.
    def inline(match: re.Match) -> str:
        rel = match.group(1)
        path = ROOT / rel
        if not path.exists():
            return match.group(0)
        svg_bytes = path.read_bytes()
        b64 = base64.b64encode(svg_bytes).decode("ascii")
        return f'<img loading="lazy" src="data:image/svg+xml;base64,{b64}" alt=""/>'

    html = re.sub(r'<img loading="lazy" src="(svg/[^"]+\.svg)" alt="[^"]*"\s*/>', inline, html)

    # Same for modal data — rewrite svg_path entries to data URIs.
    def inline_data(match: re.Match) -> str:
        rel = match.group(1)
        path = ROOT / rel
        if not path.exists():
            return match.group(0)
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'"svg_path":"data:image/svg+xml;base64,{b64}"'

    html = re.sub(r'"svg_path":"(svg/[^"]+\.svg)"', inline_data, html)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    size_kb = out.stat().st_size / 1024
    print(f"wrote {out}  ({size_kb:,.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
