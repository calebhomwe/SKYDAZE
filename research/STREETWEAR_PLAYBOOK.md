# FTC STREETWEAR PLAYBOOK
> Synthesis of Yeezy, Off-White, Nike, Pinterest, Proper, Geedup, BoohooMAN, Fashion Nova. The rules FTC plays by — what we steal, what we invert, what we refuse.

## The thesis (one paragraph)
FTC is **the editorial discipline of Proper, the silhouette obsession of Yeezy, the sub-brand architecture of Nike, the hyper-local specificity of Geedup, the mobile UX speed of BoohooMAN/Fashion Nova, and the creator-seeding scale of Fashion Nova — fused to a Christian theological core that none of these brands have, and converted into a luxury price point ($80-480) defended by 5-10x physical quality over fast-fashion peers.** Restraint is the brand.

## The 10 commandments (drilled from 8 brand studies)

### 1. Restraint reads louder than logos
- Yeezy / Lemaire / The Row / Margiela — all win at high price points with zero front-of-garment branding.
- FTC: tonal embroidery, blind emboss, interior labels only. No logo on front of any garment, ever.

### 2. Silhouette is identity
- Yeezy's elongated torsos. Nike's Air Force 1. Off-White's deconstructed seams.
- FTC must own 1 silhouette in each category: tracksuit, outerwear, tee, accessory. By drop 5, customers should recognize an FTC garment by its cut from across the street.

### 3. Five-tone palette per drop, no exceptions
- Yeezy / Proper / Lemaire all run tight 5-tone earth-neutral palettes per season.
- FTC: bone, ash, slate, oxidized rust, onyx (variant per drop). Saturation cap 0.55. No primaries. Ever.

### 4. Materials specificity is the price defense
- Proper teaches the reader: GSM, loopback, garment-washed, made-in-X.
- FTC PDPs must match: "320gsm garment-washed Japanese loopback cotton" beats "premium quality."

### 5. Hyper-local diaspora specificity is the cultural moat
- Geedup's Western Sydney. Aimé Leon Dore's Queens. Stüssy's Laguna Beach.
- FTC's: DMV go-go, Scarborough TTC, Maryland Old Bay, Perth Indian Ocean, Lagos Balogun, Peckham 343 bus. References by name, route, dish, BPM.

### 6. Drop scarcity discipline — defend by saying no
- Yeezy / Supreme / Geedup all do one-run scarcity.
- FTC: limited runs, no restocks, defend the brand by saying no. Markdown protection in wholesale terms.

### 7. Editorial-first marketing
- Proper's quarterly magazine. Aimé Leon Dore's "Friends" essays. Nike's "Find Your Greatness" campaigns.
- FTC: Substack → quarterly print magazine by year 3. Long-form designer interviews twice per drop. Brand voice: specific, skeptical, monastic-grave.

### 8. Creator-seeding > celebrity ads
- Fashion Nova's 2,000+ creators. Nike's 100+ athlete contracts.
- FTC: 100 seeded creators per quarter (faith-aligned, vetted), 10 ambassadors per year, 8-12% commission tier, auto-tracked through iPhone app.

### 9. Mobile UX speed without mobile-UX ethics
- BoohooMAN / Fashion Nova sub-second image loads, 2-tap checkout.
- FTC iPhone app matches that speed, inverts the urgency tactics. No crossed-out pricing. No countdown clocks. Story-first product view.

### 10. Sincerity is the deepest moat
- Off-White winked. Supreme winked. FTC cannot wink.
- The Christian theological foundation must be ambient, never preached, but always present. Faith lives in the construction, not the slogan.

## Color systems summary (across all brands)

| Brand | Saturation cap | Primary palette | Best 3 colors to lift |
| :--- | ---: | :--- | :--- |
| Yeezy | 0.35 | Sand / bone / mocha / ash / onyx | `#E5DCC5`, `#A88B6E`, `#15110D` |
| Off-White | 1.0 (avoid) | Black / white / safety orange | `#0E0D0C`, `#EFE9D8` (only) |
| Nike (ACG) | 0.55 | Olive / earth / charcoal | `#5A5840`, `#8A7E5C`, `#3D3B36` |
| Proper | 0.45 | Navy / olive / brown / ecru | `#2D3540`, `#5A6248`, `#E8E2D0` |
| Geedup | 0.50 | Sun-faded navy / washed olive / dusty terracotta | `#2D3540`, `#5A6248`, `#7A4538` |
| Lemaire (ref) | 0.40 | Camel / cream / charcoal | `#A88B6E`, `#E8E2D0`, `#3D3B36` |

**FTC blended palette** (drop 1 — "Cornerstone"):
- `#15110D` — Onyx
- `#5A5840` — Olive Ash
- `#A88B6E` — Camel Bone
- `#D5CFB8` — Sand Linen
- `#EFE9D8` — Bone

Saturation cap: **0.55** (locked in `ftc/colors.py`).

## Typography systems summary

| Brand | Primary face | Use |
| :--- | :--- | :--- |
| Yeezy | None visible on garments | Identity through material, not type |
| Off-White | Helvetica Bold + quotation marks | Brand mark + everything |
| Nike | Futura Bold / Trade Gothic | Headers + product names |
| Proper | Genath-like modern serif + Helvetica | Editorial + nav |
| Geedup | Custom bold serif | Wordmark, sometimes arched |
| Lemaire (ref) | Custom serif (almost calligraphic) | Wordmark |

