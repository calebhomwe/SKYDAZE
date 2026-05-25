"""Generate the two explicit high-fidelity fire prompt tests.

Outputs:
  artifacts/fire_tests/glitch_cross.svg
  artifacts/fire_tests/torn_paper_revelation.svg
  artifacts/fire_tests/index.html

Run:
  python3 generate_fire_tests.py
"""

from __future__ import annotations

from ftc.config import ARTIFACTS
from ftc.print_assets import render_fire_prompt_svg

OUT = ARTIFACTS / "fire_tests"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    assets = {
        "glitch_cross.svg": render_fire_prompt_svg("glitch-cross"),
        "torn_paper_revelation.svg": render_fire_prompt_svg("torn-paper"),
    }
    for filename, svg in assets.items():
        (OUT / filename).write_text(svg, encoding="utf-8")

    html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>FTC fire prompt tests</title>
<style>
body { margin: 0; background: #111; color: #eee; font-family: Arial, sans-serif; }
main { display: grid; grid-template-columns: repeat(2, minmax(320px, 1fr)); gap: 24px; padding: 24px; }
figure { margin: 0; background: #222; padding: 16px; }
img { width: 100%; display: block; }
figcaption { margin-top: 10px; font-size: 14px; letter-spacing: 0.08em; text-transform: uppercase; }
</style>
</head>
<body>
<main>
  <figure><img src="glitch_cross.svg" alt="Glitch Cross"/><figcaption>01 Glitch Cross</figcaption></figure>
  <figure><img src="torn_paper_revelation.svg" alt="Torn Paper Revelation"/><figcaption>02 Torn Paper Revelation</figcaption></figure>
</main>
</body>
</html>
"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
