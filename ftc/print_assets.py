"""High-definition print asset exporter (design-only, transparent background).

This module converts generated FTC graphics into production-friendly asset packs:
  - SVG (vector source)
  - PNG (transparent raster export)
  - EPS (PostScript-compatible export for print workflows)
"""

from __future__ import annotations

import json
import os
import re
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import cairosvg

from .config import artifact_path
from .graphic_designer import GraphicDesign, generate_collection_svgs

CANVAS_EXPORT_PX = 4096


@dataclass(frozen=True)
class ExportResult:
    id: str
    section: str
    layout: str
    palette: str
    symbol: str
    treatment: str
    title: str
    svg_file: str
    png_file: str
    eps_file: str


def _transparentize_svg(svg_text: str) -> str:
    """Remove base background rectangle and keep design layers only."""
    cleaned = re.sub(
        r'\s*<rect width="2400" height="2400" fill="#[0-9A-Fa-f]{6}"\/>\n',
        "\n",
        svg_text,
        count=1,
    )
    cleaned = cleaned.replace('width="2400"', f'width="{CANVAS_EXPORT_PX}"', 1)
    cleaned = cleaned.replace('height="2400"', f'height="{CANVAS_EXPORT_PX}"', 1)
    return cleaned


def _remove_text_layers(svg_text: str) -> str:
    """Optionally remove all text tags for purely symbolic assets."""
    return re.sub(r"<text\b[^>]*>.*?</text>\n?", "", svg_text, flags=re.DOTALL)


def _render_raster_and_eps(svg_path: str, png_path: str, eps_path: str, canvas_px: int) -> None:
    """Worker task for CPU-heavy raster/vector conversion."""
    svg_text = Path(svg_path).read_text()
    cairosvg.svg2png(
        bytestring=svg_text.encode(),
        write_to=png_path,
        output_width=canvas_px,
        output_height=canvas_px,
    )
    cairosvg.svg2ps(bytestring=svg_text.encode(), write_to=eps_path)


def export_print_pack(
    n: int = 1000,
    seed: str = "FTC-PRINT-PACK-V2",
    sections: list[str] | None = None,
    include_text: bool = True,
    clean_output: bool = True,
) -> dict:
    """Generate and export a full print pack in SVG + PNG + EPS."""
    if sections is None:
        sections = ["tee", "hat", "hoodie", "all-over"]

    root = artifact_path("print_pack")
    svg_dir = root / "svg"
    png_dir = root / "png"
    eps_dir = root / "eps"

    if clean_output and root.exists():
        for child in root.iterdir():
            if child.is_dir():
                for item in child.glob("*"):
                    item.unlink()
            else:
                child.unlink()

    svg_dir.mkdir(parents=True, exist_ok=True)
    png_dir.mkdir(parents=True, exist_ok=True)
    eps_dir.mkdir(parents=True, exist_ok=True)

    designs: list[GraphicDesign] = generate_collection_svgs(n=n, seed=seed, sections=sections)
    exports: list[ExportResult] = []
    conversion_jobs: list[tuple[str, str, str, int]] = []

    for design in designs:
        svg_name = design.svg_filename()
        png_name = svg_name.replace(".svg", ".png")
        eps_name = svg_name.replace(".svg", ".eps")

        svg_text = _transparentize_svg(design.svg)
        if not include_text:
            svg_text = _remove_text_layers(svg_text)

        svg_path = svg_dir / svg_name
        png_path = png_dir / png_name
        eps_path = eps_dir / eps_name

        svg_path.write_text(svg_text)
        conversion_jobs.append((str(svg_path), str(png_path), str(eps_path), CANVAS_EXPORT_PX))

        exports.append(
            ExportResult(
                id=design.id,
                section=design.section,
                layout=design.layout,
                palette=design.palette_name,
                symbol=design.symbol_name,
                treatment=design.treatment,
                title=design.title,
                svg_file=svg_name,
                png_file=png_name,
                eps_file=eps_name,
            )
        )

    # Render PNG/EPS in parallel to keep the 1000-pack generation fast.
    max_workers = max(1, min(8, (os.cpu_count() or 4)))
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_render_raster_and_eps, *job) for job in conversion_jobs]
        for future in futures:
            future.result()

    manifest = {
        "count": len(exports),
        "seed": seed,
        "include_text": include_text,
        "canvas_px": CANVAS_EXPORT_PX,
        "formats": ["svg", "png", "eps"],
        "sections": sections,
        "items": [e.__dict__ for e in exports],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    return {
        "root": str(root),
        "svg_dir": str(svg_dir),
        "png_dir": str(png_dir),
        "eps_dir": str(eps_dir),
        "manifest": str(manifest_path),
        "count": len(exports),
    }
