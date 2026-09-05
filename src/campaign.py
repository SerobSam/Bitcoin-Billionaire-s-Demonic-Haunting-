"""Campaign-level mission progression for Genesis Protocol."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class MissionDefinition:
    mission_id: str
    title: str
    region: str
    unlock: str | None
    next_mission: str | None
    rewards: tuple[str, ...] = ()


class Campaign:
    """Tracks completed missions and exposes progression rewards."""

    def __init__(self, missions: list[MissionDefinition]):
        if not missions:
            raise ValueError("Campaign requires at least one mission")
        self.missions = {mission.mission_id: mission for mission in missions}
        self.completed: list[str] = []

    @classmethod
    def load(cls, path: str | Path) -> "Campaign":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        missions = [
            MissionDefinition(
                mission_id=item["id"],
                title=item["title"],
                region=item["region"],
                unlock=item.get("unlock"),
                next_mission=item.get("next"),
                rewards=tuple(item.get("rewards", [])),
            )
            for item in data["missions"]
        ]
        return cls(missions)

    def is_unlocked(self, mission_id: str) -> bool:
        mission = self.missions[mission_id]
        return mission.unlock is None or mission.unlock in self.completed

    def complete_mission(self, mission_id: str) -> MissionDefinition:
        if mission_id not in self.missions:
            raise KeyError(f"Unknown mission: {mission_id}")
        if not self.is_unlocked(mission_id):
            raise RuntimeError(f"Mission is locked: {mission_id}")
        if mission_id not in self.completed:
            self.completed.append(mission_id)
        return self.missions[mission_id]

    def rewards_for(self, mission_id: str) -> tuple[str, ...]:
        if mission_id not in self.missions:
            raise KeyError(f"Unknown mission: {mission_id}")
        if mission_id not in self.completed:
            raise RuntimeError(f"Mission is not complete: {mission_id}")
        return self.missions[mission_id].rewards

    def grant_rewards(self, mission_id: str, loadout) -> tuple[str, ...]:
        """Apply ability rewards to a loadout; non-ability rewards remain inventory rewards."""
        try:
            from .combat import ABILITIES
        except ImportError:
            from combat import ABILITIES
        rewards = self.rewards_for(mission_id)
        for reward in rewards:
            if reward in ABILITIES:
                loadout.unlock(reward)
        return rewards

    def available(self) -> list[MissionDefinition]:
        return [mission for mission in self.missions.values() if self.is_unlocked(mission.mission_id)]

    def next_mission(self, mission_id: str) -> MissionDefinition | None:
        mission = self.missions[mission_id]
        if mission.next_mission is None:
            return None
        if not self.is_unlocked(mission.next_mission):
            return None
        return self.missions[mission.next_mission]
