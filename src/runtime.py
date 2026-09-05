"""Small, deterministic runtime foundation for the Genesis Protocol vertical slice."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import date
import json
from pathlib import Path
from typing import Dict, List

try:
    from .player_progression import PlayerProgression
    from .live_ops import DLC_MISSIONS, LiveOpsWallet, RotatingEventSchedule, SeasonPass
    from .live_ops_rewards import claim_season_reward, grant_event_reward
except ImportError:
    from player_progression import PlayerProgression
    from live_ops import DLC_MISSIONS, LiveOpsWallet, RotatingEventSchedule, SeasonPass
    from live_ops_rewards import claim_season_reward, grant_event_reward


class Choice(str, Enum):
    CLEANSE = "cleanse"
    EXPLOIT = "exploit"
    QUARANTINE = "quarantine"


@dataclass
class PlayerState:
    health: int = 100
    max_health: int = 100
    hashrate: int = 50
    corruption: int = 0
    corruption_resistance: int = 0
    evidence: int = 0
    reputation: int = 0
    inventory: Dict[str, int] = field(default_factory=dict)
    choices: List[str] = field(default_factory=list)
    progression: PlayerProgression = field(default_factory=PlayerProgression)

    def __post_init__(self) -> None:
        if self.corruption_resistance < 0:
            raise ValueError("corruption_resistance must be non-negative")

    def damage(self, amount: int) -> bool:
        self.health = max(0, self.health - max(0, amount))
        return self.health == 0

    def gain_corruption(self, amount: int) -> None:
        self.corruption = min(100, self.corruption + max(0, amount - self.corruption_resistance))

    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + max(0, amount))

    def add_item(self, item: str, count: int = 1) -> None:
        if count > 0:
            self.inventory[item] = self.inventory.get(item, 0) + count

    def earn_xp(self, amount: int) -> int:
        return self.progression.add_xp(amount)


@dataclass(frozen=True)
class Encounter:
    name: str
    enemy_health: int
    enemy_damage: int
    corruption_on_hit: int = 0


@dataclass
class GameState:
    mission: str = "bel_air_blackout"
    phase: str = "investigate"
    player: PlayerState = field(default_factory=PlayerState)
    encounter: Encounter | None = None
    dlc_mission_id: str | None = None
    completed_dlc_missions: set[str] = field(default_factory=set)
    claimed_event_ids: set[str] = field(default_factory=set)
    season_pass: SeasonPass = field(default_factory=SeasonPass)

    @property
    def player_defeated(self) -> bool:
        return self.player.health <= 0

    @property
    def active_event(self):
        return RotatingEventSchedule().event_for(date.today())

    def investigate(self) -> None:
        if self.phase != "investigate":
            raise RuntimeError("Investigation is not available in the current phase")
        xp = DLC_MISSIONS[self.dlc_mission_id].investigation_xp if self.dlc_mission_id else 25
        self.player.evidence += 1
        self.player.earn_xp(xp)
        self.season_pass.add_xp(xp, self.active_event.xp_multiplier)
        self.phase = "encounter"

    def begin_encounter(self, encounter: Encounter) -> None:
        if self.phase not in {"investigate", "encounter"}:
            raise RuntimeError("An encounter cannot start from the current phase")
        self.encounter = encounter
        self.phase = "combat"

    def begin_dlc_mission(self, wallet: LiveOpsWallet, mission_id: str) -> None:
        mission = DLC_MISSIONS.get(mission_id)
        if mission is None:
            raise KeyError(f"Unknown DLC mission: {mission_id}")
        if not wallet.owns_mission(mission_id):
            raise PermissionError("DLC mission is not owned")
        if self.phase not in {"investigate", "complete"}:
            raise RuntimeError("A DLC mission cannot start from the current phase")
        chain = wallet.available_missions()
        mission_index = chain.index(mission_id)
        if mission_index > 0 and chain[mission_index - 1] not in self.completed_dlc_missions:
            raise RuntimeError("Previous DLC mission in the chain is not complete")
        self.mission = mission_id
        self.dlc_mission_id = mission_id
        self.encounter = None
        self.phase = "investigate"

    def attack(self, damage: int) -> bool:
        if self.phase != "combat" or self.encounter is None:
            raise RuntimeError("No active encounter")
        if self.player_defeated:
            raise RuntimeError("The player is already defeated")
        remaining = self.encounter.enemy_health - max(0, damage)
        self.encounter = Encounter(self.encounter.name, remaining, self.encounter.enemy_damage, self.encounter.corruption_on_hit)
        if remaining <= 0:
            xp, loot = 100, "corrupted_fragment"
            if self.dlc_mission_id:
                mission = DLC_MISSIONS[self.dlc_mission_id]
                xp, loot = mission.completion_xp, mission.loot_item
                self.player.evidence += mission.evidence_reward
                self.completed_dlc_missions.add(self.dlc_mission_id)
            self.player.add_item(loot)
            self.player.earn_xp(xp)
            self.season_pass.add_xp(xp, self.active_event.xp_multiplier)
            self.phase = "decode"
            self.encounter = None
            return True
        self.player.damage(self.encounter.enemy_damage)
        self.player.gain_corruption(self.encounter.corruption_on_hit)
        return False

    def decode(self) -> None:
        if self.phase != "decode":
            raise RuntimeError("There is nothing to decode")
        self.player.hashrate += 10
        self.player.earn_xp(50)
        self.season_pass.add_xp(50, self.active_event.xp_multiplier)
        self.phase = "choice"

    def choose(self, choice: Choice) -> None:
        if self.phase != "choice":
            raise RuntimeError("A moral choice is not available")
        self.player.choices.append(choice.value)
        if choice is Choice.CLEANSE:
            self.player.corruption = max(0, self.player.corruption - 25)
            self.player.reputation += 2
        elif choice is Choice.EXPLOIT:
            self.player.hashrate += 30
            self.player.corruption = min(100, self.player.corruption + 20)
            self.player.reputation -= 1
        else:
            self.player.corruption = max(0, self.player.corruption - 10)
            self.player.reputation += 1
        self.player.earn_xp(25)
        self.season_pass.add_xp(25, self.active_event.xp_multiplier)
        self.phase = "complete"

    def claim_season_reward(self, tier: int, premium: bool = False) -> str:
        return claim_season_reward(self.season_pass, self.player.inventory, tier, premium=premium)

    def claim_active_event_reward(self) -> str:
        event = self.active_event
        if event.event_id in self.claimed_event_ids:
            raise ValueError("Active event reward is already claimed")
        item = grant_event_reward(self.player.inventory, event.reward_item)
        self.claimed_event_ids.add(event.event_id)
        return item

    def save(self, path: str | Path) -> None:
        payload = asdict(self)
        payload["season_pass"] = self.season_pass.to_dict()
        payload["completed_dlc_missions"] = sorted(self.completed_dlc_missions)
        payload["claimed_event_ids"] = sorted(self.claimed_event_ids)
        if self.encounter is not None:
            payload["encounter"] = asdict(self.encounter)
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "GameState":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        player_data = dict(data["player"])
        progression_data = player_data.pop("progression", None)
        player = PlayerState(**player_data, progression=PlayerProgression.from_dict(progression_data or {}))
        encounter_data = data.get("encounter")
        encounter = Encounter(**encounter_data) if encounter_data else None
        return cls(
            data["mission"],
            data["phase"],
            player,
            encounter,
            data.get("dlc_mission_id"),
            set(data.get("completed_dlc_missions", [])),
            set(data.get("claimed_event_ids", [])),
            SeasonPass.from_dict(data.get("season_pass", {})),
        )


FIRST_ENCOUNTER = Encounter("Digital Wraith", 40, 12, 7)
