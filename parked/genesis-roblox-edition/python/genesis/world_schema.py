"""GENESIS — world schema. Typed definitions of every world the player visits.

Each world has a biome (cedar/sand/marble/concrete/snow), a palette, a key
parable, and a list of collectibles. Worlds reference real geography
(Scarborough, Perth, Maryland) AND biblical geography (Eden, Galilee).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Biome = Literal[
    "cedar-forest",
    "desert-sand",
    "marble-city",
    "concrete-suburb",
    "snow-mountain",
    "olive-grove",
    "coastal-pier",
    "river-valley",
    "vineyard",
    "wheat-field",
    "rooftop-garden",
    "stone-courtyard",
]

WorldKind = Literal["biblical", "modern", "diaspora"]


@dataclass(frozen=True)
class World:
    id: str
    name: str
    kind: WorldKind
    biome: Biome
    palette: tuple[str, ...]
    region: str
    parable: str
    collectibles: tuple[str, ...]
    npcs: tuple[str, ...]
    coords_lat_lng: tuple[float, float] | None = None
    soundtrack_brief: str = ""


# ---------------------------------------------------------------------------
# BIBLICAL WORLDS
# ---------------------------------------------------------------------------

EDEN = World(
    id="W-001",
    name="Eden",
    kind="biblical",
    biome="cedar-forest",
    palette=("#1A2A1F", "#3E5C42", "#88A37B", "#D5DDB8", "#F3EEDB"),
    region="The First Garden",
    parable="What was given without asking is what we forget to thank for.",
    collectibles=("fig-leaf", "river-stone", "naming-card", "olive-sprig"),
    npcs=("the-gardener", "the-adversary", "first-named-bird"),
    soundtrack_brief="Cedar wind, river hush, distant unnamed birds.",
)

GALILEE = World(
    id="W-002",
    name="Galilee",
    kind="biblical",
    biome="coastal-pier",
    palette=("#0F1416", "#3A5C66", "#8FA9AE", "#D5D8C8", "#EFE9D4"),
    region="The Sea of Tiberias",
    parable="The boat tilts. The teacher sleeps. The storm is not the test.",
    collectibles=("fishing-net", "wooden-oar", "fig", "salt-pinch"),
    npcs=("the-fisherman", "the-teacher", "tax-collector"),
    soundtrack_brief="Water lapping wood, distant gulls, low wind.",
)

BETHLEHEM = World(
    id="W-003",
    name="Bethlehem",
    kind="biblical",
    biome="stone-courtyard",
    palette=("#1B1813", "#3D2F22", "#9B7A53", "#D8C09A", "#F2E8D2"),
    region="House of Bread",
    parable="Census in the dust. A door says no. A stable says yes.",
    collectibles=("clay-cup", "grain-sack", "lamp-oil", "wool-strand"),
    npcs=("the-innkeeper", "shepherd-boy", "magi-traveller"),
    soundtrack_brief="Sheep bells far off, low fire, swept stone.",
)

JERUSALEM = World(
    id="W-004",
    name="Jerusalem",
    kind="biblical",
    biome="marble-city",
    palette=("#15110C", "#2F2820", "#7D6B4F", "#C9BFA0", "#EDE3CB"),
    region="The City of Peace",
    parable="The temple curtain split top to bottom.",
    collectibles=("temple-coin", "broken-stone", "olive-oil-flask", "scroll-fragment"),
    npcs=("temple-keeper", "centurion", "weaver-of-veils"),
    soundtrack_brief="Distant Hebrew prayer, sandals on marble, brass.",
)

SINAI = World(
    id="W-005",
    name="Sinai",
    kind="biblical",
    biome="snow-mountain",
    palette=("#11120D", "#2C2E26", "#6B6F5F", "#C0C2B0", "#E8E9DB"),
    region="The Burning Mountain",
    parable="The bush is on fire but the wood does not burn.",
    collectibles=("flint-shard", "ram-horn", "stone-tablet-piece", "manna-flake"),
    npcs=("the-prophet", "the-priest", "the-aaron-figure"),
    soundtrack_brief="Wind across stone, ram horn, deep stillness.",
)

OLIVE_GROVE = World(
    id="W-006",
    name="Gethsemane",
    kind="biblical",
    biome="olive-grove",
    palette=("#0E1410", "#243126", "#6E8270", "#B6BFA8", "#EBE6D2"),
    region="The Garden of the Press",
    parable="The cup did not pass. The yes was harder than the cross.",
    collectibles=("olive-pit", "press-stone", "torch-stump", "linen-strip"),
    npcs=("the-sleeping-disciple", "the-soldier", "the-betrayer"),
    soundtrack_brief="Night insects, low whisper, single torch crackle.",
)


# ---------------------------------------------------------------------------
# MODERN WORLDS — diaspora cities (DMV / Maryland / Perth / Scarborough)
# ---------------------------------------------------------------------------

SCARBOROUGH = World(
    id="W-101",
    name="Scarborough",
    kind="modern",
    biome="concrete-suburb",
    palette=("#0E1417", "#2A3036", "#6B7077", "#B4B9BD", "#E4E6E5"),
    region="Ontario, Canada — the eastern suburbs of Toronto",
    parable="Bus-shelter prayer at 5:47 AM. The faithful keep their hours.",
    collectibles=("TTC-day-pass", "patty-from-jerk-corner", "winter-mitt", "church-bulletin"),
    npcs=("auntie-from-pickering", "uber-eats-cyclist", "tabla-teacher"),
    coords_lat_lng=(43.7764, -79.2318),
    soundtrack_brief="Bus engine idle, light snow, distant tabla and amapiano bleed.",
)

PERTH = World(
    id="W-102",
    name="Perth",
    kind="modern",
    biome="coastal-pier",
    palette=("#0F1418", "#3A4A55", "#94A7B0", "#D2D8D0", "#F3EEDC"),
    region="Western Australia — Indian Ocean coast",
    parable="The Indian Ocean does not negotiate. Walk earlier.",
    collectibles=("freo-coffee-cup", "swan-river-pebble", "boab-leaf", "sunburn-cream"),
    npcs=("dawn-swimmer", "boab-vendor", "scarborough-beach-busker"),
    coords_lat_lng=(-31.9505, 115.8605),
    soundtrack_brief="Surf, gulls, distant didgeridoo, no city traffic.",
)

DMV = World(
    id="W-103",
    name="DMV",
    kind="modern",
    biome="concrete-suburb",
    palette=("#10141A", "#2D353F", "#727B85", "#BCC1C7", "#E9E9E8"),
    region="DC · Maryland · Virginia — the corridor",
    parable="The metro is on time. The argument is older than the train.",
    collectibles=("smartrip-card", "half-smoke-receipt", "go-go-tape", "georgetown-leaf"),
    npcs=("howard-undergrad", "naval-yard-runner", "thai-spot-cashier"),
    coords_lat_lng=(38.9072, -77.0369),
    soundtrack_brief="Red Line braking, go-go bucket far off, Marvin Gaye through a brick wall.",
)

MARYLAND = World(
    id="W-104",
    name="Maryland",
    kind="modern",
    biome="river-valley",
    palette=("#101511", "#2F3A2D", "#7C8A6E", "#BDC4AB", "#EAE8D2"),
    region="Maryland — Chesapeake watershed, Baltimore, PG County",
    parable="The crab knows the tide. We forget what the water taught.",
    collectibles=("old-bay-shaker", "crab-claw", "natty-boh-cap", "ravens-pin"),
    npcs=("watermen-guide", "lexington-market-cook", "morgan-state-poet"),
    coords_lat_lng=(39.0458, -76.6413),
    soundtrack_brief="Crab boil steam, Bay water against pier, distant Baltimore club kick.",
)

BROOKLYN = World(
    id="W-105",
    name="Brooklyn",
    kind="modern",
    biome="rooftop-garden",
    palette=("#0D1115", "#2B313A", "#6F7782", "#B5BAC1", "#E4E2DC"),
    region="NYC — Bed-Stuy / Crown Heights / Brownsville",
    parable="Stoop is altar. Block is parish. Aunties are deacons.",
    collectibles=("dollar-slice", "subway-poetry-card", "domino-tile", "halal-cart-receipt"),
    npcs=("brownstone-elder", "bodega-cat-owner", "fulton-mall-tailor"),
    coords_lat_lng=(40.6782, -73.9442),
    soundtrack_brief="Brooklyn drill bass leaking, train rumble, distant gospel choir on Sunday.",
)

LONDON_SE = World(
    id="W-106",
    name="South London",
    kind="diaspora",
    biome="concrete-suburb",
    palette=("#11141A", "#2D343E", "#6E7682", "#B0B6BE", "#E2E2DD"),
    region="Peckham · Brixton · Lewisham",
    parable="The 343 bus carries more theology than most pulpits.",
    collectibles=("oyster-card", "jollof-foil-tray", "carnival-feather", "pentecostal-flyer"),
    npcs=("rye-lane-elder", "windrush-aunty", "estate-poet"),
    coords_lat_lng=(51.4750, -0.0750),
    soundtrack_brief="343 bus engine, distant church choir, rye-lane chatter, low UK rap kick.",
)

LAGOS_ISLAND = World(
    id="W-107",
    name="Lagos Island",
    kind="diaspora",
    biome="coastal-pier",
    palette=("#1A1410", "#3D2F25", "#9C7A55", "#D9C09C", "#F3E8D0"),
    region="Lagos, Nigeria — Eko",
    parable="Traffic is sermon. Patience is the only currency that holds value.",
    collectibles=("danfo-ticket", "balogun-fabric", "akara-paper", "fela-cassette"),
    npcs=("market-elder", "balogun-tailor", "yoruba-pastor"),
    coords_lat_lng=(6.4541, 3.3947),
    soundtrack_brief="Danfo horns, market call-and-response, Afrobeats from a corner stall.",
)


ALL_WORLDS: tuple[World, ...] = (
    EDEN, GALILEE, BETHLEHEM, JERUSALEM, SINAI, OLIVE_GROVE,
    SCARBOROUGH, PERTH, DMV, MARYLAND, BROOKLYN, LONDON_SE, LAGOS_ISLAND,
)


def world_by_id(world_id: str) -> World | None:
    for w in ALL_WORLDS:
        if w.id == world_id:
            return w
    return None


def worlds_by_kind(kind: WorldKind) -> tuple[World, ...]:
    return tuple(w for w in ALL_WORLDS if w.kind == kind)
