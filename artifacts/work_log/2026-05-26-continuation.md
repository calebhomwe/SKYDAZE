# 2026-05-26 — Continuation: master context, README, Eden vertical slice, +3 brands

Continued from `2026-05-26-graphics-game-mobile.md` after PR #8 merged.

## Inputs
User said "Continue" — picked the highest-leverage open work.

## What shipped

### 1. Repo root README
`README.md` rewritten from one-line stub → comprehensive map of the repo.
Includes: gallery link, file tour, architecture diagram, stack table, Makefile reference, 34-tier breakdown, security + secrets, license note.

### 2. FTC_MASTER_CONTEXT.md v2.3
Added sections 9-12:
- §9 — GENESIS GAME (worlds / characters / items / mechanics / monetization / liturgical calendar)
- §10 — MOBILE APP (tab list, provider routing, persistence, creator portal, push, bot detection)
- §11 — BRAND RESEARCH PROTOCOL (markdown only, 11-section dossier schema, refresh cadence)
- §12 — MULTI-PROVIDER IMAGE ROUTING (cost-ordered fallback, BG_BY_SECTION, circuit breaker)

Updated CLAUDE-USAGE block to route queries to new sections.

### 3. GENESIS Eden vertical slice in SwiftUI
First playable scene of the game, in three files:
- `mobile/ftc-ios/FTC/Genesis/GenesisModels.swift` — typed GenesisWorld + GenesisPlayer + GenesisItem
- `mobile/ftc-ios/FTC/Genesis/EdenScene.swift` — walking, item collection, restraint stat responds to walking cadence, parable overlay
- `mobile/ftc-ios/FTC/Genesis/GenesisRootView.swift` — world picker + navigation

Wired Genesis as a 5th tab in `ContentView.swift` (Generate / Gallery / Drops / **Genesis** / Creator).

Behaviors:
- Tap to walk. Slow walks (>1.2s between steps) increase restraint; rushes (<0.4s) decrease.
- Tap an item to pick up; player walks toward it first if out of reach.
- Inventory weight capped at 10. Items have their own weight.
- World title + parable overlay at top. Stats pill at bottom.
- Tree decorations using world palette.

### 4. Three more brand dossiers (markdown)
- `research/brands/STUSSY.md` — 45-year longevity + International Stüssy Tribe + chapter-store model + anti-marketing
- `research/brands/AIME_LEON_DORE.md` — closest sibling to FTC; place+product fusion, founder Substack, ALD Café, LVMH governance lesson
- `research/brands/CARHARTT_WIP.md` — stay-in-lane discipline, WIP Records music label, quarterly zine, subculture team

Master context §11 now lists 11 dossiers (was 8).

## Tracking
All markdown. Zero JSON output added.

## Next (optional)
- More brand dossiers: Mr. Porter (digital luxury merchandising), The Row (silent-luxury benchmark), Levi's (heritage cycling), Patta (Amsterdam diaspora streetwear), AWAKE NY (founder-led NYC).
- More GENESIS scenes: Galilee, Scarborough as next vertical slices in SwiftUI.
- Implement APNs configuration (Tier 33 / FTC-295).
- Wire ftc/concepts.py to also call DeepSeek v3.2 / Claude Sonnet 4.6 alternatives via the OpenRouter model fallback chain.
