"""Build a single self-contained HTML gallery showing every artifact.

Inlines all SVG content so the gallery works offline / shareable as one file.
"""

from __future__ import annotations

import base64  # noqa: F401  (used by kimi_card when PNG renders exist)
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRAPHICS_DIR = ROOT / "artifacts" / "graphics"
KIMI_DIR = ROOT / "artifacts" / "graphics-kimi"
OUT = ROOT / "artifacts" / "gallery.html"


def inline_svg(path: Path) -> str:
    return path.read_text()


def graphic_card(path: Path) -> str:
    title = path.stem.replace("ftc-graphic-", "").replace("-", " ").title()
    svg = inline_svg(path)
    return f"""
    <article class="card graphic">
      <div class="canvas">{svg}</div>
      <h3>{title}</h3>
      <p class="meta">FTC · Streetwear graphic</p>
    </article>
    """


def kimi_card(path: Path) -> str:
    # Format: ftc-kimi-NNN-K-XX-slug.png (or .svg if any)
    title = path.stem.replace("ftc-kimi-", "").replace("-", " ").title()
    if path.suffix == ".png":
        b64 = base64.b64encode(path.read_bytes()).decode()
        media = f'<img src="data:image/png;base64,{b64}" alt="{title}"/>'
    else:
        media = path.read_text()
    return f"""
    <article class="card kimi">
      <div class="canvas">{media}</div>
      <h3>{title}</h3>
      <p class="meta">Kimi · GLM · GPT Image 2 / Seedream</p>
    </article>
    """


def world_card(path: Path) -> str:
    name = path.stem.split("-", 1)[1].replace("-", " ").title()
    world_id = path.stem.split("-")[0]
    svg = inline_svg(path)
    return f"""
    <article class="card world">
      <div class="canvas wide">{svg}</div>
      <h3>{name}</h3>
      <p class="meta">GENESIS · {world_id}</p>
    </article>
    """


def main() -> None:
    graphics = sorted(GRAPHICS_DIR.glob("*.svg"))
    kimi_outputs = sorted(KIMI_DIR.glob("*.png")) + sorted(KIMI_DIR.glob("*.svg")) if KIMI_DIR.exists() else []

    parts = [
        """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FTC · Studio · 2026</title>
<style>
:root {
  --bg: #0E0D0C;
  --fg: #EFE9D8;
  --muted: #8C8782;
  --accent: #A88B6E;
}
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: 'Inter', 'Helvetica Neue', system-ui, sans-serif;
  font-weight: 300;
  line-height: 1.5;
}
header {
  padding: 80px 40px 40px;
  text-align: center;
  border-bottom: 1px solid #1F1C18;
}
header h1 {
  font-size: 32px;
  letter-spacing: 12px;
  margin: 0 0 8px;
  font-weight: 300;
}
header p {
  color: var(--muted);
  letter-spacing: 4px;
  margin: 0;
  font-size: 11px;
}
section {
  padding: 60px 40px;
  border-bottom: 1px solid #1F1C18;
}
section h2 {
  font-size: 22px;
  letter-spacing: 6px;
  margin: 0 0 8px;
  font-weight: 300;
  text-transform: uppercase;
}
section .lead {
  color: var(--muted);
  font-size: 13px;
  letter-spacing: 1px;
  margin: 0 0 40px;
  max-width: 640px;
}
.grid {
  display: grid;
  gap: 28px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}
.grid.worlds {
  grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
}
.card {
  background: #14110D;
  border: 1px solid #1F1C18;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 200ms ease, border-color 200ms ease;
}
.card:hover {
  transform: translateY(-2px);
  border-color: var(--accent);
}
.canvas {
  background: #0A0A09;
  aspect-ratio: 4 / 5;
  display: flex;
  align-items: center;
  justify-content: center;
}
.canvas.wide {
  aspect-ratio: 16 / 9;
}
.canvas svg {
  width: 100%;
  height: 100%;
}
.card h3 {
  margin: 14px 16px 4px;
  font-size: 14px;
  letter-spacing: 2px;
  font-weight: 400;
}
.card .meta {
  margin: 0 16px 16px;
  color: var(--muted);
  font-size: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
}
footer {
  padding: 40px;
  text-align: center;
  color: var(--muted);
  font-size: 11px;
  letter-spacing: 2px;
}
</style>
</head>
<body>
<header>
  <h1>FTC · STUDIO</h1>
  <p>FULL TIME CHRISTIAN · 2026 · COLLECTION 1</p>
</header>
"""
    ]

    parts.append(f"""
<section>
  <h2>STREETWEAR GRAPHICS · WHISPER TIER</h2>
  <p class="lead">{len(graphics)} restraint-tier procedural designs — cornerstone, veil, living-water, ember, threshold, covenant-arc, manna, wilderness, still-waters, vine, ladder, alabaster, broken-grid, mercy-seat, tabernacle. Faith is felt, not announced.</p>
  <div class="grid">
    {"".join(graphic_card(p) for p in graphics)}
  </div>
</section>
""")

    if kimi_outputs:
        parts.append(f"""
<section>
  <h2>KIMI · GLM · GPT IMAGE 2 / SEEDREAM</h2>
  <p class="lead">{len(kimi_outputs)} designs from the real LLM stack — 22 Kimi K2 agents brainstorming briefs in parallel, GLM 4.6 ranking, GLM 4.5-Air safety scan, OpenRouter GPT Image 2 generating (Fal Seedream-4 fallback), Qwen VL3 reviewing brand alignment. Two agents (K-21, K-22) carry BoohooMAN men's editorial composition pacing.</p>
  <div class="grid">
    {"".join(kimi_card(p) for p in kimi_outputs)}
  </div>
</section>
""")

    parts.append("""
<footer>
  Generated by the FTC pipeline · 290-agent village · DeepSeek Flash v4 + Flux + Seedream + Nano Banana · OpenRouter / Fal.ai / Novita · iPhone app ready for TestFlight
</footer>
</body>
</html>
""")

    OUT.write_text("\n".join(parts))
    size_kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT} ({size_kb:.0f} KB) — {len(graphics)} whisper graphics + {len(kimi_outputs)} Kimi/GPT Image renders")


if __name__ == "__main__":
    main()
