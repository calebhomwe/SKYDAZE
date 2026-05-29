# GENESIS — Game Dev Playbook

> Notes and references for becoming an incredible indie game dev. Studied: Studio Ghibli backgrounds, Monument Valley, Sky: Children of the Light, Animal Crossing, Stardew Valley, Journey, GRIS, Florence.

## The thesis
GENESIS is **a slow, contemplative walking game where the player visits biblical worlds (Eden, Galilee, Bethlehem, Sinai, Gethsemane) and modern diaspora cities (Scarborough, Perth, DMV, Maryland, Brooklyn, Peckham, Lagos Island), collecting items and uncovering parables.** No combat. No skill trees. No scores. Restraint is the gameplay.

## Aesthetic ancestors

### Monument Valley (ustwo games, 2014)
**What to steal:**
- Pure isometric grid as primary view.
- Color palette of 5-7 tones maximum per level.
- Architecture as character — the buildings ARE the story.
- Soft ambient soundtrack, no music.
- Slow pacing — solving a puzzle takes 90 seconds, but feeling the level takes 5 minutes.
- M.C. Escher impossible geometry as a visual identity device.

**FTC translation:**
- Use the same isometric grid (already implemented in `game/genesis/mesh_renderer.py`).
- 5-tone palette per world (already implemented in `world_schema.py`).
- Architecture references real diaspora cities, not Escher.
- Soundtrack: field recordings + light ambient.

### Sky: Children of the Light (thatgamecompany, 2019)
**What to steal:**
- Multiplayer presence WITHOUT direct interaction (other players appear as silhouettes, you can help each other but not message).
- Movement as ritual: holding a candle, lighting another player's candle, gathering light.
- Cinematic camera angles that the player doesn't fully control.
- Seasonal content cycles — every 6 weeks a new "Season of X" rolls out.
- No HUD. The world IS the interface.

**FTC translation:**
- Silent multiplayer: other players appear as silhouettes carrying lamps (the Manna mechanic).
- Movement rituals: prayer at thresholds, kneeling at wells, walking the labyrinth.
- Cinematic camera at key moments (entering Eden, crossing the Sea of Galilee).
- Seasonal content tied to liturgical calendar: Advent season, Lent season, Easter season.
- No HUD. Inventory accessed via a single gesture.

### Journey (thatgamecompany, 2012)
**What to steal:**
- 2-hour total playtime per "playthrough" — short, complete, perfect.
- Color as narrative arc — red-orange-gold-blue across the journey.
- Movement as ballet — wind, momentum, sliding down dunes.
- Music: full orchestral, written for the game, won a Grammy.

**FTC translation:**
- Each world: 30-60 minutes of contemplative walking.
- Color arcs per world — Eden (green to gold), Sinai (white to grey to stone).
- Movement feels weighted — restraint is the central stat (low restraint = the player moves slowly).
- Music: ambient + field recordings, not orchestral. Composer recommendation: Nils Frahm-adjacent, plus liturgical strings (Arvo Pärt influence).

### Studio Ghibli backgrounds
**What to steal:**
- Background paintings are characters. Every leaf, every cloud, painted intentionally.
- Color theory: warm midtones, cool shadows, never pure black, never pure white.
- Composition: rule of thirds, depth via atmospheric perspective.
- Specific real-world references: Howl's Moving Castle = Alsace France; Spirited Away = Edo-era spa towns.

**FTC translation:**
- Background SVG mesh tiles painted with this care (already on path in `mesh_renderer.py`, can be enhanced).
- Atmospheric perspective via fog band at horizon (already implemented).
- Specific real-world references for each modern world (Scarborough TTC, Maryland Chesapeake, etc.) — keep adding specificity.

### Stardew Valley (ConcernedApe, 2016)
**What to steal:**
- Day/night cycle as core mechanic.
- NPC relationships built via small daily gestures.
- Player labor as meditation — fishing, farming, walking.
- Solo development possible — ConcernedApe built it alone over 4 years.

