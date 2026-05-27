# 2026-05-26 — Graphics, Game, Brand Research, Mobile

Trackable work log. Markdown not JSON. Updated as work progresses.

## Inputs

User asked for, in this session:
1. Streetwear graphic designs (rendered, not plain).
2. Bible game assets for GENESIS — the game in the repo.
3. Mesh worlds: Scarborough, Perth, DMV, Maryland, plus biblical worlds.
4. Generation via HuggingFace Zimae, Flux, Nano Banana 1/2, Seedance — cheapest-but-best, via OpenRouter / Fal.ai / Novita.
5. Brand research dossiers in markdown for Yeezy, Off-White, Nike, Pinterest, Proper, Geedup, BoohooMAN, Fashion Nova.
6. Game dev playbook markdown.
7. iPhone app that runs off Fal.ai / Novita / OpenRouter for generation.
8. More agents — added intentionally, not for the sake of count.
9. Output must be trackable (markdown work logs over JSON dumps).

## What shipped

### Game (GENESIS)
- `game/genesis/__init__.py` — package
- `game/genesis/world_schema.py` — 13 typed worlds (6 biblical, 7 modern/diaspora)
- `game/genesis/characters.py` — 18 characters (11 biblical, 7 modern)
- `game/genesis/items.py` — 35 collectibles
- `game/genesis/mesh_renderer.py` — procedural isometric SVG world renderer
- **Generated:** 13 SVG world tiles → `artifacts/game/genesis/worlds/`

### Streetwear graphics
- `ftc/graphics_engine.py` — 15 procedural graphic styles (cornerstone, veil, living-water, ember, threshold, covenant-arc, manna, wilderness, still-waters, vine, ladder, alabaster, broken-grid, mercy-seat, tabernacle)
- **Generated:** 30 SVG streetwear graphics → `artifacts/graphics/`

### Brand research (markdown dossiers)
- `research/brands/YEEZY.md`
- `research/brands/OFF_WHITE.md`
- `research/brands/NIKE.md`
- `research/brands/PINTEREST.md`
- `research/brands/PROPER.md`
- `research/brands/GEEDUP.md`
- `research/brands/BOOHOOMAN.md`
- `research/brands/FASHION_NOVA.md`
- `research/STREETWEAR_PLAYBOOK.md` — master synthesis
- `research/game_dev/GAME_DEV_PLAYBOOK.md` — Studio Ghibli, Monument Valley, Sky:CoTL, Animal Crossing references

### Image generation infrastructure
- `workers/openrouter_image_worker.py` — Gemini Flash Image / Flux Pro / DALL·E 3 via OpenRouter
- `workers/fal_image_worker.py` — Flux Pro / Seedream-4 / Nano Banana via Fal.ai
- `workers/novita_image_worker.py` — Seedance / Flux Schnell via Novita
- `workers/streetwear_render_worker.py` — orchestrates the three; per-section black-or-white background
- `workers/multi_provider_router.py` — picks cheapest healthy provider per shot

### Mobile (iPhone app)
- `mobile/ftc-ios/` — SwiftUI app scaffold
  - `FTCApp.swift` — entry
  - `Models/Generation.swift` — provider-agnostic gen request
  - `Services/FalService.swift` — Fal.ai client
  - `Services/NovitaService.swift` — Novita client
  - `Services/OpenRouterService.swift` — OpenRouter client
  - `Views/GenerateView.swift` — main UI
  - `Views/GalleryView.swift` — saved renders
  - `Resources/Info.plist`, `Package.swift`
- `mobile/ftc-ios/README.md` — build & TestFlight instructions

### Agents (REGISTRY.yaml v2.1)
Added Tiers 29–33 — 50 new agents (FTC-251..300):
- Tier 29: Brand Research Intelligence (10)
- Tier 30: Graphic Design Engine (10)
- Tier 31: Game Dev / GENESIS (10)
- Tier 32: Multi-Provider Image Router (10)
- Tier 33: Mobile App Build & Ship (10)

### Makefile
- `make graphics` — regen 30 streetwear graphics
- `make worlds` — regen 13 world tiles
- `make gallery` — build standalone gallery HTML
- `make brand-research` — print the playbook
- `make mobile-build` — print iOS build instructions

## Decisions

- **No JSON for trackable output.** Work logs, brand dossiers, playbooks are all markdown.
- **SVG-first for renders so user has visible output now**, without burning credits. The OpenRouter/Fal/Novita workers upgrade them to photoreal when keys are present.
- **Black/white background per section, alternating** — wired into `workers/streetwear_render_worker.py` via a `BG_BY_SECTION` map.
- **DeepSeek Flash v4** drives prompt generation for image gen — fast and cheap.
- **Tier expansion was intentional**: each agent has a clear gate, consume/produce contract, and handoff. No filler.

## Next (if user wants more)

- Convert SVG worlds to high-res PNG via cairosvg for non-browser viewing.
- Run actual photoreal renders once `FAL_KEY` / `NOVITA_API_KEY` / `OPENROUTER_API_KEY` are set in `.env`.
- Publish iOS app to TestFlight (requires Apple Developer account).
- Add a few additional brands the user mentioned later (e.g., Stüssy, Carhartt WIP, Aimé Leon Dore).
