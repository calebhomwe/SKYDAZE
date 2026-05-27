"""GENESIS — playable characters and NPCs.

Biblical figures rendered as Bible-game characters with stats. Modern NPCs
from the diaspora cities (Scarborough, Perth, DMV, Maryland). Each has a
typed schema: name, kind, role, stats, world_id, signature_phrase.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CharacterKind = Literal["biblical", "modern", "spirit"]
Role = Literal["builder", "shepherd", "scribe", "fisher", "watchman", "host", "elder", "guide"]


@dataclass(frozen=True)
class Stats:
    restraint: int   # 0–10 — how slowly they move; high = patient
    weight: int      # 0–10 — what they can carry; high = sturdy
    sight: int       # 0–10 — perception of unseen
    voice: int       # 0–10 — power of spoken word
    mercy: int       # 0–10 — willingness to forgive


@dataclass(frozen=True)
class Character:
    id: str
    name: str
    kind: CharacterKind
    role: Role
    world_id: str
    stats: Stats
    signature_phrase: str
    sprite_palette: tuple[str, ...]  # used by sprite_renderer.py


# ---------------------------------------------------------------------------
# BIBLICAL CHARACTERS
# ---------------------------------------------------------------------------

ADAM = Character(
    id="C-001", name="Adam", kind="biblical", role="builder", world_id="W-001",
    stats=Stats(restraint=5, weight=8, sight=7, voice=6, mercy=5),
    signature_phrase="She is bone of my bone.",
    sprite_palette=("#3E2E22", "#88684A", "#D5C29A", "#3E5C42"),
)

EVE = Character(
    id="C-002", name="Eve", kind="biblical", role="host", world_id="W-001",
    stats=Stats(restraint=4, weight=6, sight=9, voice=8, mercy=8),
    signature_phrase="I have gotten a man with the help of the Lord.",
    sprite_palette=("#4A2E22", "#A06848", "#E2C29A", "#88A37B"),
)

NOAH = Character(
    id="C-003", name="Noah", kind="biblical", role="builder", world_id="W-002",
    stats=Stats(restraint=9, weight=10, sight=7, voice=4, mercy=6),
    signature_phrase="The Lord shut him in.",
    sprite_palette=("#2E1E14", "#704830", "#C29870", "#1B3138"),
)

ABRAHAM = Character(
    id="C-004", name="Abraham", kind="biblical", role="guide", world_id="W-005",
    stats=Stats(restraint=8, weight=7, sight=9, voice=7, mercy=7),
    signature_phrase="The Lord will provide.",
    sprite_palette=("#2A1A10", "#684030", "#B58A60", "#5E5340"),
)

MOSES = Character(
    id="C-005", name="Moses", kind="biblical", role="scribe", world_id="W-005",
    stats=Stats(restraint=7, weight=8, sight=10, voice=6, mercy=8),
    signature_phrase="Here am I.",
    sprite_palette=("#1F1A12", "#5A4830", "#A88860", "#C2C2B0"),
)

DAVID = Character(
    id="C-006", name="David", kind="biblical", role="shepherd", world_id="W-004",
    stats=Stats(restraint=6, weight=7, sight=8, voice=9, mercy=7),
    signature_phrase="The Lord is my shepherd.",
    sprite_palette=("#1F1A10", "#684A30", "#C2A878", "#7D6B4F"),
)

MARY = Character(
    id="C-007", name="Mary", kind="biblical", role="host", world_id="W-003",
    stats=Stats(restraint=10, weight=6, sight=10, voice=8, mercy=10),
    signature_phrase="Let it be unto me according to your word.",
    sprite_palette=("#2A1E18", "#7A5A40", "#D5B890", "#3D2F22"),
)

JOSEPH = Character(
    id="C-008", name="Joseph of Nazareth", kind="biblical", role="builder", world_id="W-003",
    stats=Stats(restraint=10, weight=10, sight=8, voice=4, mercy=9),
    signature_phrase="He arose and took the child and his mother by night.",
    sprite_palette=("#2A1E18", "#5C4030", "#A88060", "#9B7A53"),
)

PETER = Character(
    id="C-009", name="Peter", kind="biblical", role="fisher", world_id="W-002",
    stats=Stats(restraint=3, weight=9, sight=6, voice=10, mercy=8),
    signature_phrase="Depart from me, for I am a sinful man.",
    sprite_palette=("#1F1812", "#4A3828", "#8FA9AE", "#704A30"),
)

MARY_MAGDALENE = Character(
    id="C-010", name="Mary of Magdala", kind="biblical", role="watchman", world_id="W-004",
    stats=Stats(restraint=8, weight=6, sight=10, voice=8, mercy=10),
    signature_phrase="I have seen the Lord.",
    sprite_palette=("#1F1812", "#5A3828", "#B58060", "#7D6B4F"),
)

JESUS = Character(
    id="C-011", name="The Teacher", kind="biblical", role="guide", world_id="W-002",
    stats=Stats(restraint=10, weight=10, sight=10, voice=10, mercy=10),
    signature_phrase="Come, follow me.",
    sprite_palette=("#1A1208", "#604628", "#C29870", "#E8D8B0"),
)

# ---------------------------------------------------------------------------
# MODERN / DIASPORA CHARACTERS
# ---------------------------------------------------------------------------

SCARBOROUGH_AUNTIE = Character(
    id="C-101", name="Auntie Marlene", kind="modern", role="elder", world_id="W-101",
    stats=Stats(restraint=8, weight=7, sight=9, voice=10, mercy=9),
    signature_phrase="You eat first. Then we talk.",
    sprite_palette=("#1F1812", "#3E2A20", "#704830", "#D5BFA0"),
)

PERTH_DAWN_SWIMMER = Character(
    id="C-102", name="Em from Cottesloe", kind="modern", role="watchman", world_id="W-102",
    stats=Stats(restraint=9, weight=6, sight=10, voice=4, mercy=7),
    signature_phrase="The water tells you when.",
    sprite_palette=("#1F2428", "#3A5A6A", "#94A7B0", "#F3EEDC"),
)

DMV_RUNNER = Character(
    id="C-103", name="Jelani", kind="modern", role="watchman", world_id="W-103",
    stats=Stats(restraint=7, weight=7, sight=8, voice=6, mercy=7),
    signature_phrase="Six AM is its own theology.",
    sprite_palette=("#10141A", "#2D353F", "#727B85", "#BCC1C7"),
)

MARYLAND_WATERMAN = Character(
    id="C-104", name="Cap'n Earl", kind="modern", role="fisher", world_id="W-104",
    stats=Stats(restraint=10, weight=10, sight=10, voice=5, mercy=8),
    signature_phrase="Bay don't lie. Tide don't apologize.",
    sprite_palette=("#101511", "#2F3A2D", "#7C8A6E", "#BDC4AB"),
)

BROOKLYN_ELDER = Character(
    id="C-105", name="Mr. Eli", kind="modern", role="elder", world_id="W-105",
    stats=Stats(restraint=9, weight=7, sight=9, voice=9, mercy=10),
    signature_phrase="The stoop knows your name before you do.",
    sprite_palette=("#0D1115", "#2B313A", "#6F7782", "#B5BAC1"),
)

PECKHAM_ELDER = Character(
    id="C-106", name="Brother T", kind="modern", role="elder", world_id="W-106",
    stats=Stats(restraint=8, weight=7, sight=8, voice=10, mercy=9),
    signature_phrase="The 343 carries more theology than most pulpits.",
    sprite_palette=("#11141A", "#2D343E", "#6E7682", "#B0B6BE"),
)

LAGOS_TAILOR = Character(
    id="C-107", name="Mama Bisi", kind="modern", role="host", world_id="W-107",
    stats=Stats(restraint=7, weight=8, sight=9, voice=10, mercy=10),
    signature_phrase="Patience is the cloth. Stitches are the proof.",
    sprite_palette=("#1A1410", "#3D2F25", "#9C7A55", "#D9C09C"),
)

ALL_CHARACTERS: tuple[Character, ...] = (
    ADAM, EVE, NOAH, ABRAHAM, MOSES, DAVID, MARY, JOSEPH, PETER, MARY_MAGDALENE, JESUS,
    SCARBOROUGH_AUNTIE, PERTH_DAWN_SWIMMER, DMV_RUNNER, MARYLAND_WATERMAN,
    BROOKLYN_ELDER, PECKHAM_ELDER, LAGOS_TAILOR,
)


def character_by_id(cid: str) -> Character | None:
    for c in ALL_CHARACTERS:
        if c.id == cid:
            return c
    return None


def characters_in_world(world_id: str) -> tuple[Character, ...]:
    return tuple(c for c in ALL_CHARACTERS if c.world_id == world_id)
