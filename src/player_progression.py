"""Persistent XP and level progression for Genesis Protocol."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlayerProgression:
    """Tracks long-term character progression independently of a mission."""

    level: int = 1
    xp: int = 0
    upgrade_points: int = 0

    BASE_XP = 100
    XP_GROWTH = 50

    def __post_init__(self) -> None:
        if self.level < 1:
            raise ValueError("level must be at least 1")
        if self.xp < 0:
            raise ValueError("xp cannot be negative")
        if self.upgrade_points < 0:
            raise ValueError("upgrade_points cannot be negative")

    @property
    def xp_to_next_level(self) -> int:
        return self.BASE_XP + (self.level - 1) * self.XP_GROWTH

    def add_xp(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("xp amount cannot be negative")
        levels_gained = 0
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.upgrade_points += 1
            levels_gained += 1
        return levels_gained

    def to_dict(self) -> dict[str, int]:
        return {
            "level": self.level,
            "xp": self.xp,
            "upgrade_points": self.upgrade_points,
        }

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> "PlayerProgression":
        return cls(
            level=int(data.get("level", 1)),
            xp=int(data.get("xp", 0)),
            upgrade_points=int(data.get("upgrade_points", 0)),
        )
