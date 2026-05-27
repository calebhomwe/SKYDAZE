# Parked: GENESIS game / Roblox shirt customization

> **Status:** Parked. Not wired into the FTC brand pipeline. Held here until it gets folded into an actual Christian game or Roblox project where users customize shirts.

## Why this exists separately

The original idea was a contemplative Bible-rooted walking game ("GENESIS") that the player walks through — biblical worlds (Eden, Galilee, Bethlehem, Jerusalem, Sinai, Gethsemane) and modern diaspora cities (Scarborough, Perth, DMV, Maryland, Brooklyn, South London, Lagos Island). A first vertical slice was written in SwiftUI (the Eden scene) before realising this should be its own project, not tangled into the FTC streetwear brand pipeline.

So it lives here, fully self-contained, ready to be lifted into either:
1. **A standalone iOS / macOS / visionOS game** (Swift / SwiftUI, the existing scaffold).
2. **A Roblox experience** where players customize shirts using FTC-themed templates (see [`roblox/`](./roblox/) for the scaffold).
3. **A separate Christian game project** — engine-agnostic. The world/character/item data is in plain Python.

## What's inside

```
parked/genesis-roblox-edition/
├── python/genesis/       # World/character/item schemas (Python, engine-agnostic)
│   ├── world_schema.py   # 13 worlds: 6 biblical + 7 diaspora
│   ├── characters.py     # 18 characters: 11 biblical + 7 modern
│   ├── items.py          # 35 collectibles with weight + rarity
│   └── mesh_renderer.py  # Procedural isometric SVG world generator
├── ios/Genesis/          # Swift vertical slice (Eden scene playable)
│   ├── GenesisModels.swift
│   ├── EdenScene.swift
│   └── GenesisRootView.swift
├── worlds-svg/           # 13 rendered SVG world tiles (concept art)
│   ├── W-001-eden.svg ... W-107-lagos-island.svg
├── research/game_dev/    # Game dev playbook (Monument Valley / Sky:CoTL refs)
│   └── GAME_DEV_PLAYBOOK.md
└── roblox/               # Roblox Lua shirt-customizer scaffold
    ├── README.md
    └── ShirtCustomizer.lua
```

## Quick re-render of the concept art

```bash
# From repo root
python3 -m parked.genesis-game.python.genesis.mesh_renderer
```

(If the dashes in the path cause Python import trouble, rename the dir to `genesis_game` first — or just lift the contents into a new repo where you can name dirs as you wish.)

## Roblox path (the user's stated next destination)

You wanted players to be able to customize shirts in a future Christian Roblox game. See [`roblox/README.md`](./roblox/README.md) for:

- How Roblox shirt templates work (585×559 px UV layout)
- How to upload FTC streetwear graphics as decals
- A Lua server script that lets players select from a catalog of FTC-themed shirts
- A Lua server script that lets players upload their own decal ID
- How to integrate with Roblox MarketPlace for paid customization

The 30 FTC streetwear graphics in `../../artifacts/graphics/*.svg` can each become a Roblox shirt decal — convert to PNG, upload to Roblox, paste the asset ID into the catalog Lua table.

## Why not delete it

- The 13 world SVGs are nice as concept art / drop-campaign backdrops even without the game.
- The world / character / item schema is decent worldbuilding work; reuses easily.
- The Eden Swift scene is a clean SwiftUI walking-game template anyone can fork.
- The game-dev playbook (Monument Valley, Sky:CoTL, Ghibli refs) is useful research regardless of which engine wins.

## When this gets un-parked

Lift the entire `parked/genesis-roblox-edition/` directory into either:
- a new `calebhomwe/genesis-game` repository (recommended — clean separation)
- the FTC Roblox game repo (when it exists)

Cherry-pick what fits the target engine. Discard what doesn't.

## NOT to do

- Do NOT wire this back into the FTC brand pipeline.
- Do NOT add it as a tab in the FTC iOS shopping app.
- Do NOT spawn agents for it from the main REGISTRY.yaml.
- The brand-side of the repo treats this directory as if it were `.gitignored`.
