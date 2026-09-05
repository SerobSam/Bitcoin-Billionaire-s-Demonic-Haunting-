"""Deterministic tactical combat helpers for Genesis Protocol."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .loadout import AbilityLoadout
    from .profile import CampaignProfile


class DamageType(str, Enum):
    PHYSICAL = "physical"
    DIGITAL = "digital"
    OCCULT = "occult"
    VOID = "void"


@dataclass(frozen=True)
class Ability:
    ability_id: str
    name: str
    damage: int
    damage_type: DamageType
    cooldown: int
    corruption_gain: int = 0
    description: str = ""


@dataclass
class CooldownState:
    remaining: int = 0

    def tick(self) -> None:
        self.remaining = max(0, self.remaining - 1)

    @property
    def ready(self) -> bool:
        return self.remaining == 0


@dataclass
class Combatant:
    health: int
    max_health: int
    corruption: int = 0

    def take_damage(self, amount: int) -> bool:
        self.health = max(0, self.health - max(0, amount))
        return self.health == 0


ABILITIES = {
    "packet_burn": Ability(
        "packet_burn", "Packet Burn", 28, DamageType.DIGITAL, 2,
        description="Scorch a hostile process with a burst of corrupted packets.",
    ),
    "salt_circle": Ability(
        "salt_circle", "Salt Circle", 18, DamageType.OCCULT, 3,
        corruption_gain=5,
        description="A warding strike that trades a little sanity for reliable occult damage.",
    ),
    "cold_storage": Ability(
        "cold_storage", "Cold Storage", 12, DamageType.VOID, 4,
        corruption_gain=8,
        description="Freeze a hostile process inside a dead wallet state.",
    ),
}


class CombatSystem:
    """Resolves unlocked abilities without randomness so encounters remain reproducible."""

    def __init__(
        self,
        player: Combatant,
        enemy: Combatant,
        loadout: AbilityLoadout | None = None,
        corruption_resistance: int = 0,
    ) -> None:
        if loadout is None:
            from .loadout import AbilityLoadout
            loadout = AbilityLoadout()
        if corruption_resistance < 0:
            raise ValueError("corruption_resistance must be non-negative")
        self.player = player
        self.enemy = enemy
        self.loadout = loadout
        self.corruption_resistance = corruption_resistance
        self.cooldowns = {ability_id: CooldownState() for ability_id in ABILITIES}
        self.turn = 0

    @classmethod
    def from_profile(
        cls,
        profile: CampaignProfile,
        enemy: Combatant,
    ) -> "CombatSystem":
        """Build combat from persistent profile stats and unlocked abilities."""
        profile.apply_upgrades()
        player = Combatant(
            health=profile.player.health,
            max_health=profile.player.max_health,
            corruption=profile.player.corruption,
        )
        return cls(
            player=player,
            enemy=enemy,
            loadout=profile.loadout,
            corruption_resistance=profile.player.corruption_resistance,
        )

    def sync_player_to_profile(self, profile: CampaignProfile) -> None:
        """Persist combat health/corruption back into the campaign profile."""
        profile.player.health = self.player.health
        profile.player.max_health = self.player.max_health
        profile.player.corruption = self.player.corruption

    def _apply_corruption(self, amount: int) -> None:
        reduced = max(0, amount - self.corruption_resistance)
        self.player.corruption = min(100, self.player.corruption + reduced)

    def use(self, ability_id: str) -> int:
        if ability_id not in ABILITIES:
            raise KeyError(f"Unknown ability: {ability_id}")
        ability = self.loadout.require(ability_id)
        cooldown = self.cooldowns[ability_id]
        if not cooldown.ready:
            raise RuntimeError(f"{ability.name} is on cooldown")

        self._apply_corruption(ability.corruption_gain)
        self.enemy.take_damage(ability.damage)
        cooldown.remaining = ability.cooldown
        self.turn += 1
        for key, state in self.cooldowns.items():
            if key != ability_id:
                state.tick()
        return ability.damage

    def basic_attack(self, damage: int = 20) -> int:
        self.enemy.take_damage(damage)
        self.turn += 1
        for state in self.cooldowns.values():
            state.tick()
        return damage

    @property
    def defeated(self) -> bool:
        return self.enemy.health <= 0
