# SKYDAZE — FTC FULL TIME CHRISTIAN

> Luxury Christian streetwear brand pipeline + cross-platform AI-generation iOS app. Built by a 290-agent village under one [master context](./FTC_MASTER_CONTEXT.md) constitution. A separate Bible-rooted game scaffold lives parked at [`parked/genesis-roblox-edition/`](./parked/genesis-roblox-edition/).

---

## See the work first

| Artifact | Open it |
| :--- | :--- |
| **Visual gallery** — 30 streetwear graphics + 13 concept world tiles | [`artifacts/gallery.html`](./artifacts/gallery.html) — open in any browser |
| **Streetwear graphics** — 15 procedural styles, 30 renders | [`artifacts/graphics/`](./artifacts/graphics/) |
| **Brand research** — Yeezy, Off-White, Nike, etc. (11 dossiers) | [`research/brands/`](./research/brands/) |
| **iOS app scaffold** — SwiftUI, calls Fal/Novita/OpenRouter | [`mobile/ftc-ios/`](./mobile/ftc-ios/) |
| **Parked: GENESIS game / Roblox** — for later integration | [`parked/genesis-roblox-edition/`](./parked/genesis-roblox-edition/) |

---

## What's in this repo

### Brand pipeline (`ftc/`, `workers/`, `agents/`)
1000-design combinatorial collection engine. 290 specialized AI agents across 33 tiers, each with a tight system prompt, gates, and handoffs. DeepSeek Flash v4 drives high-throughput concept generation; Claude Opus 4.7 owns the orchestration tier. See [`agents/README.md`](./agents/README.md).

### Parked work — GENESIS game (`parked/genesis-roblox-edition/`)
Scaffold for a future Bible-rooted walking game / Roblox shirt-customization experience. Includes the Python world schema (13 worlds), the Swift Eden vertical slice, 13 rendered world SVGs as concept art, the game-dev playbook, and a Roblox Lua shirt-customizer scaffold. **Not wired into the brand pipeline.** Ready to lift into a separate game repo or your Roblox project. See [`parked/genesis-roblox-edition/README.md`](./parked/genesis-roblox-edition/README.md).

### iOS app (`mobile/ftc-ios/`)
SwiftUI app with four tabs:
- **Generate** — type a concept, ProviderRouter actor picks cheapest healthy provider (Fal/Novita/OpenRouter), image appears in 3-30s
- **Gallery** — saved renders, local Documents persistence + optional iCloud sync
- **Drops** — current FTC catalog with story-first product views
- **Creator** — for ambassadors: unique discount code, real-time commission, content packs

### Brand research (`research/`)
- [`research/STREETWEAR_PLAYBOOK.md`](./research/STREETWEAR_PLAYBOOK.md) — 10 commandments synthesized from 8 brand dossiers
- [`research/brands/`](./research/brands/) — deep markdown dossiers on Yeezy, Off-White, Nike, Pinterest, Proper, Geedup, BoohooMAN, Fashion Nova, Stüssy, Aimé Leon Dore, Carhartt WIP (11 brands)

### Image generation infrastructure (`workers/`)
- `openrouter_image_worker.py` — Gemini 2.5 Flash Image, Flux 1.1 Pro, DALL·E 3
- `fal_image_worker.py` — Flux Pro, Seedream-4, Nano Banana 1+2
- `novita_image_worker.py` — Seedance, Flux Schnell, SDXL
- `multi_provider_router.py` — 8-provider cost-ordered fallback chain; `BG_BY_SECTION` enforces black/white background alternation
- `comfyui_worker.py` — self-hosted ComfyUI path (~$2-3 for 1000 renders on RunPod spot)

---

## Quickstart

### 1. Install
```bash
make install   # installs Python deps + initializes caveman submodule
cp .env.example .env  # fill in your API keys
```

