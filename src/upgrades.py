"""Spendable character upgrades for Genesis Protocol."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlayerUpgrades:
    """Persistent stats purchased with level-up points."""

    max_health_bonus: int = 0
    hashrate_bonus: int = 0
    corruption_resistance: int = 0
    points_spent: int = 0

    def __post_init__(self) -> None:
        for value in (
            self.max_health_bonus,
            self.hashrate_bonus,
            self.corruption_resistance,
            self.points_spent,
        ):
            if value < 0:
                raise ValueError("upgrade values cannot be negative")

    def spend(self, progression, upgrade: str) -> None:
        if progression.upgrade_points <= 0:
            raise RuntimeError("No upgrade points available")
        costs = {
            "max_health": "max_health_bonus",
            "hashrate": "hashrate_bonus",
            "corruption_resistance": "corruption_resistance",
        }
        if upgrade not in costs:
            raise KeyError(f"Unknown upgrade: {upgrade}")
        setattr(self, costs[upgrade], getattr(self, costs[upgrade]) + 1)
        self.points_spent += 1
        progression.upgrade_points -= 1

    def apply(self, player) -> None:
        """Apply persistent bonuses to a mission PlayerState."""
        base_max_health = 100
        base_hashrate = 50
        player.max_health = base_max_health + self.max_health_bonus * 10
        player.health = min(player.health, player.max_health)
        player.hashrate = max(player.hashrate, base_hashrate + self.hashrate_bonus * 5)
        player.corruption_resistance = self.corruption_resistance

    def to_dict(self) -> dict[str, int]:
        return {
            "max_health_bonus": self.max_health_bonus,
            "hashrate_bonus": self.hashrate_bonus,
            "corruption_resistance": self.corruption_resistance,
            "points_spent": self.points_spent,
        }

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> "PlayerUpgrades":
        return cls(
            max_health_bonus=int(data.get("max_health_bonus", 0)),
            hashrate_bonus=int(data.get("hashrate_bonus", 0)),
            corruption_resistance=int(data.get("corruption_resistance", 0)),
            points_spent=int(data.get("points_spent", 0)),
        )
