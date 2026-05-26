"""Static HTML catalog viewer for the 1000-design collection.

One file. Open in any browser. No build step. Lazy-loads SVGs from disk.
Includes filters for section, palette family, technique, fit, MSRP band.
"""

from __future__ import annotations

import json
from pathlib import Path

from .design_engine import Design


PAGE_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>FTC FULL TIME CHRISTIAN — Collection V1 (1000)</title>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
  :root {
    --ink: #0E0D0C;
    --bone: #F3F0EA;
    --line: #2a2a2a;
    --muted: #6c6358;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bone); color: var(--ink); font-family: ui-sans-serif, -apple-system, "Inter", Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }
  header { position: sticky; top: 0; z-index: 10; background: var(--bone); padding: 18px 28px 12px; border-bottom: 1px solid rgba(0,0,0,0.08); }
  header h1 { font-size: 13px; letter-spacing: 4px; font-weight: 500; margin: 0; text-transform: uppercase; }
  header .sub { font-size: 11px; color: var(--muted); letter-spacing: 1px; margin-top: 4px; }
  .controls { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 12px; }
  .controls select, .controls input { padding: 6px 10px; border: 1px solid rgba(0,0,0,0.15); background: white; font-family: inherit; font-size: 11px; letter-spacing: 0.5px; border-radius: 2px; }
  .count { font-size: 11px; color: var(--muted); margin-left: auto; align-self: center; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 18px; padding: 24px 28px 64px; }
  .card { background: white; border: 1px solid rgba(0,0,0,0.06); cursor: pointer; transition: transform 0.15s ease; }
  .card:hover { transform: translateY(-2px); border-color: rgba(0,0,0,0.18); }
  .card img, .card svg { width: 100%; height: auto; display: block; aspect-ratio: 4/5; }
  .card .meta { padding: 10px 12px 12px; }
  .card .meta .id { font-size: 9px; letter-spacing: 1.5px; color: var(--muted); text-transform: uppercase; }
  .card .meta .title { font-size: 13px; margin-top: 4px; }
  .card .meta .row { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: var(--muted); margin-top: 6px; letter-spacing: 0.5px; }
  .card .meta .swatches { display: flex; gap: 2px; margin-top: 8px; }
  .card .meta .swatches span { width: 14px; height: 14px; border: 1px solid rgba(0,0,0,0.08); }
  .modal { display: none; position: fixed; inset: 0; background: rgba(14,13,12,0.92); z-index: 100; padding: 40px; overflow: auto; }
  .modal.open { display: flex; align-items: flex-start; justify-content: center; }
  .modal-inner { background: var(--bone); max-width: 1100px; width: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 30px; padding: 30px; }
  .modal img, .modal svg { width: 100%; height: auto; background: white; }
  .modal h2 { font-size: 18px; font-weight: 500; margin: 0 0 4px; }
  .modal .modal-id { font-size: 10px; letter-spacing: 2px; color: var(--muted); text-transform: uppercase; }
  .modal dl { font-size: 12px; line-height: 1.6; margin-top: 20px; }
  .modal dt { color: var(--muted); font-size: 10px; letter-spacing: 1px; text-transform: uppercase; margin-top: 12px; }
  .modal dd { margin: 2px 0 0; }
  .modal .close { position: fixed; top: 20px; right: 24px; color: var(--bone); cursor: pointer; font-size: 12px; letter-spacing: 2px; }
  @media (max-width: 800px) { .modal-inner { grid-template-columns: 1fr; } }
</style>
</head>
<body>
"""


def _card_html(d: Design, svg_rel_path: str) -> str:
    swatches = "".join(f'<span style="background:{h}"></span>' for h in d.palette.hexes)
    return f"""
<div class="card" data-section="{d.section}" data-family="{d.palette.family}" data-technique="{d.print_technique}" data-fit="{d.fit_family}" data-msrp="{d.msrp_usd}" data-id="{d.id}">
  <img loading="lazy" src="{svg_rel_path}" alt="{d.id} {d.title}"/>
  <div class="meta">
    <div class="id">{d.id}</div>
    <div class="title">{d.title}</div>
    <div class="row"><span>{d.section}</span><span>${d.msrp_usd}</span></div>
    <div class="swatches">{swatches}</div>
  </div>
</div>"""


def _designs_json(designs: list[Design], svg_rel_dir: str) -> str:
    rows = []
    for d in designs:
        row = d.as_catalog_row()
        row["svg_path"] = f"{svg_rel_dir}/{d.id}.svg"
        row["theological_core"] = d.theological_core
        row["typography_layout"] = d.typography_layout
        row["hardware_detail"] = d.hardware_detail
        row["aesthetic_direction"] = d.aesthetic_direction
        rows.append(row)
    return json.dumps(rows)


def _controls_html(designs: list[Design]) -> str:
    sections = sorted({d.section for d in designs})
    families = sorted({d.palette.family for d in designs})
    techniques = sorted({d.print_technique for d in designs})
    fits = sorted({d.fit_family for d in designs})

    def opts(name: str, values: list[str]) -> str:
        items = "".join(f'<option value="{v}">{v}</option>' for v in values)
        return f'<select id="f-{name}"><option value="">{name.upper()}</option>{items}</select>'

    return f"""
<div class="controls">
  {opts('section', sections)}
  {opts('family', families)}
  {opts('technique', techniques)}
  {opts('fit', fits)}
  <input id="f-q" type="search" placeholder="search id or title..." style="min-width: 220px;"/>
  <span class="count" id="count"></span>
</div>"""


SCRIPT = """
<script>
const allCards = Array.from(document.querySelectorAll('.card'));
const data = window.__FTC_DATA__;
const dataById = Object.fromEntries(data.map(r => [r.id, r]));
const $ = id => document.getElementById(id);
const count = $('count');

function apply() {
  const f = {
    section: $('f-section').value,
    family: $('f-family').value,
    technique: $('f-technique').value,
    fit: $('f-fit').value,
    q: $('f-q').value.toLowerCase(),
  };
  let shown = 0;
  allCards.forEach(c => {
    const visible = (
      (!f.section || c.dataset.section === f.section) &&
      (!f.family || c.dataset.family === f.family) &&
      (!f.technique || c.dataset.technique === f.technique) &&
      (!f.fit || c.dataset.fit === f.fit) &&
      (!f.q || c.dataset.id.toLowerCase().includes(f.q) || c.innerText.toLowerCase().includes(f.q))
    );
    c.style.display = visible ? '' : 'none';
    if (visible) shown++;
  });
  count.textContent = shown + ' / ' + allCards.length + ' shown';
}

['f-section','f-family','f-technique','f-fit','f-q'].forEach(id => {
  $(id).addEventListener('input', apply);
});
apply();

const modal = $('modal');
const modalInner = $('modal-inner');
$('modal-close').addEventListener('click', () => modal.classList.remove('open'));
modal.addEventListener('click', e => { if (e.target === modal) modal.classList.remove('open'); });

allCards.forEach(c => {
  c.addEventListener('click', () => {
    const d = dataById[c.dataset.id];
    if (!d) return;
    modalInner.innerHTML = `
      <div><img src="${d.svg_path}" alt="${d.id}"/></div>
      <div>
        <div class="modal-id">${d.id} · ${d.section}</div>
        <h2>${d.title}</h2>
        <dl>
          <dt>Theological core</dt><dd>${d.theological_core}</dd>
          <dt>Aesthetic direction</dt><dd>${d.aesthetic_direction}</dd>
          <dt>Typography</dt><dd>${d.typography_layout}</dd>
          <dt>Print</dt><dd>${d.print_technique} · ${d.print_placement}</dd>
          <dt>Hardware / Finish</dt><dd>${d.hardware_detail}</dd>
          <dt>Fit family</dt><dd>${d.fit_family}</dd>
          <dt>Palette</dt><dd>${d.palette_name} · ${d.palette_family} · ${d.palette_hex.join(' / ')}</dd>
          <dt>MSRP / COGS / Margin</dt><dd>$${d.msrp_usd} · $${d.estimated_cogs_usd} · ${d.margin_pct}%</dd>
        </dl>
      </div>
    `;
    modal.classList.add('open');
  });
});
</script>
"""


def render_catalog(designs: list[Design], svg_rel_dir: str = "svg") -> str:
    cards = "\n".join(_card_html(d, f"{svg_rel_dir}/{d.id}.svg") for d in designs)
    data = _designs_json(designs, svg_rel_dir)
    return (
        PAGE_HEAD
        + '<header><h1>FTC FULL TIME CHRISTIAN  ·  Collection V1</h1>'
        + f'<div class="sub">1000 designs  ·  250 tracksuit  ·  250 outerwear  ·  250 tee  ·  250 accessory</div>'
        + _controls_html(designs)
        + '</header>'
        + f'<div class="grid">{cards}</div>'
        + '<div id="modal" class="modal"><div id="modal-close" class="close">CLOSE ×</div><div id="modal-inner" class="modal-inner"></div></div>'
        + f'<script>window.__FTC_DATA__ = {data};</script>'
        + SCRIPT
        + "</body></html>"
    )


def write_catalog(designs: list[Design], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    html = render_catalog(designs)
    path = out_dir / "catalog.html"
    path.write_text(html, encoding="utf-8")
    return path
