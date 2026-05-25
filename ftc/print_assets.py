"""Standalone print artwork for FTC collection assets.

These SVG/EPS files are the production assets. They are simple, scalable,
and intentionally garment-agnostic so the same mark can move across a tee,
cap, hoodie, tote, or label without re-drawing.
"""

from __future__ import annotations

import hashlib
import html
from collections.abc import Callable

from .colors import Palette

CANVAS = 2048


def _hash_int(seed: str) -> int:
    return int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8], "big")


def _ink(palette: Palette) -> str:
    return palette.hexes[1] if len(palette.hexes) > 1 else "#11100E"


def _accent(palette: Palette) -> str:
    return palette.hexes[2] if len(palette.hexes) > 2 else _ink(palette)


def _safe_text(value: str) -> str:
    return html.escape(value.upper(), quote=True)


def typography_qa_score(title: str, typography_layout: str) -> float:
    """Small deterministic typography gate used before export.

    It is intentionally conservative: short text, no novelty fonts, clear
    hierarchy, and restrained treatments score well. The generator only emits
    assets that meet the mock QA floor used by the catalog.
    """
    lower = typography_layout.lower()
    score = 9.4
    if len(title) > 22:
        score -= 0.4
    if "no typography" in lower or "geometric mark" in lower:
        score += 0.3
    if "grotesque" in lower or "serif" in lower or "mono" in lower:
        score += 0.2
    if "comic" in lower or "brush" in lower or "impact" in lower:
        score -= 2.0
    return round(max(8.0, min(10.0, score)), 1)


def mockup_qa_score(print_technique: str, palette: Palette) -> float:
    """Score portability and production readiness for the flat mockup."""
    score = 8.8
    if print_technique in {"Tonal embroidery", "Deboss", "Screen", "Puff"}:
        score += 0.4
    if palette.contrast_score >= 0.55:
        score += 0.3
    return round(min(10.0, score), 1)


def _metadata(fid: str, title: str) -> str:
    return (
        f"<metadata>FTC FULL TIME CHRISTIAN {html.escape(fid)} "
        f"{html.escape(title)} print-ready vector asset</metadata>"
    )


def _texture_defs() -> str:
    return """
  <defs>
    <filter id="rough-edge" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="3" seed="19" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="9"/>
    </filter>
    <pattern id="scanlines" width="12" height="12" patternUnits="userSpaceOnUse">
      <rect width="12" height="2" fill="#C5FF00" opacity="0.22"/>
    </pattern>
    <pattern id="halftone" width="32" height="32" patternUnits="userSpaceOnUse">
      <circle cx="8" cy="8" r="3" fill="#0E0D0C" opacity="0.28"/>
      <circle cx="24" cy="24" r="2" fill="#0E0D0C" opacity="0.18"/>
    </pattern>
  </defs>"""


def _seal(fid: str, title: str, palette: Palette) -> str:
    fg = _ink(palette)
    ac = _accent(palette)
    return f"""
  <circle cx="1024" cy="1024" r="560" fill="none" stroke="{fg}" stroke-width="34"/>
  <circle cx="1024" cy="1024" r="420" fill="none" stroke="{ac}" stroke-width="10" opacity="0.82"/>
  <path d="M724 1052 H1324" stroke="{fg}" stroke-width="52" stroke-linecap="square"/>
  <path d="M844 898 H1204 M844 1166 H1204" stroke="{fg}" stroke-width="18" stroke-linecap="square"/>
  <text x="1024" y="770" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="92" font-weight="700" letter-spacing="18" fill="{fg}">{_safe_text(title)}</text>
  <text x="1024" y="1392" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="48" letter-spacing="14" fill="{fg}">{fid}</text>"""


