# LUMENFALL

Arcaea-inspired **dual-plane** lane rhythm game built in **Godot 4.4**. Tap, hold, flick, and trace **Lumen Arcs** on floor and sky rails. Build combo to trigger **RAPTURE CHAIN** fever for double score, screen shake, and a BPM-synced beat bed.

## Controls

| Plane | Keys | Lanes |
|-------|------|-------|
| Floor | D F J K | 0–3 |
| Sky | W E U I | 0–3 |

| Action | Key |
|--------|-----|
| Menu | ESC |
| Retry | R |

## Run locally

```bash
# From repo root (Godot 4.4+ on PATH)
make game-run

# Headless stress suites (200 / 500 / 1000 / 2000 note spawns, dual-plane)
make game-stress
```

## Project layout

```
games/lumenfall/
├── data/charts/          # JSON beatmaps (first_light, rapture_chain, void_surge)
├── scenes/Menu.tscn      # Song select + daily mission
├── scenes/Game.tscn      # Gameplay + HUD
├── scripts/autoload/     # GameState, ChartLibrary, BeatEngine
├── scripts/gameplay/     # BeatmapPlayer, dual-plane lanes, notes
├── tests/                # Headless stress harness
└── docs/RESEARCH.md      # Arcaea / rhythm-game research
```

## Meta progression

- **Daily mission**: clear 3 songs per UTC day
- **Streak**: consecutive play days (resets if you skip a day)
- **Unlocks**: B+ on *First Light* → *Rapture Chain*; A+ on *Rapture Chain* → *Void Surge*

## Chart format

```json
{"t": 1500, "lane": 1, "plane": "floor", "type": "tap"}
{"t": 2200, "lane": 0, "plane": "sky", "type": "flick"}
{"t": 3300, "lane": 0, "plane": "floor", "type": "arc", "lane_end": 3, "end_t": 3900}
```

Generate procedural charts:

```bash
python3 games/lumenfall/tools/generate_chart.py rapture_chain
python3 games/lumenfall/tools/generate_chart.py void_surge
python3 games/lumenfall/tools/generate_chart.py custom --title "My Chart" --count 120 --bpm 180
```

## Agent squad (OpenRouter Spawn)

Best coding models for app polish — see `artifacts/lumenfall/agent_squad.md`.

```bash
make spawn-lumenfall-plan
make spawn-lumenfall-execute   # bounded 4-worker launch
```

## Image generation hook

```bash
python3 games/lumenfall/tools/generate_cover.py
```

Writes `assets/textures/cover_prompt.json` for OpenRouter image generation when `OPENROUTER_API_KEY` is set.

## Design goals (from research)

- Dual-plane readability like Arcaea (floor taps + sky flicks/arcs)
- Strict Pure/Great/Good/Miss ladder with visible accuracy
- Sub-2s restart loop and fever dopamine spike at 50 combo
- Procedural BPM beat bed via `BeatEngine` (no external audio required)
- Shader-driven backgrounds for fast skin swaps
