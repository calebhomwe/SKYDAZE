# FTC Cinematic Ad Campaign Playbook (Ruthless Mode)

Use this pack to generate high-energy, realistic Christian streetwear ads with trap-cinematic tone while preserving FTC luxury constraints.

## Global Prompt Prefix

Apply this prefix to every image/video request:

- Luxury Christian streetwear campaign
- realistic cloth physics, premium texture fidelity, cinematic lighting
- teen and young-adult hype energy, confident movement, zero cartoon styling
- abstract Christian symbolism only (light, stone, water, geometry, hidden text)
- no literal bible scenes, no neon overload, no fast-fashion fit shortcuts

## Model Routing

- Default route: OpenRouter
- Reasoning/writing: `deepseek/deepseek-chat-v4-fast`, `qwen/qwen-max`
- Stills: `qwen/visual-qwen`
- Video: Novita Kling/Seedream first; fallback to OpenRouter video models
- Audio/Speech/Transcription/Rerank/Embeddings: OpenRouter multimodal endpoints

## Campaign Concepts (Ready-to-Run)

### 1) Night Transit Testament (Hoodie + Track Pants)
- **Hero still prompt:** Oversized heavyweight black hoodie and washed track pants, matte hardware, reflective wet asphalt, sodium-vapor street light halo, model walking through mist, shallow depth of field, realistic cotton grain, tonal embroidery detail on chest.
- **Video prompt (8-10s):** Slow dolly-in from full body to chest embroidery, fabric sway in cold wind, one passing train light streak, model turns once, texture macro cut to cuff and hem seam, cinematic urban silence.
- **Audio cue:** Dark ambient 808 pulse, sparse reversed choir texture, no explicit lyric hook.

### 2) Cornerstone Velocity (Shoes + Long Sleeve)
- **Hero still prompt:** Technical sneaker closeup and oversized long sleeve in charcoal, cracked concrete stair set, low-angle frame, motion blur streak on passing traffic, realistic rubber and mesh detail.
- **Video prompt (6-8s):** Foot plant closeup -> stair ascent -> shoulder turn reveal of back graphic, emphasis on drape and stride confidence, moonlit concrete with soft fog.
- **Audio cue:** Tight sub-bass + metallic rim textures, restrained spoken phrase.

### 3) Hidden Psalm Club (Logo Tee + Overshirt)
- **Hero still prompt:** Logo tee under open overshirt, monochrome palette, church-window-inspired geometric light pattern cast on wall, clean negative space, premium jersey texture.
- **Video prompt (7-9s):** Static wide starts silent, model enters frame, light pattern shifts across shirt logo, interior label macro with hidden text, final locked-off portrait.
- **Audio cue:** Minimal trap percussion with long reverb tails.

### 4) Mercy in Motion (Full Oversized Set)
- **Hero still prompt:** Oversized hoodie, track pants, and sneaker stack, multi-model cast (max 2), parking structure top floor, overcast sky, wind-driven fabric movement, editorial framing.
- **Video prompt (10-12s):** Wide hero walk -> synchronized stop -> texture closeups -> rooftop edge silhouette, keep cuts slow and weighty.
- **Audio cue:** Atmospheric drone with restrained hi-hat accents.

### 5) Stone & Water Capsule (Long Sleeve + Shorts Variant)
- **Hero still prompt:** Stone-gray long sleeve, water reflections across fabric, reflective puddle foreground, abstract theological mood through light and surface.
- **Video prompt (6-8s):** Tracking shot along puddle reflection, rack focus from reflection to garment details, final chest-level lock shot.
- **Audio cue:** Low synth bed with filtered vocal chop, no chant cliches.

### 6) Youth Liturgy Run (Drop Montage)
- **Hero still prompt:** Multi-look collage frame: hoodie, logo tee, long sleeve, shoes; all in muted palette with matte blacks and bone whites, realistic campaign styling.
- **Video prompt (12-15s):** Three-location montage (street tunnel, stairwell, rooftop), each look gets one signature movement and one detail macro, end card with subtle FTC mark.
- **Audio cue:** Fast-paced trap-adjacent instrumental with clean master and clear speech pocket.

## Output QA Checklist

- Realism: cloth behavior, seams, embroidery, and shoe materials read as authentic
- Style: high energy without breaking luxury restraint
- Theology: symbolic and abstract only
- Product coverage: hoodies, track pants, shoes, logo tees, long sleeves, oversized fits
- Delivery: export hero stills, 6-15s cuts, transcript-safe speech hooks, reranked top variants
