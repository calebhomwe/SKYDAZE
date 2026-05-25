"""Generate the 1000-design FTC Collection V1.

Produces:
  artifacts/collection_v1/
    catalog.html               <-- open this in a browser
    svg/<id>.svg               <-- per-design standalone print artwork
    eps/<id>.eps               <-- per-design EPS companion
    mockups/<id>.svg           <-- flat apparel/accessory preview
    designs.json               <-- full catalog data (all 1000)
    concepts/<id>.json         <-- Section-4 concept payload per design
    pricing.csv                <-- MSRP / COGS / margin per design
    summary.json               <-- collection-level stats

Run:
    python generate_collection.py
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from ftc.catalog import write_catalog
from ftc.config import ARTIFACTS
from ftc.design_engine import SECTION_PLAN, generate_collection
from ftc.print_assets import mockup_qa_score, render_print_eps, render_print_svg, typography_qa_score
from ftc.svg_mockups import render_design_svg

console = Console()
OUT = ARTIFACTS / "collection_v1"


def _stash_palette_obj_on_dict(d):
    """When writing JSON we drop the Palette object; for SVG we keep it."""
    out = d.as_concept_json()
    return out


def main() -> int:
    console.rule("[bold]FTC Collection V1 — 1000 designs[/bold]")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "svg").mkdir(parents=True, exist_ok=True)
    (OUT / "eps").mkdir(parents=True, exist_ok=True)
    (OUT / "mockups").mkdir(parents=True, exist_ok=True)
    (OUT / "concepts").mkdir(parents=True, exist_ok=True)

    designs = generate_collection()
    console.print(f"[green]Generated[/green] {len(designs)} designs")

    catalog_rows = []
    pricing_rows = []
    section_counts: Counter = Counter()
    family_counts: Counter = Counter()
    technique_counts: Counter = Counter()

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), TextColumn("{task.completed}/{task.total}")) as p:
        task = p.add_task("rendering print assets + writing concepts", total=len(designs))
        for d in designs:
            svg_dict = d.as_catalog_row() | {
                "_palette_obj": d.palette,
                "section": d.section,
                "silhouette": d.silhouette,
                "title": d.title,
                "print_technique": d.print_technique,
                "print_placement": d.print_placement,
                "id": d.id,
            }
            print_svg = render_print_svg(d)
            print_eps = render_print_eps(d)
            mockup_svg = render_design_svg(svg_dict)
            (OUT / "svg" / f"{d.id}.svg").write_text(print_svg, encoding="utf-8")
            (OUT / "eps" / f"{d.id}.eps").write_text(print_eps, encoding="utf-8")
            (OUT / "mockups" / f"{d.id}.svg").write_text(mockup_svg, encoding="utf-8")

            concept_path = OUT / "concepts" / f"{d.id}.json"
            concept_path.write_text(json.dumps(_stash_palette_obj_on_dict(d), indent=2))

            row = d.as_catalog_row()
            row["svg_path"] = f"svg/{d.id}.svg"
            row["eps_path"] = f"eps/{d.id}.eps"
            row["mockup_path"] = f"mockups/{d.id}.svg"
            row["canvas_px"] = 2048
            row["asset_type"] = "standalone_vector_graphic"
            row["usable_surfaces"] = ["tee", "hat", "hoodie", "tote", "label"]
            row["typography_qa_score"] = typography_qa_score(d.title, d.typography_layout)
            row["mockup_qa_score"] = mockup_qa_score(d.print_technique, d.palette)
            catalog_rows.append(row)

            pricing_rows.append({
                "id": d.id,
                "section": d.section,
                "silhouette": d.silhouette,
                "title": d.title,
                "msrp_usd": d.msrp_usd,
                "estimated_cogs_usd": d.estimated_cogs_usd,
                "margin_usd": d.msrp_usd - d.estimated_cogs_usd,
                "margin_pct": round(d.margin_pct, 1),
            })

            section_counts[d.section] += 1
            family_counts[d.palette.family] += 1
            technique_counts[d.print_technique] += 1
            p.update(task, advance=1)

    (OUT / "designs.json").write_text(json.dumps(catalog_rows, indent=2))

    with (OUT / "pricing.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(pricing_rows[0].keys()))
        writer.writeheader()
        writer.writerows(pricing_rows)

    catalog_path = write_catalog(designs, OUT)

    section_revenue = {
        s: sum(r["msrp_usd"] for r in pricing_rows if r["section"] == s)
        for s in SECTION_PLAN
    }
    section_cogs = {
        s: sum(r["estimated_cogs_usd"] for r in pricing_rows if r["section"] == s)
        for s in SECTION_PLAN
    }

    summary = {
        "total_designs": len(designs),
        "by_section": dict(section_counts),
        "by_palette_family": dict(family_counts),
        "by_technique": dict(technique_counts),
        "pricing_if_one_of_each_sold": {
            "total_revenue_usd": sum(r["msrp_usd"] for r in pricing_rows),
            "total_cogs_usd": sum(r["estimated_cogs_usd"] for r in pricing_rows),
            "total_margin_usd": sum(r["msrp_usd"] - r["estimated_cogs_usd"] for r in pricing_rows),
            "avg_margin_pct": round(sum(r["margin_pct"] for r in pricing_rows) / len(pricing_rows), 1),
            "by_section": {
                s: {
                    "revenue_usd": section_revenue[s],
                    "cogs_usd": section_cogs[s],
                    "margin_usd": section_revenue[s] - section_cogs[s],
                }
                for s in SECTION_PLAN
            },
        },
        "asset_exports": {
            "print_svg": len(list((OUT / "svg").glob("*.svg"))),
            "eps": len(list((OUT / "eps").glob("*.eps"))),
            "mockup_svg": len(list((OUT / "mockups").glob("*.svg"))),
            "canvas_px": 2048,
            "background": "transparent",
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))

    console.rule("[bold green]Collection V1 — complete[/bold green]")
    console.print(f"\nCatalog: [bold]{catalog_path}[/bold]")
    console.print(f"SVGs:    {OUT / 'svg'}  ({len(designs)} print artwork files)")
    console.print(f"EPS:     {OUT / 'eps'}  ({len(designs)} files)")
    console.print(f"Mockups: {OUT / 'mockups'}")
    console.print(f"Concepts:{OUT / 'concepts'}")
    console.print(f"Pricing: {OUT / 'pricing.csv'}")
    console.print(f"Summary: {OUT / 'summary.json'}")
    console.print(
        f"\nIf one of each sold at MSRP: "
        f"[bold]${summary['pricing_if_one_of_each_sold']['total_revenue_usd']:,} revenue[/bold] · "
        f"${summary['pricing_if_one_of_each_sold']['total_margin_usd']:,} margin "
        f"(avg {summary['pricing_if_one_of_each_sold']['avg_margin_pct']}% gross)"
    )
    console.print("\nNext: open the catalog in a browser. To render photoreal:")
    console.print("  cp .env.example .env  &&  fill FAL_KEY  &&  python workers/render_worker.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
