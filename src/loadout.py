"""Progression-aware ability loadouts for Genesis Protocol."""
from __future__ import annotations

from dataclasses import dataclass, field

try:
    from .combat import ABILITIES, Ability
except ImportError:
    from combat import ABILITIES, Ability


DEFAULT_UNLOCKS = ("packet_burn",)


@dataclass
class AbilityLoadout:
    """Tracks which combat abilities the player has earned."""

    unlocked: set[str] = field(default_factory=lambda: set(DEFAULT_UNLOCKS))

    def unlock(self, ability_id: str) -> Ability:
        if ability_id not in ABILITIES:
            raise KeyError(f"Unknown ability: {ability_id}")
        self.unlocked.add(ability_id)
        return ABILITIES[ability_id]

    def is_unlocked(self, ability_id: str) -> bool:
        return ability_id in self.unlocked

    def available(self) -> tuple[Ability, ...]:
        return tuple(ABILITIES[key] for key in ABILITIES if key in self.unlocked)

    def require(self, ability_id: str) -> Ability:
        if not self.is_unlocked(ability_id):
            raise RuntimeError(f"Ability is locked: {ability_id}")
        return ABILITIES[ability_id]

    def to_dict(self) -> dict[str, list[str]]:
        return {"unlocked": [key for key in ABILITIES if key in self.unlocked]}

    @classmethod
    def from_dict(cls, data: dict[str, list[str]]) -> "AbilityLoadout":
        loadout = cls()
        loadout.unlocked.clear()
        for ability_id in data.get("unlocked", []):
            loadout.unlock(ability_id)
        if not loadout.unlocked:
            loadout.unlocked.update(DEFAULT_UNLOCKS)
        return loadout
