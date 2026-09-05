"""Small, deterministic runtime foundation for the Genesis Protocol vertical slice."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from pathlib import Path
from typing import Dict, List

try:
    from .player_progression import PlayerProgression
except ImportError:
    from player_progression import PlayerProgression


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
        """Apply corruption after resistance from persistent character upgrades."""
        reduced = max(0, amount - self.corruption_resistance)
        self.corruption = min(100, self.corruption + reduced)

    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + max(0, amount))

    def add_item(self, item: str, count: int = 1) -> None:
        if count > 0:
            self.inventory[item] = self.inventory.get(item, 0) + count

    def earn_xp(self, amount: int) -> int:
        """Award XP through the persistent progression component."""
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

    def investigate(self) -> None:
        if self.phase != "investigate":
            raise RuntimeError("Investigation is not available in the current phase")
        self.player.evidence += 1
        self.player.earn_xp(25)
        self.phase = "encounter"

    def begin_encounter(self, encounter: Encounter) -> None:
        if self.phase != "encounter":
            raise RuntimeError("An encounter cannot start from the current phase")
        self.encounter = encounter
        self.phase = "combat"

    def attack(self, damage: int) -> bool:
        if self.phase != "combat" or self.encounter is None:
            raise RuntimeError("No active encounter")
        if self.player_defeated:
            raise RuntimeError("The player is already defeated")
        remaining = self.encounter.enemy_health - max(0, damage)
        self.encounter = Encounter(
            self.encounter.name,
            remaining,
            self.encounter.enemy_damage,
            self.encounter.corruption_on_hit,
        )
        if remaining <= 0:
            self.player.add_item("corrupted_fragment")
            self.player.earn_xp(100)
            self.phase = "decode"
            self.encounter = None
            return True
        self.player.damage(self.encounter.enemy_damage)
        self.player.gain_corruption(self.encounter.corruption_on_hit)
        return False

    @property
    def player_defeated(self) -> bool:
        return self.player.health <= 0

    def decode(self) -> None:
        if self.phase != "decode":
            raise RuntimeError("There is nothing to decode")
        self.player.hashrate += 10
        self.player.earn_xp(50)
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
        self.phase = "complete"

    def save(self, path: str | Path) -> None:
        payload = asdict(self)
        if self.encounter is not None:
            payload["encounter"] = asdict(self.encounter)
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "GameState":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        player_data = data["player"]
        progression_data = player_data.pop("progression", None)
        player = PlayerState(
            **player_data,
            progression=PlayerProgression.from_dict(progression_data or {}),
        )
        encounter_data = data.get("encounter")
        encounter = Encounter(**encounter_data) if encounter_data else None
        return cls(data["mission"], data["phase"], player, encounter)


FIRST_ENCOUNTER = Encounter(
    name="Digital Wraith",
    enemy_health=40,
    enemy_damage=12,
    corruption_on_hit=7,
)