Keys needed (all optional in dry-run mode):
- `OPENROUTER_API_KEY` — DeepSeek Flash v4 + Hermes-3 + image gen
- `FAL_KEY` — Flux Pro / Seedream-4 / Nano Banana
- `NOVITA_API_KEY` — Seedance + Flux Schnell
- `FIRECRAWL_API_KEY` — web scraping
- `SHOPIFY_STORE_DOMAIN` + `SHOPIFY_ADMIN_TOKEN` — distribution

### 2. Generate visible output (no keys required)
```bash
make graphics   # 30 SVG streetwear graphics
make gallery    # rebuild artifacts/gallery.html
```

### 3. Real image rendering (keys required)
```bash
make render-multi          # cost-ordered fallback across all 3 providers
make render-comfy          # self-hosted ComfyUI on RunPod (~$2-3 for 1000 images)
```

### 4. Build the iOS app
```bash
cd mobile/ftc-ios/
cp FTC/Resources/Secrets.plist.example FTC/Resources/Secrets.plist
# Edit Secrets.plist, fill in keys
open Package.swift  # opens in Xcode
# Press cmd-R to run
```

### 5. YouTube intelligence + brand research
```bash
make youtube-harvest        # dry-run synthesis
make youtube-harvest-real   # live transcripts (no key needed)
make brand-research         # lists dossiers + opens playbook
make mobile-build           # iOS build instructions
```

---

## Architecture diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   FTC_MASTER_CONTEXT.md                     │
│         (one source of truth · all 300 agents bow)          │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
  ┌─────▼─────┐                            ┌──────▼──────┐
  │  Brand    │                            │   Game      │
  │  pipeline │                            │   GENESIS   │
  └─────┬─────┘                            └──────┬──────┘
        │                                         │
  ┌─────▼─────┐  ┌──────────┐  ┌──────────┐ ┌────▼────┐
  │ Concepts  │  │ Graphics │  │ Renders  │ │ Worlds  │
  │ (JSON)    │  │  (SVG)   │  │  (PNG)   │ │  (SVG)  │
  └─────┬─────┘  └─────┬────┘  └─────┬────┘ └────┬────┘
        │              │              │            │
        └──────────────┼──────────────┴────────────┘
                       │
              ┌────────▼────────┐
              │ Multi-Provider  │
              │   Router        │  ← Fal / Novita / OpenRouter
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │ Mobile iOS app  │  ← end-customer + creator portal
              └─────────────────┘
