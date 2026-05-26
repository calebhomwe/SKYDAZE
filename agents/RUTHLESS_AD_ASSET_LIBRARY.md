# FTC Ruthless Ad Asset Library

Distributed from parallel specialist runs: still prompts, video prompts, audio beds, hooks, transcription QA, and rerank rubric.

## Universal Negative Prompts

- lowres, blurry, noisy, jpeg artifacts, soft focus on subject
- cartoon, anime, 3d render, plastic skin, game-like shading
- neon overload, oversaturated colors, blown highlights, crushed blacks
- deformed hands, broken anatomy, warped footwear, inconsistent proportions
- cheap fast-fashion fit, thin fabric, fake logos, gibberish text, watermark

## Still Prompt Set (12 total)

| Concept | ID | Prompt |
|---|---|---|
| Stone Covenant Alley | C1-HERO | Rain-dark luxury city alley at blue hour, one teen model mid-stride between raw concrete walls and carved stone block, 35mm low angle 4:5 vertical frame, cool moon fill + warm sodium rim, oversized black hoodie + heavyweight track pants + premium sneakers, realistic cotton grain and stitch tension, faint geometric halo projection and water reflection path. |
| Stone Covenant Alley | C1-DETAIL | 85mm macro crop wrist-to-hip, hand adjusting hoodie cuff on wet stone plinth, cross-polarized key with cool rim bounce, raised embroidery and water-beaded cotton, hidden micro-text in cuff seam, long sleeve underlayer + track waistband + sneaker toe. |
| Living Water Underpass | C2-HERO | Post-rain underpass, two young-adult models walking through shallow flow, 28mm wide with slight dutch tilt and puddle reflections, cool top fill + tungsten practicals, oversized logo tee over long sleeve + track pants + technical trainers, ripples forming concentric geometry. |
| Living Water Underpass | C2-DETAIL | 50mm ground-level close-up, shoe heel cutting through water beside cuffed track pants, narrow top strip light with reflected fill, splash physics and wet/dry fabric transitions, embossed outsole micro text. |
| Geometry of Grace Rooftop | C3-HERO | Sunset rooftop with concrete prisms, single model posed monument-style, 40mm medium full-body with negative space, golden key + cool skyline bounce, oversized cream hoodie + logo tee + slate track pants + high-top sneakers, prism shadows forming geometric intersections. |
| Geometry of Grace Rooftop | C3-DETAIL | 70mm torso portrait, zipper half-open over logo tee with city bokeh, side key + silver bounce, rib grain and zipper highlights, stitched coordinates hidden under placket. |
| Silent Psalm Metro | C4-HERO | Late-night metro platform with subject sharp and crowd motion blur, 35mm centered full-body, softened fluorescents + warm ad-box rim, oversized long sleeve + wide track pants + monochrome sneakers, tile grid symbolism and subtle seam text. |
| Silent Psalm Metro | C4-DETAIL | 90mm macro bench detail, clasped hands over knee with hem labels and shoe quarter in focus, practical overhead + bounce card, twin-needle stitching and cotton fuzz, geometric perforation matrix in background. |
| Dawn Ascension Court | C5-HERO | Empty urban court at dawn, three-model reveal walk, 24mm wide symmetrical hero, soft dawn ambient + warm back rim, fleece hoodies + structured logo tees + nylon-blend track pants + mixed-material sneakers, line geometry and dew highlights. |
| Dawn Ascension Court | C5-DETAIL | 85mm shoulder-up dual portrait, one hood up one layered tee/long-sleeve, sunrise edge light, rib collars and micro print crack realism, halo arc flare and abstract pendant linework. |
| Nocturnal Refinement | C6-HERO | Luxury shopping district at night, model against brushed steel storefront, 50mm medium full-body off-center, tungsten key + cool street fill, black-on-black hoodie and track set with material contrast, reflected vertical path light and etched stone glyphs. |
| Nocturnal Refinement | C6-DETAIL | 65mm product close, folded long sleeve over hoodie with hero shoe on stone block and droplets, controlled softbox + kicker, knit thickness and outsole microtexture fidelity, stone-water-light triad composition. |

## Video Prompt Set (8 total)

### 1) Rooftop Halo Hoodie (10s)
- 0.0-2.0: low-angle close on hoodie hem, one step forward.
- 2.0-5.5: half-orbit to profile, subtle shoulder roll.
- 5.5-8.5: push-in to chest/logo zone.
- 8.5-10.0: hold on 3/4 profile.
- Camera: slow gimbal rise + orbit + micro push.
- Physics: hood edge flutter, sleeve drag, cotton settle.
- Light shift: cool dusk to warm rear rim bloom.