**FTC translation:**
- Day/night cycle in each world. Different parables available at different times.
- NPC relationships: each character has a daily routine. Talking to them at the right moment unlocks parable fragments.
- Player labor: building shelter from collected items, walking pilgrimage routes.
- Solo-dev feasible: SwiftUI + procedural SVG/PNG asset generation = small team or solo can ship.

### Animal Crossing: New Horizons (Nintendo, 2020)
**What to steal:**
- Real-time clock integration: the game time matches the player's actual time zone.
- Seasonal events: Halloween, Christmas, New Year actually happen in the game when they happen IRL.
- Customization without combat: terraforming, decorating, dressing.
- Social mechanics that feel personal without being competitive.

**FTC translation:**
- Real-time clock: Sunday mornings unlock specific content (a service in the modern worlds, a different NPC routine in biblical worlds).
- Liturgical calendar events: Advent unlocks the Bethlehem world to all players. Lent unlocks Gethsemane.
- Customization: outfit your character in FTC garments (cross-promo with the actual clothing brand).
- Social: see other players' shelters and items, leave them small gifts.

## The tech stack (proposed)

### Engine choice
**SwiftUI + Metal for iOS-first launch**, then port to:
- macOS (free with iOS via Catalyst)
- visionOS (Apple Vision Pro — perfect for contemplative-walking genre)
- iPad (free with iOS)

Why SwiftUI over Unity:
1. Single-developer friendly.
2. iOS-native performance (60fps locked).
3. SwiftUI Canvas + Metal shaders = enough graphical power for stylized 2.5D.
4. App Store distribution unified.
5. Already required for the FTC iPhone app — same toolchain, shared codebase.

### Asset pipeline
- **World tiles:** SVG generated by `game/genesis/mesh_renderer.py` → converted to PDF for Xcode → vector-clean at any resolution.
- **Characters:** SVG sprites with simple frame animation (2-3 frames per action).
- **Items:** SVG icons with tonal palette per world.
- **Backgrounds:** procedurally generated SVG that gets cached as PNG at retrieval.

### Persistence
- **CoreData** for save games (Apple-native, free).
- **iCloud sync** for cross-device continuity.
- **No backend required for v1.0** — single-player.

### Multiplayer (v2.0)
- **CloudKit** for silent multiplayer (Apple-native, free).
- Game Center for leaderboards (not needed — but available).

### Audio
- **AVAudioEngine** for layered ambient (one ambient bed per world + reactive layers).
- Field recordings from real diaspora cities.
- Sourced via Freesound.org (CC0) or commissioned from composer.

## Mechanics deep-dive

### The restraint stat
- Every player starts at restraint=5.
- Walking slowly through worlds increases restraint.
- Running, rushing, skipping dialogue decreases it.
- High restraint unlocks:
  - More parable fragments per NPC interaction.
  - Hidden items in worlds.
  - "Sabbath rest" — the game pauses with a soft visual when the player has played for 1 hour.

### The weight stat
- Items have weight.
- The player can only carry a few items at once.
- Choosing which to carry IS the gameplay.
- Some items are heavier than they look (the Stone Tablet from Sinai is weight 8).

### Parable unlocking
- Each NPC, when given the right item, shares a parable fragment.
- 5 fragments = 1 complete parable (written by FTC editorial team).
- 30 parables total across the game.
- Parables are READ, not voiced — text on screen, ambient audio underneath.

### Shelter building
- In each world, the player can build a small shelter from collected items.
- Shelter persists in iCloud — visible to other players who visit later.
- Other players can leave small gifts in your shelter (one item per visit, no messaging).

### The pilgrimage route
- 13 worlds connected via "thresholds."
- Walking from Eden to Galilee to Bethlehem to Jerusalem to Sinai forms a pilgrimage.
- Modern diaspora worlds are entered via "remembrance gates" — the player can walk from Bethlehem to DMV (the connection: Bethlehem = "house of bread"; DMV's Ben's Chili Bowl is the house of half-smokes).
- Completing the full pilgrimage = the credits.

