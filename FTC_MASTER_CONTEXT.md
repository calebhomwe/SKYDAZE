# FTC FULL TIME CHRISTIAN — MASTER CONTEXT FILE
> **VERSION:** 2.2 | **LAST UPDATED:** 2026-05-25  
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
| Reference Scraping | ⏳ Pending | Run `scraper.py` first |
| Test Batch (5 concepts) | ⏳ Pending | Validate with `run_test.py` |
| Full Generation (100) | 🔒 Locked | Unlocks after test batch passes |
| Shopify Integration | 🔒 Locked | Post-generation phase |
| Social Scheduler | 🔒 Locked | Post-promo phase |

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

> **USAGE INSTRUCTION FOR CLAUDE:**  
> Before responding to ANY FTC-related query, read this file in full.  
> If asked to generate concepts, validate against Section 4 + Section 5.  
> If asked to write code, comply with Section 3 + Section 6.  
> If uncertain about aesthetic alignment, default to Section 2 + Section 1.  
> **NEVER deviate from this context. This is the brand.**