**FTC typography lock-in:**
- **Display:** custom humanist serif (commission by drop 3 — until then, **Caslon Pro** or **Genath**)
- **Body:** **Inter** or **Founders Grotesk** (grotesque, low contrast)
- **Mono:** **JetBrains Mono** (for SKU codes, tech labels)
- **No display faces.** No blackletter. No script. No novelty.
- **Tracking:** 4-6% on uppercase titles. 0% on body.
- **Size:** garment type at 8-10pt (interior labels), editorial titles at 22pt, body at 14-16pt.

## Operational benchmarks (extracted from all 8)

| Metric | BoohooMAN | Fashion Nova | Yeezy | Proper | Nike | FTC target |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| SKUs live at any time | 12,000+ | 8,000+ | 80-120 per season | 200 curated | 100k+ | 60-100 |
| Concept-to-ad-live | 36 hours | 48 hours | 6 months | 8 weeks | 4-12 weeks | 5-7 days |
| Return rate | 30% | 25% | 12% | 5% | 14% | <8% |
| Customer LTV | £90 | $120 | $1,200 | $4,000 | $500 | $800-1,500 |
| Repeat at 90 days | 40% | 45% | 60% | 75% | 55% | 60% |
| Drop scarcity | None | None | Strong | Soft (curated) | Strong (collabs) | Strong |
| Mobile load <1s | Yes | Yes | Slow | Slow | Yes | **Required** |
| Creator program | Some | 2,000+ | None | None | 100+ athletes | 100/quarter |

## Sub-brand architecture (lifted from Nike)

FTC sub-line proposal:
1. **FTC HERITAGE** — the main line. Tracksuit / outerwear / tee / accessory.
2. **FTC SANCTUM** — limited religious/liturgical pieces (Easter capsule, Christmas, Advent).
3. **FTC MOVEMENT** — athletic-influenced for the campus/gospel-rap crowd.
4. **FTC ARCHIVE** — annual re-issue of year-1 drops in refined materials (year 5+).

Each sub-line shares:
- 5-tone palette discipline (different palette per sub-line, all under saturation cap)
- Same typography system
- Same theological core
- Same restraint posture

Each sub-line has its own:
- Silhouette family
- Material weight band
- Drop frequency
- Customer segment

## Product photography spec (synthesized)

**The 8-shot package** for every garment:
1. Hero — front, model in real backdrop, available light, 2:3 vertical.
2. Hero alt — back, same model, same setting.
3. Silhouette — flat-lay or hanger, on bone-or-onyx backdrop.
4. Material macro — hand-on-fabric, single fiber visible at this scale.
5. Construction detail — seam, label, embroidery, deboss.
6. Editorial mid-effort — model moving, breath visible.
7. Architectural — garment in environment (church interior, brutalist building, north window).
8. Drape rest — garment alone on a chair, sofa, doorway.

Backdrop discipline:
- **Hero + alt:** real interior (never cyclorama).
- **Silhouette:** **alternating black or white backdrop per section** (user's request).
- **Material macro:** zoom level so fabric weave is visible.
- **Construction:** zoom on a single technical detail.
- **Editorial:** real environment.
- **Architectural:** archival-grade location (research the location for each drop).
- **Drape rest:** soft natural light.

## The 12-month operational playbook

### Months 1-3 (Q1 — Genesis Drop)
- Cornerstone Drop launches.
- 100 creators seeded (10 high-tier).
- iPhone app v1.0 in TestFlight (private beta).
- Substack launches with 3 long-form pieces.

### Months 4-6 (Q2 — Wilderness Drop)
- iPhone app v1.1 with Creator Portal.
- First Pinterest Shop integration.
- First gospel-rap artist collab (Lecrae / Hulvey / KB tier).

### Months 7-9 (Q3 — Harvest Drop)
- Wholesale pitches to 20 boutiques (DSM, SSENSE, MoMA Design Store).
- First trade show (PROJECT or Liberty).
- Quarterly editorial brief sent to all 100 creators.

### Months 10-12 (Q4 — Advent Drop)
- Advent capsule (FTC SANCTUM sub-line launch).
- Year-end Substack essay.
- Year-1 sell-through analysis → year-2 plan.

## The forbidden moves (from all 8 brand studies)
1. Logos on the front of garments.
2. Neon or saturated primaries.
3. Blackletter typography (Geedup cautionary).
4. Crossed-out pricing or % off sales.
5. Influencers under 18.
6. Knock-off designs.
7. Polyester-heavy garments.
8. Sub-200gsm fabric.
9. Trend-chasing without authorial filter.
10. Irony / wink-at-itself voice.
11. Provocation marketing (Yeezy cautionary).
12. Mass-market scale dilution (Nike cautionary).

## The required moves
1. 5-10x peer fabric weight + price defense.
2. Tonal embroidery / blind emboss only.
3. 5-tone earth-neutral palette per drop.
4. Editorial Substack + quarterly magazine roadmap.
5. iPhone app as primary customer touchpoint (Nike SNKRS model).
6. 100-creator quarterly seeding (faith-aligned vetting).
7. Hyper-local diaspora specificity in every campaign.
8. Drop scarcity, no restocks, markdown protection.
9. Materials lexicon in every PDP.
10. Sincerity over irony in every line of copy.

## TL;DR — the one-line synthesis
**FTC sells restraint at luxury price, defended by craft, propagated by faith-aligned creators, delivered through a fast mobile app with story-first product viewing — to a global Christian diaspora that already knows what it wants and is tired of being talked down to.**
