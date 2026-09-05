"""Persistent campaign profile for Genesis Protocol."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

try:
    from .combat import ABILITIES
    from .loadout import AbilityLoadout
    from .player_progression import PlayerProgression
    from .runtime import PlayerState
    from .upgrades import PlayerUpgrades
except ImportError:
    from combat import ABILITIES
    from loadout import AbilityLoadout
    from player_progression import PlayerProgression
    from runtime import PlayerState
    from upgrades import PlayerUpgrades


@dataclass
class CampaignProfile:
    """Long-lived player state shared by every mission in a campaign."""

    player: PlayerState
    upgrades: PlayerUpgrades
    loadout: AbilityLoadout

    @classmethod
    def new(cls) -> "CampaignProfile":
        profile = cls(PlayerState(), PlayerUpgrades(), AbilityLoadout())
        profile.apply_upgrades()
        return profile

    @property
    def progression(self) -> PlayerProgression:
        return self.player.progression

    def apply_upgrades(self) -> None:
        """Apply purchased bonuses before a mission begins."""
        self.upgrades.apply(self.player)

    def mission_player(self) -> PlayerState:
        """Return the shared PlayerState after refreshing upgrade bonuses."""
        self.apply_upgrades()
        return self.player

    def grant_mission_rewards(self, campaign, mission_id: str) -> tuple[str, ...]:
        """Grant completed-mission rewards to persistent inventory/loadout."""
        rewards = campaign.grant_rewards(mission_id, self.loadout)
        for reward in rewards:
            if reward not in ABILITIES and reward not in self.player.inventory:
                self.player.add_item(reward)
        return rewards

    def to_dict(self) -> dict:
        return {
            "player": {
                "health": self.player.health,
                "max_health": self.player.max_health,
                "hashrate": self.player.hashrate,
                "corruption": self.player.corruption,
                "evidence": self.player.evidence,
                "reputation": self.player.reputation,
                "inventory": dict(self.player.inventory),
                "choices": list(self.player.choices),
                "progression": self.progression.to_dict(),
            },
            "upgrades": self.upgrades.to_dict(),
            "loadout": self.loadout.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CampaignProfile":
        player_data = dict(data.get("player", {}))
        progression = PlayerProgression.from_dict(player_data.pop("progression", {}))
        player = PlayerState(**player_data, progression=progression)
        profile = cls(
            player=player,
            upgrades=PlayerUpgrades.from_dict(data.get("upgrades", {})),
            loadout=AbilityLoadout.from_dict(data.get("loadout", {})),
        )
        profile.apply_upgrades()
        return profile

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "CampaignProfile":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
