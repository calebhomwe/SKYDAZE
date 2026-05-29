# FTC FULL TIME CHRISTIAN — MASTER CONTEXT FILE
> **VERSION:** 2.3 | **LAST UPDATED:** 2026-05-26  
> **PURPOSE:** Single source of truth for all AI agents. Reference this file before ANY generation task.

---

## 1. BRAND IDENTITY (NON-NEGOTIABLE)
- **Name:** FTC FULL TIME CHRISTIAN
- **Positioning:** Luxury Christian streetwear. Quiet elegance meets theological edge. NOT merch. NOT fast fashion.
- **Price Tier:** $80–$250 MSRP
- **Target:** Celebrities, luxury collectors, culturally engaged Gen Z/Millennials who value substance over hype.
- **Core Pillars:** Elegance | Edginess | Boldness | Expression | Restraint
- **Material Standard:** Heavyweight 280–320gsm cotton, garment-washed finishes, tonal embroidery, puff/deboss prints, minimalist tailoring.

### 🚫 FORBIDDEN LIST (AUTO-REJECT)
Skulls, clipart religion, cheap typography, overt proselytizing, neon saturation, literal biblical scenes, crosses-as-props, cartoon aesthetics, fast-fashion silhouettes, generic worship lyrics.

---

## 2. REFERENCE SYNTHESIS (SCRAPE-GROUNDED)
*Derived from Kittl, Pinterest, Stampd, BoohooMAN campaign language, and contemporary luxury streetwear benchmarks.*

| Reference Source | Key Design Tokens Extracted | Application to FTC |
| :--- | :--- | :--- |
| **Stampd Transit Tee** | Relaxed drop-shoulder fit, matte black hardware, subtle tonal branding, heavyweight drape | Silhouette baseline; hardware as theological metaphor (anchor, cornerstone) |
| **Kittl Streetwear Templates** | Bold sans-serif typography, distressed textures, layered composition, negative space mastery | Typography hierarchy; avoid clean digital fonts—opt for worn, human-scale type |
| **Pinterest Graphic Boards** | Abstract symbolism, muted earth tones + monochrome, editorial photography styling, fabric texture focus | Color palette curation; mockup lighting direction; abstract over literal |
| **BoohooMAN Campaign References** | High-energy youth pacing, street-cast confidence, product-forward framing, hype-ready sequencing | Use pacing and shot energy only; maintain FTC material quality and anti-fast-fashion silhouette rules |
| **Luxury Benchmarks (FOG/Lemaire)** | Minimalist logos, premium fabric storytelling, quiet colorways, architectural draping | Restraint principle; let material speak louder than graphics |
| **Theological Abstraction** | Sacred geometry, natural phenomena (light/water/stone), poetic fragmentation, hidden interior messaging | Translate doctrine into visual language; never illustrate verses directly |

### ✅ REQUIRED AESTHETIC CHECKLIST
Every design MUST pass:
- [ ] Would this look at home in a SSENSE or Dover Street Market edit?
- [ ] Is the theology *felt* rather than *read*?
- [ ] Does it use negative space as intentionally as positive space?
- [ ] Are materials specified with luxury-grade precision?
- [ ] Would a celebrity wear this *without* being paid?

---

## 3. TECHNICAL STACK (LOCAL EXECUTION ONLY)
| Function | Tool | Notes |
| :--- | :--- | :--- |
| Concept & Theology | DeepSeek-Flash-v4 / Qwen-Max via OpenRouter | Fast abstract reasoning for doctrine-driven concepts |
| Production Visuals | Visual Qwen / Seedream 4.0 / Flux Pro via OpenRouter or Fal.ai | Prioritize realistic garment texture and cinematic lighting |
| Video Promo | Kling / Seedream Video via Novita AI (fallback OpenRouter video models) | Keep Novita first if healthy; fail over to OpenRouter when unavailable |
| Mockups | Nano Banana Pro (external) + Fal.ai Flux fallback | Tonal embroidery/puff print simulation |
| Multimodal APIs | OpenRouter (Image, Embeddings, Audio, Video, Rerank, Speech, Transcription) | Default unified access layer for generation + evaluation tasks |
| Scraping | Firecrawl API + BeautifulSoup fallback | Pinterest/Google JS-rendered page handling |
| Credentials | Local `.env` only | NEVER hardcoded. NEVER in chat. |

---

