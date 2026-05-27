"""GENESIS — collectible items.

Bible-rooted items (manna, scroll, oil-flask) and modern diaspora artifacts
(SmartTrip card, Old Bay shaker, danfo ticket). Each has a category, weight,
rarity, and a one-line lore.

Items are picked up in worlds (game/genesis/world_schema.py) and used to
unlock parables, build shelters, and earn favor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Category = Literal["food", "tool", "garment", "relic", "currency", "instrument", "scroll", "totem"]
Rarity = Literal["common", "uncommon", "rare", "sacred"]


@dataclass(frozen=True)
class Item:
    id: str
    name: str
    category: Category
    rarity: Rarity
    weight: int  # 0–10 — how much it slows the player
    world_id: str
    lore: str
    icon_palette: tuple[str, ...]


# ---------------------------------------------------------------------------
# BIBLICAL ITEMS
# ---------------------------------------------------------------------------

FIG_LEAF = Item("I-001", "Fig Leaf", "garment", "common", 1, "W-001",
                "What we sewed when we knew we were seen.", ("#3E5C42", "#88A37B", "#1A2A1F"))
RIVER_STONE = Item("I-002", "River Stone", "tool", "common", 2, "W-001",
                   "Smooth from a thousand years of being moved.", ("#6B6F5F", "#9B9C8A", "#C0C2B0"))
OLIVE_SPRIG = Item("I-003", "Olive Sprig", "totem", "uncommon", 1, "W-001",
                   "Dove brought it back. The flood admitted defeat.", ("#6E8270", "#B6BFA8", "#243126"))
FISHING_NET = Item("I-004", "Fishing Net", "tool", "common", 4, "W-002",
                   "Empty all night. Then full to breaking.", ("#3A5C66", "#8FA9AE", "#0F1416"))
WOODEN_OAR = Item("I-005", "Wooden Oar", "tool", "common", 5, "W-002",
                  "The teacher slept while we worked.", ("#704830", "#A88060", "#2A1E18"))
FIG = Item("I-006", "Ripe Fig", "food", "common", 1, "W-002",
           "Out of season but somehow there.", ("#5A3838", "#9C5050", "#3D2820"))
SALT_PINCH = Item("I-007", "Salt Pinch", "food", "common", 0, "W-002",
                  "You are this. Don't lose savor.", ("#FFFFFF", "#E0E0DA", "#888880"))
CLAY_CUP = Item("I-008", "Clay Cup", "relic", "uncommon", 2, "W-003",
                "From the cousin's house, fired in a small kiln.", ("#9B7A53", "#D8C09A", "#3D2F22"))
GRAIN_SACK = Item("I-009", "Grain Sack", "food", "common", 6, "W-003",
                  "Two weeks for the journey. One week after.", ("#A88060", "#D5B890", "#2A1E18"))
LAMP_OIL = Item("I-010", "Lamp Oil", "tool", "uncommon", 3, "W-003",
                "Five wise. Five foolish. Don't be foolish.", ("#C2A878", "#E8D8B0", "#3D2820"))
TEMPLE_COIN = Item("I-011", "Temple Coin", "currency", "uncommon", 0, "W-004",
                   "Render unto Caesar. Render unto God. Know the difference.", ("#7D6B4F", "#C9BFA0", "#2F2820"))
SCROLL_FRAGMENT = Item("I-012", "Scroll Fragment", "scroll", "rare", 1, "W-004",
                       "The line was: 'I am.' Then the parchment tore.", ("#EDE3CB", "#C9BFA0", "#15110C"))
RAM_HORN = Item("I-013", "Ram Horn", "instrument", "rare", 3, "W-005",
                "Caught in the thicket. Provided.", ("#A88860", "#C2C2B0", "#1F1A12"))
STONE_TABLET = Item("I-014", "Stone Tablet Piece", "relic", "sacred", 8, "W-005",
                    "The first set was broken. The second set still holds.", ("#6B6F5F", "#C0C2B0", "#11120D"))
MANNA_FLAKE = Item("I-015", "Manna Flake", "food", "uncommon", 0, "W-005",
                   "Enough for today. Don't hoard it.", ("#E8E9DB", "#C0C2B0", "#2C2E26"))
OLIVE_PIT = Item("I-016", "Olive Pit", "totem", "uncommon", 0, "W-006",
                 "From the press, where mercy and grief share a room.", ("#243126", "#6E8270", "#0E1410"))
LINEN_STRIP = Item("I-017", "Linen Strip", "garment", "rare", 1, "W-006",
                   "Left folded. Not taken.", ("#EBE6D2", "#B6BFA8", "#0E1410"))

# ---------------------------------------------------------------------------
# MODERN / DIASPORA ITEMS
# ---------------------------------------------------------------------------

TTC_DAY_PASS = Item("I-101", "TTC Day Pass", "currency", "common", 0, "W-101",
                    "Will get you to Pickering and back. Twice if you behave.",
                    ("#E4E6E5", "#6B7077", "#0E1417"))
SCARBOROUGH_PATTY = Item("I-102", "Jerk-Corner Patty", "food", "uncommon", 2, "W-101",
                         "Hot enough to burn the roof of your mouth, twice.",
                         ("#C09060", "#704830", "#1F1208"))
WINTER_MITT = Item("I-103", "Winter Mitt", "garment", "common", 3, "W-101",
                   "One always disappears. Always.", ("#2A3036", "#6B7077", "#B4B9BD"))
FREO_COFFEE_CUP = Item("I-104", "Fremantle Coffee Cup", "food", "common", 1, "W-102",
                       "Magic before 8 AM. Long black after.", ("#3A4A55", "#D2D8D0", "#0F1418"))
SWAN_RIVER_PEBBLE = Item("I-105", "Swan River Pebble", "totem", "uncommon", 1, "W-102",
                         "Black swan adjacent. Soft from tide.", ("#0F1418", "#3A4A55", "#94A7B0"))
BOAB_LEAF = Item("I-106", "Boab Leaf", "totem", "rare", 0, "W-102",
                 "From a tree older than the colony.", ("#3A4A55", "#94A7B0", "#D2D8D0"))
SMARTRIP_CARD = Item("I-107", "SmarTrip Card", "currency", "common", 0, "W-103",
                     "Tap. Then tap again because the first one didn't take.",
                     ("#2D353F", "#727B85", "#BCC1C7"))
HALF_SMOKE = Item("I-108", "Half-Smoke (Ben's)", "food", "uncommon", 2, "W-103",
                  "Onions, chili, mumbo sauce optional. Required if you're real.",
                  ("#704830", "#C09060", "#1F1208"))
GO_GO_TAPE = Item("I-109", "Go-Go Cassette", "instrument", "rare", 2, "W-103",
                  "Chuck Brown lives. The pocket is the city's heartbeat.",
                  ("#2D353F", "#727B85", "#0F1418"))
OLD_BAY = Item("I-110", "Old Bay Shaker", "food", "common", 1, "W-104",
               "On everything. Especially the things you didn't think.",
               ("#7C8A6E", "#BDC4AB", "#101511"))
CRAB_CLAW = Item("I-111", "Crab Claw", "totem", "uncommon", 2, "W-104",
                 "Steamed. Salted. Earned with a wooden mallet.",
                 ("#A88060", "#D5B890", "#2F3A2D"))
RAVENS_PIN = Item("I-112", "Ravens Pin", "totem", "common", 0, "W-104",
                  "Purple counts as a liturgical color, here.",
                  ("#3A2A50", "#7060A0", "#1F1530"))
DOLLAR_SLICE = Item("I-113", "Dollar Slice", "food", "common", 1, "W-105",
                    "Foldable. Honest. Available at 2 AM.",
                    ("#A88060", "#D5B890", "#2A1E18"))
SUBWAY_POEM_CARD = Item("I-114", "Subway Poem Card", "scroll", "uncommon", 0, "W-105",
                        "Six lines. Better than half the books you read.",
                        ("#0D1115", "#6F7782", "#E4E2DC"))
OYSTER_CARD = Item("I-115", "Oyster Card", "currency", "common", 0, "W-106",
                   "The 343 will accept it. The aunties will not.",
                   ("#11141A", "#2D343E", "#B0B6BE"))
JOLLOF_FOIL = Item("I-116", "Jollof Foil Tray", "food", "uncommon", 3, "W-106",
                   "Smoky bottom is mandatory.", ("#A88060", "#D5B890", "#1A1410"))
DANFO_TICKET = Item("I-117", "Danfo Ticket", "currency", "common", 0, "W-107",
                    "Hold tight. The conductor will find you.",
                    ("#9C7A55", "#D9C09C", "#1A1410"))
BALOGUN_FABRIC = Item("I-118", "Balogun Market Fabric", "garment", "rare", 4, "W-107",
                      "Asoebi-grade. Saved for a specific Saturday.",
                      ("#3D2F25", "#9C7A55", "#F3E8D0"))

ALL_ITEMS: tuple[Item, ...] = (
    FIG_LEAF, RIVER_STONE, OLIVE_SPRIG, FISHING_NET, WOODEN_OAR, FIG, SALT_PINCH,
    CLAY_CUP, GRAIN_SACK, LAMP_OIL, TEMPLE_COIN, SCROLL_FRAGMENT, RAM_HORN,
    STONE_TABLET, MANNA_FLAKE, OLIVE_PIT, LINEN_STRIP,
    TTC_DAY_PASS, SCARBOROUGH_PATTY, WINTER_MITT, FREO_COFFEE_CUP,
    SWAN_RIVER_PEBBLE, BOAB_LEAF, SMARTRIP_CARD, HALF_SMOKE, GO_GO_TAPE,
    OLD_BAY, CRAB_CLAW, RAVENS_PIN, DOLLAR_SLICE, SUBWAY_POEM_CARD,
    OYSTER_CARD, JOLLOF_FOIL, DANFO_TICKET, BALOGUN_FABRIC,
)


def items_in_world(world_id: str) -> tuple[Item, ...]:
    return tuple(i for i in ALL_ITEMS if i.world_id == world_id)


def item_by_id(item_id: str) -> Item | None:
    for i in ALL_ITEMS:
        if i.id == item_id:
            return i
    return None
