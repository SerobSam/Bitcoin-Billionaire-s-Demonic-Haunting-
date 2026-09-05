"""Persistent RPG progression for Genesis Protocol."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlayerProgression:
    """Tracks level, XP, and earned permanent upgrade points."""

    level: int = 1
    experience: int = 0
    upgrade_points: int = 0

    def xp_to_next_level(self) -> int:
        return 100 * self.level

    def award_xp(self, amount: int) -> int:
        """Award non-negative XP and return the number of levels gained."""
        amount = max(0, amount)
        self.experience += amount
        gained = 0
        while self.experience >= self.xp_to_next_level():
            self.experience -= self.xp_to_next_level()
            self.level += 1
            self.upgrade_points += 1
            gained += 1
        return gained

    def spend_upgrade_point(self) -> None:
        if self.upgrade_points <= 0:
            raise RuntimeError("No upgrade points available")
        self.upgrade_points -= 1

    def to_dict(self) -> dict[str, int]:
        return {
            "level": self.level,
            "experience": self.experience,
            "upgrade_points": self.upgrade_points,
        }

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> "PlayerProgression":
        progression = cls(
            level=max(1, int(data.get("level", 1))),
            experience=max(0, int(data.get("experience", 0))),
            upgrade_points=max(0, int(data.get("upgrade_points", 0))),
        )
        return progression