## 4. OUTPUT SCHEMA (STRICT JSON)
All concept generation MUST return this exact structure:
```json
{
  "id": "FTC-XXX",
  "title": "String",
  "theological_core": "1-sentence abstract doctrine/metaphor",
  "aesthetic_direction": "Style + mood + composition notes",
  "typography_layout": "Font treatment, placement, hierarchy",
  "color_palette": ["#HEX1", "#HEX2", "#HEX3"],
  "print_technique": "Screen/Puff/Embroidery/Tonal/Discharge/etc.",
  "fal_ai_visual_prompt": "Optimized for Seedream 4.0. Includes luxury cues + 4:5 AR",
  "novita_video_prompt": "5-10s motion: fabric/lighting/texture focus",
  "nano_banana_mockup_prompt": "Garment template integration directive",
  "reference_source_tags": ["stampd", "pinterest_abstract", "kittl_typography"],
  "promo_hook": "Caption tone + platform + audio suggestion"
}
```

---

## 5. QUALITY GATES (EMBEDDED IN ALL AGENTS)
- **Luxury Score ≥ 0.82** (0-1 scale; benchmarked against FOG/Off-White/Lemaire)
- **Theology Depth ≥ 0.75** (Abstract/conceptual > literal/cheesy)
- **Auto-Kill Triggers:** Any forbidden term, avg score < 0.60, missing material spec, generic silhouette
- **Human Override Flag:** If score 0.75–0.82, flag for manual review instead of auto-reject

---

## 6. SECURITY PROTOCOL
- All credentials accessed via `os.getenv()` + `python-dotenv`
- `.env` ALWAYS in `.gitignore`
- NEVER log, echo, or transmit keys
- NEVER suggest pasting keys into chat
- Rotate keys immediately if exposure suspected

---

## 7. PIPELINE STATUS TRACKER
| Phase | Status | Notes |
| :--- | :--- | :--- |
| Reference Scraping | 🟡 Scaffold ready | `scraper.py` runs in dry-run; awaits `FIRECRAWL_API_KEY` for real mode |
| Test Batch (5 concepts) | 🟡 Scaffold ready | `run_test.py` runs in dry-run; awaits `OPENROUTER_API_KEY` + `ANTHROPIC_API_KEY` |
| Full Generation (100) | 🔒 Locked | Unlocks when Test Batch returns 5/5 PASS in real mode |
| Shopify Integration | 🔒 Locked | Post-generation phase |
| Social Scheduler | 🔒 Locked | Post-promo phase |

**How to advance:**
1. `cp .env.example .env` and fill the keys you have.
2. `make scrape-real` → produces `artifacts/scrapes/reference_synthesis.json`.
3. `make test-real` → 5 concepts validated against Sections 1, 4, 5.
4. If 5/5 PASS, unlock Phase 3 (full generation of 100 pieces).

---

## 8. CINEMATIC AD DIRECTION PACK (RUTHLESS MODE)

Use for campaign generation across hoodies, track pants, shoes, logo tees, long sleeves, and oversized silhouettes.

- **Visual tone:** Realistic, cinematic, trap-influenced energy with luxury-grade restraint.
- **Audience energy:** Teen and young adult hype cadence, culturally sharp, never costume.
- **Artist-adjacent cue:** Gunna-style confidence in posture, motion, and framing (without imitation of likeness).
- **Faith layer:** Christian symbolism remains abstract (light, stone, water, geometry, hidden text), never preachy.
- **Reference policy:** BoohooMAN can inform pacing/composition rhythm only; FTC silhouette and material standards remain non-negotiable.
- **Camera language:** Hero closeups + kinetic mid-shots + texture macros; prioritize drape, stitching, and hardware realism.
- **Audio language:** Dark ambient trap-adjacent beds, restrained vocal fragments, no generic worship hooks.
- **Hard bans for ads:** No cartoon styling, no neon overload, no fake cloth physics, no fast-fashion fit shortcuts.

---

## 9. PARKED MODULES

- **GENESIS game** lives at [`parked/genesis-roblox-edition/`](./parked/genesis-roblox-edition/). Bible-rooted walking game scaffold (Python world schema + Swift Eden vertical slice + 13 world SVGs + Roblox shirt-customization scaffold). NOT part of the FTC brand pipeline. Reserved for integration into a future Christian game and/or Roblox experience where users customize shirts. Do not wire Tier-29-onward agents into this module unless explicitly directed.