```

---

## Stack

| Layer | Choice | Why |
| :--- | :--- | :--- |
| Orchestration | Claude Opus 4.7 | Reasoning, planning, brand-steward gates |
| Fast LLM | DeepSeek Flash v4 (via OpenRouter) | Concept gen, copy blast, theology check |
| Multi-step tool use | Hermes 3 Llama-3.1-405B (via OpenRouter) | OpenClaw integration, structured generation |
| Code execution | Cline / Claude Sonnet 4.6 | Pipeline automation, refactors |
| Image generation | Flux 1.1 Pro / Seedream-4 / Nano Banana 1+2 / Gemini Flash Image | Photoreal + mockup + editorial |
| Video | Novita Seedance / OpenRouter video | Cinematic ad pipeline |
| Web scraping | Firecrawl + youtube-transcript-api + yt-dlp | Reference synthesis |
| Mobile | SwiftUI 5 + Metal (iOS 17+) | Native performance, no JS bridge |
| Compression | [caveman](https://github.com/JuliusBrussee/caveman) (vendored submodule) | 65-75% token reduction on long prompts |
| Self-host renders | ComfyUI + Flux Dev FP8 + RunPod spot | ~$2-3 to render 1000 designs vs ~$40 on Fal |
| Orchestration scheduling | n8n + Postgres (Docker Compose) | Always-on pipeline |
| Frontend | Catalog HTML (self-contained, base64 SVG embed) | Open anywhere, no build |

---

## Make targets

| Target | What it does |
| :--- | :--- |
| `make install` | Install Python deps + caveman submodule |
| `make scrape` / `make scrape-real` | Reference scrape (dry / real) |
| `make test` / `make test-real` | Smoke pipeline (dry / real) |
| `make collection` | Generate 1000 design concepts |
| `make package` | Self-contained catalog HTML |
| `make render` / `make render-dry` | Fal.ai render path |
| `make render-comfy` / `make render-comfy-dry` / `make render-comfy-cn` | ComfyUI self-host path |
| `make render-multi` / `make render-multi-dry` | Multi-provider cost-routed render |
| `make youtube-harvest` / `make youtube-harvest-real` | YouTube transcript intelligence |
| **`make graphics`** | **Regen 30 SVG streetwear graphics** |
| **`make worlds`** | **Regen 13 SVG GENESIS world tiles** |
| **`make gallery`** | **Build self-contained `artifacts/gallery.html`** |
| `make brand-research` | List brand dossiers |
| `make game-dev` | Index GENESIS assets |
| `make mobile-build` | iOS build instructions |
| `make spawn-plan` / `make spawn-dry` / `make spawn-launch` | OpenRouter swarm |
| `make caveman-install` / `make caveman-update` / `make caveman-uninstall` | Token-compression submodule |
| `make clean` | Wipe regenerable artifacts |
| `make lint` | ruff over all Python |

---

## The 300-agent village

| Tier | Domain | Count |
|---:|---|---:|
| 0 | Orchestrators | 5 |
| 1 | Concept & Theology | 10 |
| 2 | Aesthetic Direction | 10 |
| 3 | Visual Production | 10 |
| 4 | Mockups | 5 |
| 5 | Video | 8 |
| 6 | Scraping & Research | 8 |
| 7 | Quality Assurance | 8 |
| 8 | Copy & Editorial | 6 |
| 9 | Distribution | 5 |
| 10 | Marketing & Promo | 5 |
| 11 | Ops & Compliance | 4 |
| 12 | Analytics | 4 |
| 13 | Infrastructure | 5 |
| 14 | Agent Interoperability | 17 |
| 15 | Cinematic Ads | 10 |
| 16 | YouTube Intelligence | 10 |
| 17 | DeepSeek Flash Research | 10 |
| 18 | OpenClaw / Hermes Execution | 10 |
| 19 | Cline AI Execution | 10 |
| 20 | Market Intelligence | 10 |
| 21 | Demand & Retail | 10 |
| 22 | Drop Strategy & FOMO | 10 |
| 23 | Lifestyle Amplification | 10 |
| 24 | Faith Community Outreach | 10 |
| 25 | Generative Design Innovation | 10 |
| 26 | Wholesale & B2B | 10 |
| 27 | Cross-Platform Media | 10 |
| 28 | Data Science & ML | 10 |
| 29 | Brand Research | 10 |
| 30 | Graphic Design Engine | 10 |
| 31 | GENESIS Game Dev | 10 |
| 32 | Multi-Provider Image Router | 10 |
| 33 | Mobile App Build & Ship | 10 |
| | **Total** | **300** |

Full registry: [`agents/REGISTRY.yaml`](./agents/REGISTRY.yaml) (v2.1.0).

---

## Security & secrets

`.env` is `.gitignore`d. All credentials accessed via `os.getenv()` + `python-dotenv`. Never logged, never echoed, never transmitted. See [`SECURITY_QUICKSTART.md`](./SECURITY_QUICKSTART.md). iOS app keys live in `mobile/ftc-ios/FTC/Resources/Secrets.plist` (also gitignored).

---

## License

All work in this repo is © 2026 FTC FULL TIME CHRISTIAN. Vendored submodules retain their own licenses (`tools/caveman` is MIT).

---

## Acknowledgments

Built by [Claude Code on the web](https://claude.ai/code) under direct human direction. The agent village is the engine; the human chooses the destination.