def _word_stack(fid: str, title: str, palette: Palette) -> str:
    fg = _ink(palette)
    ac = _accent(palette)
    return f"""
  <text x="1024" y="810" text-anchor="middle" font-family="Arial Black, Arial, Helvetica, sans-serif" font-size="188" font-weight="900" letter-spacing="10" fill="none" stroke="{fg}" stroke-width="14">{_safe_text(title)}</text>
  <text x="1024" y="1012" text-anchor="middle" font-family="Arial Black, Arial, Helvetica, sans-serif" font-size="188" font-weight="900" letter-spacing="10" fill="{fg}" opacity="0.95">{_safe_text(title)}</text>
  <rect x="612" y="1128" width="824" height="38" fill="{ac}" opacity="0.9"/>
  <text x="1024" y="1268" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="58" letter-spacing="20" fill="{fg}">FULL TIME CHRISTIAN</text>
  <text x="1024" y="1360" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="38" letter-spacing="12" fill="{fg}" opacity="0.72">{fid}</text>"""


def _cornerstone(fid: str, title: str, palette: Palette) -> str:
    fg = _ink(palette)
    ac = _accent(palette)
    return f"""
  <rect x="610" y="694" width="360" height="360" fill="none" stroke="{fg}" stroke-width="34"/>
  <rect x="1012" y="694" width="426" height="360" fill="{fg}" opacity="0.94"/>
  <rect x="610" y="1096" width="828" height="258" fill="none" stroke="{fg}" stroke-width="34"/>
  <path d="M748 1226 H1300" stroke="{ac}" stroke-width="30" stroke-linecap="square"/>
  <text x="1024" y="1516" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="74" font-weight="700" letter-spacing="14" fill="{fg}">{_safe_text(title)}</text>
  <text x="1024" y="1600" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="34" letter-spacing="10" fill="{fg}" opacity="0.72">{fid}</text>"""


def _ripple(fid: str, title: str, palette: Palette) -> str:
    fg = _ink(palette)
    ac = _accent(palette)
    rings = "\n".join(
        f'  <ellipse cx="1024" cy="990" rx="{220 + i * 130}" ry="{96 + i * 50}" '
        f'fill="none" stroke="{fg if i % 2 == 0 else ac}" stroke-width="{28 - i * 3}" opacity="{0.95 - i * 0.12}"/>'
        for i in range(5)
    )
    return f"""
{rings}
  <path d="M688 990 H1360" stroke="{fg}" stroke-width="18" opacity="0.82"/>
  <text x="1024" y="1328" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="104" font-weight="700" letter-spacing="16" fill="{fg}">{_safe_text(title)}</text>
  <text x="1024" y="1416" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="36" letter-spacing="12" fill="{fg}" opacity="0.72">{fid}</text>"""


def _arch(fid: str, title: str, palette: Palette) -> str:
    fg = _ink(palette)
    ac = _accent(palette)
    return f"""
  <path d="M644 1370 V934 C644 724 814 554 1024 554 C1234 554 1404 724 1404 934 V1370" fill="none" stroke="{fg}" stroke-width="42"/>
  <path d="M780 1370 V956 C780 820 888 710 1024 710 C1160 710 1268 820 1268 956 V1370" fill="none" stroke="{ac}" stroke-width="18" opacity="0.82"/>
  <path d="M560 1370 H1488" stroke="{fg}" stroke-width="42" stroke-linecap="square"/>
  <text x="1024" y="1546" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="88" font-weight="700" letter-spacing="16" fill="{fg}">{_safe_text(title)}</text>
  <text x="1024" y="1636" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="34" letter-spacing="10" fill="{fg}" opacity="0.72">{fid}</text>"""