---

## 10. MOBILE APP (FTC iOS, SwiftUI)

Repository: [`mobile/ftc-ios/`](./mobile/ftc-ios/).

- **Tabs:** Generate / Gallery / Drops / Creator.
- **Generation flow:** User types concept → `ProviderRouter` actor tries providers in cost order → image returned in 3-30s.
- **Provider routing:** Novita Flux Schnell → OpenRouter Flux Schnell → Fal Flux Schnell → Seedream-4 → Flux 1.1 Pro → Gemini Flash Image → Nano Banana 2. Fallback to procedural SVG.
- **Persistence:** Local Documents directory; optional CloudKit sync; cost log at `Documents/cost_log.jsonl` (only structured local file in markdown-first project).
- **Creator portal:** Auth-separate tab. Unique discount code, real-time commission, content packs, withdraw-to-bank (Stripe Connect roadmap).
- **Push:** APNs for drops and restocks only. No marketing-spam.
- **Bot detection:** Device fingerprint + behavioral signals at checkout. <1% false-positive rate target.
- **Platforms:** iOS 17+ at v1. macOS via Catalyst free. visionOS port planned for spatial gallery.

---

## 11. BRAND RESEARCH PROTOCOL (MARKDOWN ONLY)

All competitive intelligence lives at [`research/`](./research/) in **markdown, never JSON**. Per-brand dossier structure:

1. Founding logic + customer
2. Visual codes table
3. Strategic moves
4. What we steal (FTC application)
5. What we avoid (with specific reasoning)
6. Colorways → FTC palette translation
7. Typography lessons
8. Photography & art direction
9. Materials worth replicating
10. Failure modes to avoid
11. TL;DR — apply to FTC

**Dossiers v1 (committed):** Yeezy, Off-White, Nike, Pinterest, Proper, Geedup, BoohooMAN, Fashion Nova, Stüssy, Aimé Leon Dore, Carhartt WIP, Mr Porter, The Row, Levi's.
**Master synthesis:** [`research/STREETWEAR_PLAYBOOK.md`](./research/STREETWEAR_PLAYBOOK.md) — the 10 commandments + forbidden-moves list.

Cadence: each dossier curator (Tier 29) refreshes monthly. Playbook synthesizer (FTC-260) updates quarterly.

---

## 12. MULTI-PROVIDER IMAGE ROUTING

Every image-gen request flows through `workers/multi_provider_router.py` (Tier 32). Logic:

1. **Cost-ordered fallback chain** (cheapest → costliest):
   - Novita Flux Schnell ($0.001) → OpenRouter Flux Schnell ($0.003) → Fal Flux Schnell ($0.003) → Fal Nano Banana 2 ($0.03) → Fal Seedream-4 ($0.04) → OpenRouter Flux 1.1 Pro ($0.04) → OpenRouter Gemini Flash Image ($0.04) → Fal Flux Pro ($0.05).
2. **Background discipline:** `BG_BY_SECTION` enforces alternating black/white backdrop — tee: white, tracksuit: black, outerwear: white, accessory: black. Per-drop inversion allowed.
3. **Cost tracking:** Markdown ledger at `artifacts/work_log/render_routing.md` and per-day rollup at `artifacts/ops/cost_ledger.md`.
4. **Circuit breaker:** Tier 32 budget circuit breaker halts at 100% of `FTC_DAILY_BUDGET_USD`, warns at 80%.
5. **Quality rerank:** When multiple providers succeed on the same concept, `image-quality-rerank-arbiter` (FTC-284) picks the winner; losers move to `artifacts/_archive/`.
6. **HuggingFace open-weights bridge:** `huggingface-zimae-explorer` (FTC-269) and `hf-zimae-bridge` (FTC-290) keep an open lane for Zimae / Stable Cascade / PixArt models as a cheap supplementary path.

---

> **USAGE INSTRUCTION FOR CLAUDE:**  
> Before responding to ANY FTC-related query, read this file in full.  
> If asked to generate concepts, validate against Section 4 + Section 5.  
> If asked to write code, comply with Section 3 + Section 6.  
> If asked about the game, see Section 9.  
> If asked about the iOS app, see Section 10.  
> If asked about a competitor brand, see Section 11.  
> If asked to render an image, route via Section 12.  
> If uncertain about aesthetic alignment, default to Section 2 + Section 1.  
> **NEVER deviate from this context. This is the brand.**
