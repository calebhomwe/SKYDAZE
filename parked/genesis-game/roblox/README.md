# Roblox shirt customization — FTC scaffold

> Drop this into a Roblox experience to let players customize shirts using FTC-themed templates. Engine: Roblox Studio + Luau.

## How Roblox shirts work (90-second version)

1. Roblox has two clothing types: `Shirt` and `Pants`. Each takes a `ShirtTemplate` / `PantsTemplate` property holding a `rbxassetid://...` URL.
2. The template is a 585×559 px PNG that wraps the avatar's torso + arms via a fixed UV layout.
3. Pants templates are 585×257 px (legs) — or 585×559 with the bottom half empty.
4. To use a custom design: upload the PNG to Roblox (Create → Asset Manager → Import → Shirt), get an asset ID back, set `shirt.ShirtTemplate = "rbxassetid://<ID>"`.
5. Roblox charges Robux to upload clothing (~10 R$ per asset). MarketPlace sales return ~70%.

## Files in this directory

- `ShirtCustomizer.lua` — server-side Lua. Catalog of FTC-themed shirts + the "apply to player" function.
- `ShirtTemplate-blank.png` (optional, generate locally) — the 585×559 UV layout reference.
- This `README.md`.

## Convert FTC graphics to Roblox decals

From the repo root:

```bash
# Install cairosvg if missing (handles SVG → PNG conversion)
pip install cairosvg

# Convert each FTC graphic to a 585x559 PNG suitable for Roblox shirts
python3 - <<'PY'
from pathlib import Path
import cairosvg
src = Path('artifacts/graphics')
dst = Path('parked/genesis-game/roblox/shirt-decals')
dst.mkdir(parents=True, exist_ok=True)
for svg in sorted(src.glob('*.svg')):
    out = dst / (svg.stem + '.png')
    cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=585, output_height=559)
    print('->', out)
PY
```

Then in Roblox Studio:
1. Asset Manager → Bulk Import → select the PNGs.
2. For each, set Asset Type = "Shirt".
3. Copy the asset IDs.
4. Paste them into the `FTC_SHIRT_CATALOG` table in `ShirtCustomizer.lua`.

## Catalog structure

The Lua script stores shirts as:

```lua
{
    id = "cornerstone",
    name = "Cornerstone",
    palette = "bone",
    template_id = "rbxassetid://0",  -- replace with real ID after upload
    price_robux = 0,                 -- 0 = free, >0 = paid
}
```

## Usage in your game

```lua
local Customizer = require(script.ShirtCustomizer)

-- Apply a shirt to a player
game.Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(character)
        wait(0.5)
        Customizer.applyShirt(player, "cornerstone")
    end)
end)

-- Show a selection UI (your own UI — Customizer exposes the catalog)
local catalog = Customizer.getCatalog()
for _, entry in ipairs(catalog) do
    print(entry.name, entry.price_robux, "R$")
end

-- Let a player apply their own uploaded shirt
Customizer.applyCustomTemplate(player, "rbxassetid://1234567890")
```

## Monetization path

1. **Free shirts:** include the FTC streetwear catalog as free items players unlock by reaching specific in-game milestones (visited 5 worlds, completed first parable, etc).
2. **Premium shirts:** seasonal Roblox-exclusive variants — 50-150 R$ each. Roblox takes 30%; the remaining ~70% comes back as DevEx → USD.
3. **Custom upload tier:** the GamePass that unlocks `applyCustomTemplate` — 200-500 R$ one-time.

## Compliance notes

- Roblox prohibits trademark infringement on uploaded clothing. FTC originals are fine; do not upload Yeezy / Off-White / Nike screenshots.
- Robux earnings convert to USD via DevEx at ~0.0035 USD per Robux (subject to change).
- Roblox requires you to be 13+ to upload clothing.
- Clothing assets undergo a moderation review before going live (usually 24-48 hours).

## Suggested integration order

1. **Week 1:** Upload 5-10 FTC streetwear graphics as Roblox shirts (free).
2. **Week 2:** Wire `ShirtCustomizer.lua` into a simple lobby experience. Test on Studio + mobile + console.
3. **Week 3:** Build the selection UI (Roblox ScreenGui). Add the world-tile concept art as backdrop scenes.
4. **Week 4:** Soft launch with a small invited group (Discord, the FTC creator program).
5. **Month 2:** Add premium shirts behind GamePass + custom-upload tier.

## Why this matters

Roblox has 70M+ daily active users, many in the 13-25 demo the FTC brand targets. A Roblox experience that lets players wear FTC shirts in-world is:
- Free user-acquisition for the real-world brand.
- Low marginal cost — the shirts are pixels, not garments.
- A clear bridge from the diaspora-Christian online culture to the streetwear brand.
- A way for kids who can't afford a $160 hoodie to still belong to FTC.

This is the cheapest brand-extension move in the entire 5-year plan. Worth doing.