def _ledger(fid: str, title: str, palette: Palette) -> str:
    fg = _ink(palette)
    ac = _accent(palette)
    lines = "\n".join(
        f'  <path d="M650 {760 + i * 128} H1398" stroke="{fg if i != 2 else ac}" stroke-width="{22 if i != 2 else 38}" opacity="{0.88 - i * 0.06}"/>'
        for i in range(6)
    )
    return f"""
  <rect x="570" y="610" width="908" height="812" fill="none" stroke="{fg}" stroke-width="28"/>
{lines}
  <text x="1024" y="1570" text-anchor="middle" font-family="Courier New, monospace" font-size="78" font-weight="700" letter-spacing="10" fill="{fg}">{_safe_text(title)}</text>
  <text x="1024" y="1652" text-anchor="middle" font-family="Courier New, monospace" font-size="34" letter-spacing="8" fill="{fg}" opacity="0.72">{fid}</text>"""


def _field_marker(fid: str, title: str, palette: Palette) -> str:
    fg = _ink(palette)
    ac = _accent(palette)
    return f"""
  <path d="M1024 488 L1378 1376 H670 Z" fill="none" stroke="{fg}" stroke-width="38" stroke-linejoin="miter"/>
  <path d="M1024 706 L1216 1244 H832 Z" fill="{fg}" opacity="0.94"/>
  <path d="M738 1376 H1310" stroke="{ac}" stroke-width="34"/>
  <text x="1024" y="1546" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="84" font-weight="700" letter-spacing="14" fill="{fg}">{_safe_text(title)}</text>
  <text x="1024" y="1632" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="34" letter-spacing="10" fill="{fg}" opacity="0.72">{fid}</text>"""


def _label(fid: str, title: str, palette: Palette) -> str:
    fg = _ink(palette)
    ac = _accent(palette)
    return f"""
  <rect x="510" y="704" width="1028" height="640" rx="18" fill="none" stroke="{fg}" stroke-width="30"/>
  <rect x="592" y="786" width="864" height="156" fill="{fg}" opacity="0.94"/>
  <text x="1024" y="894" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="72" font-weight="700" letter-spacing="16" fill="#F3F0EA">FTC</text>
  <text x="1024" y="1102" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="112" font-weight="800" letter-spacing="14" fill="{fg}">{_safe_text(title)}</text>
  <path d="M686 1218 H1362" stroke="{ac}" stroke-width="28"/>
  <text x="1024" y="1512" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="36" letter-spacing="10" fill="{fg}" opacity="0.72">{fid}</text>"""


def _glitch_cross(fid: str, title: str, palette: Palette) -> str:
    fg = _ink(palette)
    ac = "#C5FF00"
    red = "#FF003C"
    blue = "#00B7FF"
    return f"""
  <g transform="translate(112,-38) rotate(-4 1024 1024)">
    <rect x="812" y="326" width="354" height="1114" fill="{red}" opacity="0.55" transform="translate(-42,14)"/>
    <rect x="812" y="326" width="354" height="1114" fill="{blue}" opacity="0.52" transform="translate(46,-10)"/>
    <rect x="812" y="326" width="354" height="1114" fill="{fg}" filter="url(#rough-edge)"/>
    <rect x="548" y="762" width="884" height="290" fill="{red}" opacity="0.46" transform="translate(-34,-18)"/>
    <rect x="548" y="762" width="884" height="290" fill="{blue}" opacity="0.50" transform="translate(42,20)"/>
    <rect x="548" y="762" width="884" height="290" fill="{fg}" filter="url(#rough-edge)"/>
    <rect x="482" y="496" width="1080" height="900" fill="url(#scanlines)" opacity="0.35"/>
    <path d="M540 672 H840 M1132 552 H1498 M460 1138 H788 M1110 1284 H1516" stroke="{ac}" stroke-width="34" stroke-linecap="square"/>
  </g>
  <text x="1018" y="1608" text-anchor="middle" font-family="Courier New, monospace" font-size="58" font-weight="700" letter-spacing="5" fill="{ac}">ERROR 404: SIN NOT FOUND</text>
  <text x="1018" y="1690" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="32" letter-spacing="11" fill="{fg}" opacity="0.72">{fid} / {html.escape(title.upper())}</text>"""


