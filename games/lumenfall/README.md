# LUMENFALL

Arcaea-inspired lane rhythm game built in **Godot 4.4**. Tap, hold, and trace **Lumen Arcs** across four lanes. Build combo to trigger **RAPTURE CHAIN** fever for double score and gold nebula visuals.

## Controls

| Key | Lane |
|-----|------|
| D | 0 |
| F | 1 |
| J | 2 |
| K | 3 |

## Run locally

```bash
# From repo root (Godot 4.4+ on PATH)
make game-run

# Headless stress suites (200 / 500 / 1000 note spawns)
make game-stress
```

## Project layout

```
games/lumenfall/
├── data/charts/          # JSON beatmaps
├── scenes/Main.tscn      # Playable scene
├── scripts/              # Gameplay + UI + visuals
├── shaders/              # Nebula background
├── tests/                # Headless stress harness
└── docs/RESEARCH.md      # Arcaea / rhythm-game research
```

## Chart format

```json
{"t": 1500, "lane": 1, "type": "tap"}
{"t": 2200, "lane": 1, "type": "hold", "end_t": 2900}
{"t": 3300, "lane": 0, "type": "arc", "lane_end": 3, "end_t": 3900}
```

## Image generation hook

```bash
python3 games/lumenfall/tools/generate_cover.py
```

Writes `assets/textures/cover_prompt.json` for OpenRouter image generation when `OPENROUTER_API_KEY` is set.

## Design goals (from research)

- Dual-plane readability like Arcaea (floor taps + arc traces)
- Strict Pure/Great/Good/Miss ladder with visible accuracy
- Sub-2s restart loop and fever dopamine spike at 50 combo
- Shader-driven backgrounds for fast skin swaps
