#!/usr/bin/env python3
"""FTC FULL TIME CHRISTIAN — Full Design Pipeline.

Usage:
    python3 pipeline.py                          # dry-run, no API calls
    FTC_RUN_MODE=real python3 pipeline.py        # real mode: scrapes + LLM
    FTC_RUN_MODE=real python3 pipeline.py --n 50 # generate only 50 designs

Outputs:
    artifacts/designs/svg/         (1000 individual print-ready SVGs)
    artifacts/designs/catalog.json (full catalog with all metadata)
    artifacts/designs/index.html   (visual gallery preview)
    artifacts/research/            (trend synthesis + scrape raw data)

Pipeline stages:
    1. Trend Research  — scrape Pinterest/Reddit/YouTube references
    2. Design Engine   — generate 1000 Design concept objects
    3. SVG Renderer    — render each concept as a 2400×2400 SVG
    4. Catalog Export  — write JSON catalog + HTML gallery
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from ftc.config import RUN_MODE, artifact_path
from ftc.graphic_designer import GraphicDesign, generate_collection_svgs
from ftc.trend_researcher import research_trends

console = Console()

# ---------------------------------------------------------------------------
# HTML gallery
# ---------------------------------------------------------------------------

GALLERY_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>FTC FULL TIME CHRISTIAN — 1000 Graphic Designs</title>
<style>
  :root {{
    --bg: #111;
    --fg: #f0ebe1;
    --accent: #8a7a60;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--fg); font-family: 'Arial', sans-serif; }}
  header {{
    padding: 40px 60px 20px;
    border-bottom: 1px solid #333;
  }}
  header h1 {{
    font-size: 2.4rem;
    font-weight: 900;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }}
  header p {{
    font-size: 0.85rem;
    color: var(--accent);
    letter-spacing: 0.2em;
    margin-top: 8px;
  }}
  .filters {{
    padding: 20px 60px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }}
  .filter-btn {{
    background: transparent;
    border: 1px solid #444;
    color: var(--fg);
    padding: 6px 16px;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .filter-btn:hover, .filter-btn.active {{
    background: var(--fg);
    color: var(--bg);
  }}
  .stats {{
    padding: 0 60px 20px;
    font-size: 0.8rem;
    color: var(--accent);
    letter-spacing: 0.1em;
  }}
  .gallery {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 2px;
    padding: 2px;
  }}
  .card {{
    position: relative;
    aspect-ratio: 1;
    overflow: hidden;
    cursor: pointer;
    background: #1a1a1a;
  }}
  .card img {{
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: transform 0.3s ease;
  }}
  .card:hover img {{ transform: scale(1.04); }}
  .card .overlay {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0,0,0,0.85));
    padding: 30px 12px 10px;
    transform: translateY(100%);
    transition: transform 0.25s ease;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
  }}
  .card:hover .overlay {{ transform: translateY(0); }}
  .card .overlay .id {{ color: var(--accent); }}
  .card .overlay .title {{ font-weight: 700; margin: 3px 0; text-transform: uppercase; }}
  .card .overlay .meta {{ color: #aaa; font-size: 0.65rem; }}
  .download-btn {{
    display: inline-block;
    margin-top: 6px;
    padding: 4px 10px;
    border: 1px solid var(--accent);
    color: var(--accent);
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-decoration: none;
    text-transform: uppercase;
  }}
  .download-btn:hover {{ background: var(--accent); color: var(--bg); }}
  footer {{
    padding: 40px 60px;
    border-top: 1px solid #333;
    font-size: 0.75rem;
    color: #555;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }}
  @media (max-width: 600px) {{
    header {{ padding: 20px; }}
    .gallery {{ grid-template-columns: repeat(2, 1fr); }}
  }}
</style>
</head>
<body>
<header>
  <h1>FTC Full Time Christian</h1>
  <p>1000 Print-Ready Graphic Designs · 2400×2400px SVG</p>
</header>
<div class="filters">
  <button class="filter-btn active" onclick="filterDesigns('all')">All ({total})</button>
  <button class="filter-btn" onclick="filterDesigns('tee')">Tee ({tee_count})</button>
  <button class="filter-btn" onclick="filterDesigns('hat')">Hat ({hat_count})</button>
  <button class="filter-btn" onclick="filterDesigns('hoodie')">Hoodie ({hoodie_count})</button>
  <button class="filter-btn" onclick="filterDesigns('all-over')">All-Over ({allover_count})</button>
</div>
<div class="stats">{total} designs · {layout_count} layouts · {palette_count} palettes · {symbol_count} symbols</div>
<div class="gallery" id="gallery">
{cards}
</div>
<footer>FTC FULL TIME CHRISTIAN · Brand: Luxury Christian Streetwear · Designs are print-ready SVG (2400×2400px)</footer>
<script>
function filterDesigns(section) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('.card').forEach(card => {{
    if (section === 'all' || card.dataset.section === section) {{
      card.style.display = '';
    }} else {{
      card.style.display = 'none';
    }}
  }});
}}
</script>
</body>
</html>"""


