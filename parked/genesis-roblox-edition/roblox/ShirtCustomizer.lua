--!strict
-- ShirtCustomizer.lua
-- Server-side Roblox Luau module for FTC shirt customization.
-- See ./README.md for setup, decal upload, and integration steps.

local ShirtCustomizer = {}

----------------------------------------------------------------------------
-- Catalog
-- Each shirt corresponds to one FTC streetwear graphic (artifacts/graphics/*.svg).
-- After converting to PNG and uploading to Roblox, paste the asset ID below.
----------------------------------------------------------------------------

export type ShirtEntry = {
    id: string,
    name: string,
    palette: string,
    template_id: string,
    price_robux: number,
    unlock_condition: string?,
}

local FTC_SHIRT_CATALOG: { ShirtEntry } = {
    { id = "cornerstone",    name = "Cornerstone",    palette = "bone",        template_id = "rbxassetid://0", price_robux = 0,   unlock_condition = "default" },
    { id = "veil",           name = "Veil",           palette = "onyx",        template_id = "rbxassetid://0", price_robux = 0 },
    { id = "living-water",   name = "Living Water",   palette = "slate",       template_id = "rbxassetid://0", price_robux = 50 },
    { id = "ember",          name = "Ember",          palette = "rust",        template_id = "rbxassetid://0", price_robux = 50 },
    { id = "threshold",      name = "Threshold",      palette = "ash",         template_id = "rbxassetid://0", price_robux = 0 },
    { id = "covenant-arc",   name = "Covenant",       palette = "olive",       template_id = "rbxassetid://0", price_robux = 75 },
    { id = "manna",          name = "Manna",          palette = "linen",       template_id = "rbxassetid://0", price_robux = 75 },
    { id = "wilderness",     name = "Wilderness",     palette = "stone",       template_id = "rbxassetid://0", price_robux = 50 },
    { id = "still-waters",   name = "Still Waters",   palette = "slate",       template_id = "rbxassetid://0", price_robux = 75 },
    { id = "vine",           name = "True Vine",      palette = "cedar",       template_id = "rbxassetid://0", price_robux = 100 },
    { id = "ladder",         name = "Jacob's Ladder", palette = "stone",       template_id = "rbxassetid://0", price_robux = 100 },
    { id = "alabaster",      name = "Alabaster",      palette = "bone",        template_id = "rbxassetid://0", price_robux = 100 },
    { id = "broken-grid",    name = "Broken Grid",    palette = "onyx",        template_id = "rbxassetid://0", price_robux = 150 },
    { id = "mercy-seat",     name = "Mercy Seat",     palette = "camel",       template_id = "rbxassetid://0", price_robux = 150 },
    { id = "tabernacle",     name = "Tabernacle",     palette = "olive",       template_id = "rbxassetid://0", price_robux = 150 },
}

local CATALOG_BY_ID: { [string]: ShirtEntry } = {}
for _, entry in ipairs(FTC_SHIRT_CATALOG) do
    CATALOG_BY_ID[entry.id] = entry
end

----------------------------------------------------------------------------
-- Ownership tracking (in-memory; swap for DataStore in production)
----------------------------------------------------------------------------

local owned: { [number]: { [string]: boolean } } = {}

local function ensureOwnershipBucket(userId: number)
    if not owned[userId] then
        owned[userId] = {}
        -- Grant default unlocks
        for _, entry in ipairs(FTC_SHIRT_CATALOG) do
            if entry.unlock_condition == "default" or entry.price_robux == 0 then
                owned[userId][entry.id] = true
            end
        end
    end
end

----------------------------------------------------------------------------
-- Public API
----------------------------------------------------------------------------

function ShirtCustomizer.getCatalog(): { ShirtEntry }
    return FTC_SHIRT_CATALOG
end

function ShirtCustomizer.getEntry(shirtId: string): ShirtEntry?
    return CATALOG_BY_ID[shirtId]
end

function ShirtCustomizer.ownsShirt(player: Player, shirtId: string): boolean
    ensureOwnershipBucket(player.UserId)
    return owned[player.UserId][shirtId] == true
end

function ShirtCustomizer.applyShirt(player: Player, shirtId: string): boolean
    local entry = CATALOG_BY_ID[shirtId]
    if not entry then
        warn(string.format("[ShirtCustomizer] unknown shirt id: %s", shirtId))
        return false
    end
    if not ShirtCustomizer.ownsShirt(player, shirtId) then
        warn(string.format("[ShirtCustomizer] %s does not own %s — prompting purchase", player.Name, shirtId))
        return false
    end
    local character = player.Character
    if not character then return false end

    -- Remove existing shirt
    local existingShirt = character:FindFirstChildOfClass("Shirt")
    if existingShirt then existingShirt:Destroy() end

    local shirt = Instance.new("Shirt")
    shirt.Name = "FTC_Shirt"
    shirt.ShirtTemplate = entry.template_id
    shirt.Parent = character
    return true
end

-- Lets a player apply a custom-uploaded decal ID (requires GamePass in production)
function ShirtCustomizer.applyCustomTemplate(player: Player, templateAssetId: string): boolean
    local character = player.Character
    if not character then return false end
    local existingShirt = character:FindFirstChildOfClass("Shirt")
    if existingShirt then existingShirt:Destroy() end
    local shirt = Instance.new("Shirt")
    shirt.Name = "FTC_CustomShirt"
    shirt.ShirtTemplate = templateAssetId
    shirt.Parent = character
    return true
end

-- Grant a shirt to a player (called from MarketPlace purchase callbacks)
function ShirtCustomizer.grant(player: Player, shirtId: string)
    if not CATALOG_BY_ID[shirtId] then return end
    ensureOwnershipBucket(player.UserId)
    owned[player.UserId][shirtId] = true
end

-- Hook MarketplaceService.ProcessReceipt to this for paid shirts
function ShirtCustomizer.processReceipt(receiptInfo: { PlayerId: number, ProductId: number })
    -- In production: map ProductId -> shirtId via your DataStore
    -- For now: leaving as scaffold
    local player = game:GetService("Players"):GetPlayerByUserId(receiptInfo.PlayerId)
    if not player then return Enum.ProductPurchaseDecision.NotProcessedYet end
    -- Map ProductId -> shirtId (fill in after listing in MarketPlace)
    local productToShirt: { [number]: string } = {
        -- [123456789] = "covenant-arc",
    }
    local shirtId = productToShirt[receiptInfo.ProductId]
    if shirtId then
        ShirtCustomizer.grant(player, shirtId)
        return Enum.ProductPurchaseDecision.PurchaseGranted
    end
    return Enum.ProductPurchaseDecision.NotProcessedYet
end

return ShirtCustomizer