### 2) Platform Glide Track Pants (9s)
- 0.0-1.5: ground-level track on cuffs and shoes.
- 1.5-4.5: side tracking medium, waistband adjustment.
- 4.5-7.0: dolly-in with train light streaks.
- 7.0-9.0: stop-turn lock.
- Physics: nylon swish, cuff recoil, knee crease memory.

### 3) Asphalt Pulse Shoes (8s)
- 0.0-1.8: extreme close sole landing.
- 1.8-4.0: arc around both shoes during pivot.
- 4.0-6.5: subtle slow-motion heel-to-toe step.
- 6.5-8.0: static shoe hero lock.
- Physics: pant break compression/release over collar.

### 4) Studio Signal Logo Tee (7s)
- 0.0-2.0: medium frontal step into beam.
- 2.0-4.5: slow push to logo, hem adjustment.
- 4.5-6.0: slight pan as shoulder turns.
- 6.0-7.0: logo + jawline hold.
- Physics: chest tension, hem rebound, seam micro-wrinkles.

### 5) Stairwell Ascent Long Sleeve (11s)
- 0.0-2.5: rear follow climbing stairs.
- 2.5-5.5: side profile through rails.
- 5.5-8.5: top-down landing pause.
- 8.5-11.0: front medium lock at top.
- Physics: sleeve bunching, torso stretch/release.

### 6) Alley Drift Oversized Fit (12s)
- 0.0-3.0: wide entrance from deep background.
- 3.0-6.0: forward tracking medium-wide.
- 6.0-9.0: 180 orbit on torso turn.
- 9.0-12.0: portrait push with puddle foreground.
- Physics: oversized hem lag and layered settle.

### 7) Tunnel Set Full FTC Look (15s)
- 0.0-3.0: hero walk, second model defocused.
- 3.0-6.0: low-angle shoe/track sync step.
- 6.0-10.0: waist-up orbit on hoodie.
- 10.0-13.0: center stop, hands in pockets.
- 13.0-15.0: clean end-card lock.
- Physics: pocket compression and lace micro-motion.

### 8) Dawn Court Longline Reset (9s)
- 0.0-2.0: wide center-court establish.
- 2.0-4.5: push-in, one ball bounce then drop.
- 4.5-7.0: side profile walk.
- 7.0-9.0: chest-up sunrise rim hold.
- Physics: longline hem lag and collar settle.

## Audio Bed Templates (8 moods)

1. Midnight Flex (136 BPM, sparse 808 + reverse choir textures)  
2. Tunnel Pressure (140 BPM, metallic hits + sub drops)  
3. Luxury Menace (128 BPM, velvet strings + piano motifs)  
4. Neon Drift (132 BPM, reese bass + reverse textures)  
5. Rally Before the Drop (138 BPM, tension arc + halftime break)  
6. Cold Precision (126 BPM, minimal low-end tactical bed)  
7. Ascend Mode (134 BPM, rising ambient trap arc)  
8. Aftershock Credits (122 BPM, slow dark outro energy)  

Global audio constraints: no explicit profanity, no generic worship hooks, no lead singing, preserve a speech pocket around 1.5-4 kHz.

## Voice Hook Lines (<=10 words each)

1. Night mode on. FTC in full effect.  
2. Built for pressure, dressed like victory.  
3. No noise, just motion and intent.  
4. From silence to statement in one drop.  
5. Premium energy. Street pulse. Zero compromise.  
6. They hear the beat, then hear the brand.  
7. Dark room glow, headline-level confidence.  
8. Fast heart, clean message, heavy impact.  
9. Every frame hits. Every word lands.  
10. Young spirit, elite finish, all signal.  
11. Turn it up, keep it polished.  
12. FTC speaks once; the room remembers.  

## Transcription QA Checklist (8 items)

1. Voice sits clearly above bed.  
2. No ad-lib overlap on key words.  
3. Controlled speaking pace.  
4. Consonants remain sharp (s/t/k/p).  
5. No clipping/noise bursts.  
6. Brand terms pronounced consistently.  
7. Caption timestamps align to speech.  
8. Post-ASR review of names, numbers, and negations.  

## Rerank Rubric (100 points)

| Factor | Weight |
|---|---:|
| Brand safety compliance | 15 |
| First-3-second hook impact | 12 |
| Speech intelligibility in mix | 12 |
| Premium cinematic tone | 10 |
| Youth resonance (teen/YA) | 10 |
| Trap-adjacent fit | 9 |
| Transcription confidence | 8 |
| Editability for ad cuts | 8 |
| Emotional arc and momentum | 8 |
| Hook/CTA memorability | 8 |

Scoring method: `(factor_score / 5) * weight`, summed across all factors.
