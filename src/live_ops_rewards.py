"""Helpers for turning live-ops track rewards into player inventory items."""
from __future__ import annotations

from typing import MutableMapping

from .live_ops import SeasonPass


def claim_season_reward(
    season: SeasonPass,
    inventory: MutableMapping[str, int],
    tier: int,
    premium: bool = False,
) -> str:
    """Claim one unlocked reward and atomically add it to player inventory."""
    item = season.claim(tier, premium=premium)
    inventory[item] = inventory.get(item, 0) + 1
    return item


def grant_event_reward(inventory: MutableMapping[str, int], event_item: str) -> str:
    """Grant a rotating-event cache exactly once per supplied reward call."""
    if not event_item:
        raise ValueError("event item cannot be empty")
    inventory[event_item] = inventory.get(event_item, 0) + 1
    return event_item