def _torn_paper(fid: str, title: str, palette: Palette) -> str:
    fg = _ink(palette)
    paper = "#C8B692"
    shadow = "#34291F"
    tear = "#0B0B0B"
    return f"""
  <g transform="translate(-92,18) rotate(-3 1024 1024)">
    <path d="M282 438 L1688 356 L1770 1478 L402 1608 Z" fill="{paper}" filter="url(#rough-edge)"/>
    <path d="M430 520 L1640 440 L1686 1386 L510 1512 Z" fill="url(#halftone)" opacity="0.22"/>
    <path d="M548 686 L744 622 L902 702 L1072 626 L1236 720 L1428 660 L1510 812 L1402 956 L1518 1132 L1308 1204 L1164 1136 L1004 1228 L858 1128 L704 1206 L586 1040 L662 898 Z" fill="{shadow}" opacity="0.24" transform="translate(30,38)"/>
    <path d="M548 686 L744 622 L902 702 L1072 626 L1236 720 L1428 660 L1510 812 L1402 956 L1518 1132 L1308 1204 L1164 1136 L1004 1228 L858 1128 L704 1206 L586 1040 L662 898 Z" fill="{tear}" filter="url(#rough-edge)"/>
    <text x="1024" y="1022" text-anchor="middle" font-family="Arial Black, Arial, Helvetica, sans-serif" font-size="196" font-weight="900" letter-spacing="8" fill="#F1EEE5" transform="rotate(-5 1024 1022)">TRUTH</text>
    <path d="M474 628 L632 696 M1544 666 L1426 756 M546 1252 L694 1160 M1496 1202 L1340 1126" stroke="{fg}" stroke-width="18" opacity="0.5"/>
  </g>
  <text x="1024" y="1754" text-anchor="middle" font-family="Courier New, monospace" font-size="34" letter-spacing="8" fill="{fg}" opacity="0.72">{fid} / {html.escape(title.upper())}</text>"""


MOTIFS: tuple[Callable[[str, str, Palette], str], ...] = (
    _seal,
    _word_stack,
    _cornerstone,
    _ripple,
    _arch,
    _ledger,
    _field_marker,
    _label,
    _glitch_cross,
    _torn_paper,
)


def render_print_svg(design: object) -> str:
    """Return a transparent 2048x2048 print SVG for one design object."""
    fid = str(design.id)
    title = str(design.title)
    palette = design.palette
    motif = MOTIFS[_hash_int(fid) % len(MOTIFS)]
    body = motif(fid, title, palette)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS} {CANVAS}" width="{CANVAS}" height="{CANVAS}" role="img" aria-label="{html.escape(fid)} {html.escape(title)} print artwork">
  {_metadata(fid, title)}
  <title>{html.escape(fid)} {html.escape(title)}</title>
  <desc>Standalone vector graphic. Transparent background. No people or raster images.</desc>
{_texture_defs()}
{body}
</svg>
"""


def render_fire_prompt_svg(kind: str) -> str:
    """Render the two explicit fire prompt tests as raw square assets."""
    if kind == "glitch-cross":
        fid = "FTC-FIRE-001"
        title = "Glitch Cross"
        palette = Palette(
            name="glitch-black-green",
            family="fire-test",
            hexes=("#050505", "#070707", "#C5FF00"),
            weights=(0.70, 0.20, 0.10),
            contrast_score=0.92,
            rationale="Black cyberpunk base with neon error accent.",
        )
        background = '<rect width="2048" height="2048" fill="#050505"/>'
        body = _glitch_cross(fid, title, palette)
        desc = "Prompt test 1: glitch cross, RGB split distortion, neon green monospace error text."
    elif kind == "torn-paper":
        fid = "FTC-FIRE-002"
        title = "Torn Paper Revelation"
        palette = Palette(
            name="paper-black-charcoal",
            family="fire-test",
            hexes=("#FAF8F0", "#0B0B0B", "#C8B692"),
            weights=(0.62, 0.28, 0.10),
            contrast_score=0.9,
            rationale="White isolation, beige paper, black reveal layer.",
        )
        background = '<rect width="2048" height="2048" fill="#FAF8F0"/>'
        body = _torn_paper(fid, title, palette)
        desc = "Prompt test 2: torn beige paper reveal with rough charcoal TRUTH lettering."
    else:
        raise ValueError(f"Unknown fire prompt asset: {kind}")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS} {CANVAS}" width="{CANVAS}" height="{CANVAS}" role="img" aria-label="{html.escape(title)}">
  {_metadata(fid, title)}
  <title>{html.escape(title)}</title>
  <desc>{desc}</desc>
{_texture_defs()}
{background}
{body}
</svg>
"""


