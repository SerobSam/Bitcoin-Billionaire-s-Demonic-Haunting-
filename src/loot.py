"""Deterministic weighted loot selection backed by the project's loot tier data."""
from __future__ import annotations

import json
from pathlib import Path
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class LootTier:
    id: str
    name: str
    drop_weight: int
    affix_min: int
    affix_max: int


def load_tiers(path: str | Path) -> list[LootTier]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [LootTier(
        id=item["id"],
        name=item["name"],
        drop_weight=int(item["drop_weight"]),
        affix_min=int(item["affix_min"]),
        affix_max=int(item["affix_max"]),
    ) for item in data["tiers"]]


def choose_tier(tiers: list[LootTier], rng: random.Random | None = None) -> LootTier:
    if not tiers or any(t.drop_weight <= 0 for t in tiers):
        raise ValueError("Loot tiers must be non-empty and have positive weights")
    picker = rng or random.Random()
    return picker.choices(tiers, weights=[t.drop_weight for t in tiers], k=1)[0]


def roll_drop(tiers: list[LootTier], seed: int) -> dict:
    """Return a reproducible drop for mission/test simulations."""
    rng = random.Random(seed)
    tier = choose_tier(tiers, rng)
    affixes = rng.randint(tier.affix_min, tier.affix_max)
    return {"tier": tier.id, "name": tier.name, "affixes": affixes}