def _card_html(d: GraphicDesign) -> str:
    svg_path = f"svg/{d.svg_filename()}"
    return (
        f'<div class="card" data-section="{d.section}" data-layout="{d.layout}">\n'
        f'  <img src="{svg_path}" alt="{d.id}" loading="lazy"/>\n'
        f'  <div class="overlay">\n'
        f'    <div class="id">{d.id}</div>\n'
        f'    <div class="title">{d.title}</div>\n'
        f'    <div class="meta">{d.layout} · {d.palette_name} · {d.symbol_name}</div>\n'
        f'    <a class="download-btn" href="{svg_path}" download="{d.svg_filename()}">Download SVG</a>\n'
        f'  </div>\n'
        f'</div>'
    )


def _build_gallery(designs: list[GraphicDesign], out_dir: Path) -> None:
    sections = [d.section for d in designs]
    cards_html = "\n".join(_card_html(d) for d in designs)
    html = GALLERY_TEMPLATE.format(
        total=len(designs),
        tee_count=sections.count("tee"),
        hat_count=sections.count("hat"),
        hoodie_count=sections.count("hoodie"),
        allover_count=sections.count("all-over"),
        layout_count=len({d.layout for d in designs}),
        palette_count=len({d.palette_name for d in designs}),
        symbol_count=len({d.symbol_name for d in designs}),
        cards=cards_html,
    )
    gallery_path = out_dir / "index.html"
    gallery_path.write_text(html)
    console.print(f"  [green]Gallery written →[/green] {gallery_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="FTC Design Pipeline")
    parser.add_argument("--n", type=int, default=1000, help="Number of designs to generate (default: 1000)")
    parser.add_argument("--seed", default="FTC-GRAPHIC-COLLECTION-V1", help="Deterministic seed")
    parser.add_argument("--skip-research", action="store_true", help="Skip trend research phase")
    parser.add_argument("--sections", default="tee,hat,hoodie,all-over", help="Comma-separated section list")
    args = parser.parse_args()

    n = args.n
    sections = args.sections.split(",")

    console.rule(f"[bold]FTC FULL TIME CHRISTIAN — Design Pipeline  (mode={RUN_MODE})[/bold]")
    console.print(f"  Generating [bold]{n}[/bold] designs across sections: {sections}")
    console.print()

    # Stage 1: Trend Research
    if not args.skip_research:
        console.print("[bold cyan]Stage 1: Trend Research[/bold cyan]")
        t0 = time.time()
        trends = research_trends()
        console.print(f"  Done in {time.time()-t0:.1f}s  ·  {len(trends.get('trends', []))} trend clusters\n")
    else:
        console.print("[dim]Stage 1: Trend Research — skipped[/dim]\n")

    # Stage 2: Generate graphic designs
    console.print("[bold cyan]Stage 2: Generating Designs[/bold cyan]")
    t0 = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Rendering SVGs…", total=n)

        designs = generate_collection_svgs(n=n, seed=args.seed, sections=sections)
        progress.update(task, advance=n)

    console.print(f"  {len(designs)} designs generated in {time.time()-t0:.1f}s\n")

    # Stage 3: Write SVG files
    console.print("[bold cyan]Stage 3: Writing SVG Files[/bold cyan]")
    t0 = time.time()
    svg_dir = artifact_path("designs", "svg")
    svg_dir.mkdir(parents=True, exist_ok=True)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Writing SVGs…", total=len(designs))
        for d in designs:
            svg_path = svg_dir / d.svg_filename()
            svg_path.write_text(d.svg)
            progress.update(task, advance=1)

    total_size_mb = sum((svg_dir / d.svg_filename()).stat().st_size for d in designs) / 1_048_576
    console.print(f"  {len(designs)} SVG files → {svg_dir}")
    console.print(f"  Total size: {total_size_mb:.1f} MB in {time.time()-t0:.1f}s\n")

    # Stage 4: Catalog export
    console.print("[bold cyan]Stage 4: Catalog Export[/bold cyan]")
    designs_dir = artifact_path("designs")
    designs_dir.mkdir(parents=True, exist_ok=True)
    catalog = [
        {
            "id": d.id,
            "section": d.section,
            "layout": d.layout,
            "palette": d.palette_name,
            "font": d.font_name,
            "symbol": d.symbol_name,
            "treatment": d.treatment,
            "title": d.title,
            "svg_file": d.svg_filename(),
            "bg_color": d.bg_color,
            "fg_color": d.fg_color,
        }
        for d in designs
    ]
    catalog_path = designs_dir / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2))
    console.print(f"  Catalog → {catalog_path}")

    # Build HTML gallery
    _build_gallery(designs, designs_dir)

    # Summary table
    console.print()
    table = Table(title="Collection Summary", show_header=True)
    table.add_column("Section", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Layouts", justify="right")
    table.add_column("Palettes", justify="right")
    table.add_column("Symbols", justify="right")

    for section in sections:
        section_designs = [d for d in designs if d.section == section]
        table.add_row(
            section.upper(),
            str(len(section_designs)),
            str(len({d.layout for d in section_designs})),
            str(len({d.palette_name for d in section_designs})),
            str(len({d.symbol_name for d in section_designs})),
        )
    console.print(table)

    console.print()
    console.rule("[bold green]Pipeline Complete[/bold green]")
    console.print(f"  [bold]{len(designs)}[/bold] print-ready SVG designs generated")
    console.print(f"  SVGs: [cyan]{svg_dir}[/cyan]")
    console.print(f"  Gallery: [cyan]{designs_dir / 'index.html'}[/cyan]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