## Monetization (intentionally restrained)

**Free download.** First 3 worlds (Eden, Galilee, Scarborough) free.

**One-time IAP unlocks:**
- "Biblical Worlds Pack" — Bethlehem, Jerusalem, Sinai, Gethsemane: $4.99
- "Diaspora Worlds Pack" — Perth, DMV, Maryland, Brooklyn, Peckham, Lagos Island: $4.99
- "Complete Pilgrimage" — both packs + future seasonal worlds: $11.99

**Seasonal content (free for owners):**
- Advent season (December) — Bethlehem expands.
- Lent season (Feb-March) — Gethsemane expands.
- Easter season (April) — Jerusalem expands.
- Harvest (October) — Maryland expands.

**No ads. No microtransactions. No loot boxes.**

## Studios to model

| Studio | Lesson |
| :--- | :--- |
| thatgamecompany | Slow contemplative design ethic |
| ustwo games | Visual polish on small scope |
| Annapurna Interactive | Publishing model for artful games |
| Mobius Digital | Small-team excellence (Outer Wilds) |
| ConcernedApe | Solo-dev possibility (Stardew Valley) |
| Hidetaka Miyazaki / FromSoftware | "Difficulty as honesty" — though FTC inverts this |
| Studio Ghibli | Background painting as character |

## Resources to learn from

### Books
- *The Art of Game Design* by Jesse Schell
- *A Theory of Fun for Game Design* by Raph Koster
- *Designing Games* by Tynan Sylvester

### Talks
- Jenova Chen (thatgamecompany) — "Designing Journey" (GDC 2013)
- Ken Wong (Monument Valley) — "Monument Valley: Art for Apps" (GDC 2014)
- ConcernedApe — Stardew Valley postmortem
- Jonathan Blow — "Designing to Reveal the Nature of the Universe" (Indiecade East 2014)

### SwiftUI + Metal for game dev
- WWDC 2020 — "Build SwiftUI views for widgets" + "Use Metal in SwiftUI"
- *SwiftUI by Example* by Hacking with Swift
- *Metal Programming Guide* (Apple docs)

### Audio design
- *The Sound of Sky* — devlog on Sky's audio system (medium.com/sky-cotl-dev)
- Nils Frahm — *Spaces* (album) — for the ambient bed reference
- Arvo Pärt — *Tabula Rasa* — for liturgical string reference

## Production roadmap

### Q1-Q2 2026 — Prototype
- World renderer: ✅ done (SVG mesh)
- Character/items: ✅ schema done
- Single-player walking in one world (Eden) — Swift implementation
- Asset pipeline: SVG → PDF → Xcode Asset Catalog

### Q3 2026 — Vertical Slice
- 3 worlds playable (Eden, Galilee, Scarborough)
- Walk + collect + NPC interaction + 1 parable per world
- Day/night cycle
- iCloud save

### Q4 2026 — Alpha
- All 13 worlds renderable
- Pilgrimage path connecting them
- 30 parables fully written
- Audio for each world
- TestFlight beta with 50 invited players (FTC creator program)

### Q1 2027 — Beta
- Public TestFlight (500 invited)
- Multiplayer (silent presence, gifting)
- Liturgical calendar integration
- App Store review submission

### Q2 2027 — Launch
- Day-one: free download + IAP packs
- Cross-promo with FTC iPhone shopping app (shared brand, shared aesthetic)
- Apple Arcade pitch (alternative monetization if Apple offers)

## TL;DR — the one-line synthesis
**GENESIS is a contemplative walking game where the player visits 13 worlds — 6 biblical, 7 diaspora — collecting items and unlocking parables, built solo or in a small team using SwiftUI + Metal, monetized via one-time IAP packs, and designed to be played the way FTC garments are worn: slowly, intentionally, with restraint as the central virtue.**
