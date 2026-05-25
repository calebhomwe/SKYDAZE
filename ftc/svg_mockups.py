"""Compose flat SVG mockups from silhouette + palette + design metadata."""

from __future__ import annotations

from .colors import Palette, best_text_color
from .silhouettes import SECTION_SILHOUETTES, VIEWBOX


def _swatch_bar(palette: Palette, y: int = 700) -> str:
    """Bottom strip showing the palette + weights."""
    out: list[str] = []
    x = 30
    total_w = 540
    for hexc, weight in zip(palette.hexes, palette.weights, strict=False):
        w = max(20, int(total_w * weight))
        out.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="22" fill="{hexc}" stroke="#202020" stroke-width="0.5"/>'
        )
        x += w
    return "\n".join(out)


def _print_indicator(technique: str, placement: str, color: str) -> str:
    """A small badge that hints at the print/embroidery treatment."""
    glyph = {
        "Tonal embroidery": "•",
        "Puff": "▲",
        "Deboss": "▢",
        "Screen": "■",
        "Discharge": "◆",
        "Woven label": "◫",
    }.get(technique, "•")
    x_y = {
        "chest-center": (296, 290),
        "chest-left": (220, 290),
        "sleeve-left": (170, 380),
        "hem-back": (300, 600),
        "side-seam": (470, 480),
        "hood-interior": (300, 220),
        "pocket": (300, 430),
    }.get(placement, (296, 290))
    return (
        f'<text x="{x_y[0]}" y="{x_y[1]}" font-family="Inter,Helvetica" font-size="14" '
        f'fill="{color}" text-anchor="middle" opacity="0.9">{glyph}</text>'
    )


def render_design_svg(design: dict) -> str:
    """Return a self-contained SVG string for one design."""
    section = design["section"]
    silhouette_key = design["silhouette"]
    palette = design["_palette_obj"]  # Palette instance attached during generation
    technique = design["print_technique"]
    placement = design.get("print_placement", "chest-center")
    title = design["title"]
    fid = design["id"]
    palette_name = palette.name

    silhouettes = SECTION_SILHOUETTES[section]
    body_template = next((tpl for key, tpl in silhouettes if key == silhouette_key), silhouettes[0][1])

    body_color = palette.hexes[0]
    accent_color = palette.hexes[1] if len(palette.hexes) > 1 else palette.hexes[0]
    canvas_bg = "#F3F0EA"  # warm gallery off-white
    text_color = best_text_color(canvas_bg)

    body_svg = body_template.format(body=body_color, accent=accent_color)
    indicator = _print_indicator(technique, placement, accent_color)
    swatches = _swatch_bar(palette)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}" width="600" height="750" role="img" aria-label="{fid} {title}">
  <rect width="100%" height="100%" fill="{canvas_bg}"/>
  <text x="30" y="50" font-family="Inter,Helvetica" font-size="12" fill="{text_color}" letter-spacing="2">FTC FULL TIME CHRISTIAN</text>
  <text x="30" y="70" font-family="Inter,Helvetica" font-size="10" fill="{text_color}" opacity="0.6">{fid}  ·  {section.upper()}  ·  {palette_name}</text>
  <g transform="translate(0,30)">{body_svg}</g>
  {indicator}
  <text x="30" y="688" font-family="Inter,Helvetica" font-size="13" fill="{text_color}" letter-spacing="1">{title}</text>
  <text x="570" y="688" font-family="Inter,Helvetica" font-size="10" fill="{text_color}" opacity="0.6" text-anchor="end">{technique} · {placement}</text>
  {swatches}
</svg>"""