def render_print_eps(design: object) -> str:
    """Return a compact EPS companion for print shops that prefer EPS."""
    fid = str(design.id)
    title = str(design.title).upper().replace("(", "").replace(")", "")
    palette = design.palette
    motif_index = _hash_int(fid) % len(MOTIFS)
    # EPS text stays editable. The SVG is the visual source of truth.
    fg = _ink(palette)
    r = int(fg[1:3], 16) / 255
    g = int(fg[3:5], 16) / 255
    b = int(fg[5:7], 16) / 255
    shape = {
        0: "306 306 718 0 360 arc stroke 306 306 540 0 360 arc stroke",
        1: "120 330 moveto 492 330 lineto 492 282 lineto 120 282 lineto closepath fill",
        2: "130 190 220 220 rectstroke 362 190 250 220 rectfill 130 440 482 160 rectstroke",
        3: "306 306 120 0 360 arc stroke 306 306 220 0 360 arc stroke",
        4: "120 520 moveto 120 280 200 150 306 150 curveto 412 150 492 280 492 520 curveto stroke",
        5: "120 180 372 330 rectstroke 160 240 moveto 452 240 lineto stroke 160 330 moveto 452 330 lineto stroke 160 420 moveto 452 420 lineto stroke",
        6: "306 120 moveto 500 520 lineto 112 520 lineto closepath stroke 306 235 moveto 390 460 lineto 222 460 lineto closepath fill",
        7: "96 190 420 300 rectstroke 140 240 332 70 rectfill",
        8: "270 92 92 428 rectfill 132 248 372 104 rectfill 90 210 moveto 210 210 lineto stroke 390 170 moveto 528 170 lineto stroke 70 420 moveto 190 420 lineto stroke",
        9: "84 116 moveto 548 92 lineto 528 528 lineto 112 548 lineto closepath stroke 160 210 moveto 240 190 lineto 310 220 lineto 380 194 lineto 470 230 lineto 438 330 lineto 484 420 lineto 376 460 lineto 306 430 lineto 230 470 lineto 168 402 lineto 198 310 lineto closepath fill",
    }[motif_index]
    return f"""%!PS-Adobe-3.0 EPSF-3.0
%%Title: {fid} {title}
%%Creator: FTC print asset generator
%%BoundingBox: 0 0 612 612
%%EndComments
/rectstroke {{ /h exch def /w exch def /y exch def /x exch def newpath x y moveto w 0 rlineto 0 h rlineto w neg 0 rlineto closepath stroke }} bind def
/rectfill {{ /h exch def /w exch def /y exch def /x exch def newpath x y moveto w 0 rlineto 0 h rlineto w neg 0 rlineto closepath fill }} bind def
{r:.4f} {g:.4f} {b:.4f} setrgbcolor
18 setlinewidth 1 setlinejoin 1 setlinecap
{shape}
/Helvetica-Bold findfont 44 scalefont setfont
306 560 moveto ({title[:18]}) dup stringwidth pop 2 div neg 0 rmoveto show
/Helvetica findfont 18 scalefont setfont
306 590 moveto ({fid}) dup stringwidth pop 2 div neg 0 rmoveto show
showpage
%%EOF
"""
