"""SVG silhouette templates for FTC sections.

Each silhouette is a clean, flat luxury e-commerce style mockup (think
Lemaire or SSENSE product flat). Two layers per garment: body fill + accent
fill. Print/embroidery placement is rendered as a tiny indicator badge.
"""

from __future__ import annotations

VIEWBOX = "0 0 600 750"

# All paths are crafted as flat e-comm silhouettes. They are simple on
# purpose — luxury reads as restraint.

TRACKSUIT_TOP = """
<g id="tracksuit-top">
  <path d="M 130 130 L 470 130 L 510 200 L 470 240 L 470 600 L 130 600 L 130 240 L 90 200 Z" fill="{body}"/>
  <rect x="130" y="240" width="340" height="14" fill="{accent}" opacity="0.85"/>
  <rect x="468" y="130" width="6" height="470" fill="{accent}" opacity="0.5"/>
  <rect x="126" y="130" width="6" height="470" fill="{accent}" opacity="0.5"/>
  <circle cx="300" cy="180" r="20" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.85"/>
</g>
"""

TRACKSUIT_BOTTOM = """
<g id="tracksuit-bottom">
  <path d="M 175 80 L 425 80 L 460 200 L 430 700 L 330 700 L 305 220 L 295 220 L 270 700 L 170 700 L 140 200 Z" fill="{body}"/>
  <rect x="200" y="80" width="6" height="620" fill="{accent}" opacity="0.7"/>
  <rect x="394" y="80" width="6" height="620" fill="{accent}" opacity="0.7"/>
</g>
"""

TEE = """
<g id="tee">
  <path d="M 110 160 L 230 110 L 370 110 L 490 160 L 470 260 L 410 230 L 410 620 L 190 620 L 190 230 L 130 260 Z" fill="{body}"/>
  <ellipse cx="300" cy="130" rx="55" ry="20" fill="{accent}" opacity="0.6"/>
  <rect x="270" y="290" width="60" height="60" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.9"/>
</g>
"""

HOODIE = """
<g id="hoodie">
  <path d="M 200 90 Q 300 50 400 90 L 450 170 L 530 180 L 510 290 L 440 260 L 440 660 L 160 660 L 160 260 L 90 290 L 70 180 L 150 170 Z" fill="{body}"/>
  <path d="M 220 90 Q 300 60 380 90 L 380 200 Q 300 240 220 200 Z" fill="{accent}" opacity="0.45"/>
  <rect x="230" y="380" width="140" height="100" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.8"/>
  <line x1="260" y1="100" x2="260" y2="200" stroke="{accent}" stroke-width="1" opacity="0.6"/>
  <line x1="340" y1="100" x2="340" y2="200" stroke="{accent}" stroke-width="1" opacity="0.6"/>
</g>
"""

JACKET = """
<g id="jacket">
  <path d="M 120 140 L 230 110 L 300 130 L 370 110 L 480 140 L 510 250 L 470 230 L 470 660 L 130 660 L 130 230 L 90 250 Z" fill="{body}"/>
  <path d="M 230 110 L 300 200 L 230 280 Z" fill="{accent}" opacity="0.55"/>
  <path d="M 370 110 L 300 200 L 370 280 Z" fill="{accent}" opacity="0.55"/>
  <line x1="300" y1="200" x2="300" y2="660" stroke="{accent}" stroke-width="1.5" opacity="0.8"/>
  <circle cx="300" cy="260" r="3" fill="{accent}"/>
  <circle cx="300" cy="340" r="3" fill="{accent}"/>
  <circle cx="300" cy="420" r="3" fill="{accent}"/>
  <circle cx="300" cy="500" r="3" fill="{accent}"/>
</g>
"""

PANTS = """
<g id="pants">
  <path d="M 175 80 L 425 80 L 450 200 L 415 700 L 320 700 L 305 230 L 295 230 L 280 700 L 185 700 L 150 200 Z" fill="{body}"/>
  <path d="M 175 80 L 425 80 L 410 105 L 190 105 Z" fill="{accent}" opacity="0.5"/>
</g>
"""

SHORTS = """
<g id="shorts">
  <path d="M 160 120 L 440 120 L 460 200 L 420 400 L 320 400 L 305 240 L 295 240 L 280 400 L 180 400 L 140 200 Z" fill="{body}"/>
  <rect x="160" y="120" width="280" height="20" fill="{accent}" opacity="0.5"/>
</g>
"""

CAP = """
<g id="cap">
  <path d="M 160 360 Q 300 200 440 360 L 440 420 L 160 420 Z" fill="{body}"/>
  <path d="M 100 420 L 500 420 L 500 460 L 100 460 Z" fill="{body}"/>
  <ellipse cx="300" cy="360" rx="40" ry="22" fill="{accent}" opacity="0.85"/>
</g>
"""

BEANIE = """
<g id="beanie">
  <path d="M 180 380 Q 300 200 420 380 L 420 460 L 180 460 Z" fill="{body}"/>
  <rect x="180" y="430" width="240" height="40" fill="{accent}" opacity="0.6"/>
</g>
"""

BAG = """
<g id="bag">
  <rect x="180" y="280" width="240" height="280" rx="8" fill="{body}"/>
  <path d="M 220 280 Q 220 200 300 200 Q 380 200 380 280" fill="none" stroke="{body}" stroke-width="14"/>
  <rect x="240" y="380" width="120" height="80" fill="none" stroke="{accent}" stroke-width="2" opacity="0.85"/>
</g>
"""

SCARF = """
<g id="scarf">
  <rect x="220" y="120" width="160" height="540" fill="{body}"/>
  <rect x="220" y="120" width="160" height="30" fill="{accent}" opacity="0.6"/>
  <rect x="220" y="630" width="160" height="30" fill="{accent}" opacity="0.6"/>
</g>
"""


SECTION_SILHOUETTES: dict[str, list[tuple[str, str]]] = {
    "tracksuit": [
        ("tracksuit-top", TRACKSUIT_TOP),
        ("tracksuit-bottom", TRACKSUIT_BOTTOM),
        ("hoodie", HOODIE),
        ("pants", PANTS),
        ("shorts", SHORTS),
    ],
    "outerwear": [
        ("jacket", JACKET),
        ("hoodie", HOODIE),
        ("tracksuit-top", TRACKSUIT_TOP),
    ],
    "tee": [
        ("tee", TEE),
        ("hoodie", HOODIE),
        ("tracksuit-top", TRACKSUIT_TOP),
    ],
    "accessory": [
        ("cap", CAP),
        ("beanie", BEANIE),
        ("bag", BAG),
        ("scarf", SCARF),
    ],
}
