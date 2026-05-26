#!/usr/bin/env python3
"""Procedural LUMENFALL chart generator — dual-plane tap/hold/arc/flick."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHART_DIR = ROOT / "data" / "charts"


def beat_ms(bpm: float, beat: float, offset_ms: float = 800.0) -> int:
    return int(round(offset_ms + (60_000.0 / bpm) * beat))


def generate(
    chart_id: str,
    title: str,
    difficulty: str,
    bpm: float,
    note_count: int,
    *,
    seed: int | None = None,
    sky_ratio: float = 0.35,
) -> dict:
    rng = random.Random(seed if seed is not None else hash(chart_id) & 0xFFFF)
    notes: list[dict] = []
    beat = 0.0
    step = 0.5 if difficulty == "Future" else 0.75 if difficulty == "Present" else 1.0

    while len(notes) < note_count:
        t = beat_ms(bpm, beat)
        lane = rng.randint(0, 3)
        plane = "sky" if rng.random() < sky_ratio else "floor"
        roll = rng.random()

        if roll < 0.12:
            notes.append(
                {
                    "t": t,
                    "lane": lane,
                    "plane": plane,
                    "type": "hold",
                    "end_t": t + int(60000 / bpm * rng.choice([1.0, 1.5, 2.0])),
                }
            )
        elif roll < 0.22:
            notes.append(
                {
                    "t": t,
                    "lane": lane,
                    "plane": plane,
                    "type": "arc",
                    "lane_end": (lane + rng.choice([1, 2, 3])) % 4,
                    "end_t": t + int(60000 / bpm * rng.choice([1.0, 1.5])),
                }
            )
        elif plane == "sky" and roll < 0.32:
            notes.append({"t": t, "lane": lane, "plane": "sky", "type": "flick"})
        else:
            notes.append({"t": t, "lane": lane, "plane": plane, "type": "tap"})

        beat += step
        if difficulty == "Future" and rng.random() < 0.08:
            beat += 0.25

    notes.sort(key=lambda n: n["t"])
    return {
        "id": chart_id,
        "title": title,
        "artist": "LUMENFALL",
        "difficulty": difficulty,
        "bpm": bpm,
        "offset_ms": 0,
        "lane_count": 4,
        "notes": notes,
    }


PRESETS = {
    "rapture_chain": ("Rapture Chain", "Present", 178, 95, 0.4),
    "void_surge": ("Void Surge", "Future", 182, 130, 0.55),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LUMENFALL chart JSON")
    parser.add_argument("chart_id", nargs="?", choices=list(PRESETS) + ["custom"])
    parser.add_argument("--count", type=int, default=80)
    parser.add_argument("--bpm", type=float, default=174)
    parser.add_argument("--title", default="Generated")
    parser.add_argument("--difficulty", default="Present")
    parser.add_argument("--sky-ratio", type=float, default=0.35)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    if args.chart_id and args.chart_id != "custom":
        title, diff, bpm, count, sky = PRESETS[args.chart_id]
        chart = generate(args.chart_id, title, diff, bpm, count, sky_ratio=sky, seed=args.seed)
        out = CHART_DIR / f"{args.chart_id}.json"
    else:
        cid = args.title.lower().replace(" ", "_")
        chart = generate(
            cid,
            args.title,
            args.difficulty,
            args.bpm,
            args.count,
            sky_ratio=args.sky_ratio,
            seed=args.seed,
        )
        out = CHART_DIR / f"{cid}.json"

    payload = json.dumps(chart, indent=2)
    if args.stdout:
        print(payload)
        return
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(payload + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(chart['notes'])} notes)")


if __name__ == "__main__":
    main()
