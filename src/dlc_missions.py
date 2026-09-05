"""Playable runtime mission chains for the three Genesis Protocol add-ons."""
from __future__ import annotations

from dataclasses import dataclass

try:
    from .live_ops import CONTENT_ADD_ONS
    from .runtime import Choice, Encounter, GameState
except ImportError:
    from live_ops import CONTENT_ADD_ONS
    from runtime import Choice, Encounter, GameState


@dataclass(frozen=True)
class MissionSpec:
    mission_id: str
    title: str
    evidence_reward: int
    xp_reward: int
    encounter: Encounter
    loot: str


MISSION_SPECS = {
    "neon_tokyo_blackout": MissionSpec("neon_tokyo_blackout", "Neon Tokyo: Blackout", 2, 125, Encounter("Neon Oni", 35, 10, 6), "neon_core"),
    "shibuya_wraith_hunt": MissionSpec("shibuya_wraith_hunt", "Shibuya Wraith Hunt", 2, 150, Encounter("Shibuya Wraith", 50, 13, 8), "wraith_mask"),
    "datacenter_descent": MissionSpec("datacenter_descent", "Datacenter Descent", 3, 175, Encounter("Possessed Miner", 60, 14, 10), "infernal_hash"),
    "server_cathedral": MissionSpec("server_cathedral", "Server Cathedral", 3, 200, Encounter("Server Seraph", 70, 16, 12), "seraph_key"),
    "aftershock": MissionSpec("aftershock", "Aftershock", 4, 200, Encounter("Genesis Echo", 65, 15, 9), "echo_shard"),
    "zero_day_epilogue": MissionSpec("zero_day_epilogue", "Zero-Day Epilogue", 5, 250, Encounter("Zero-Day Revenant", 85, 18, 14), "zero_day_key"),
}


@dataclass
class PlayableDLCMission:
    """A six-step mission driven by the same GameState combat/decode runtime."""

    spec: MissionSpec
    game: GameState
    step: str = "investigate"
    completed: bool = False

    @classmethod
    def start(cls, mission_id: str) -> "PlayableDLCMission":
        if mission_id not in MISSION_SPECS:
            raise KeyError(f"Unknown DLC mission: {mission_id}")
        return cls(MISSION_SPECS[mission_id], GameState(mission=mission_id))

    def investigate(self) -> None:
        self._require("investigate")
        self.game.investigate()
        self.game.player.evidence += self.spec.evidence_reward - 1
        self.step = "combat"

    def attack(self, damage: int) -> bool:
        self._require("combat")
        if self.game.encounter is None:
            self.game.begin_encounter(self.spec.encounter)
        defeated = self.game.attack(damage)
        if defeated:
            self.game.player.add_item(self.spec.loot)
            self.game.player.earn_xp(self.spec.xp_reward)
            self.step = "decode"
        return defeated

    def decode(self, key: str = "genesis") -> None:
        self._require("decode")
        self.game.decode()
        self.game.player.add_item(f"decoded_{self.spec.mission_id}")
        self.step = "choice"

    def choose(self, choice: Choice = Choice.QUARANTINE) -> None:
        self._require("choice")
        self.game.choose(choice)
        self.step = "extract"

    def extract(self) -> str:
        self._require("extract")
        self.completed = True
        self.step = "complete"
        return self.spec.loot

    def _require(self, step: str) -> None:
        if self.step != step:
            raise RuntimeError(f"DLC mission requires {step} step")


DLC_CHAINS = {
    add_on_id: tuple(PlayableDLCMission.start(mission_id) for mission_id in add_on.missions)
    for add_on_id, add_on in CONTENT_ADD_ONS.items()
}


def missions_for_add_on(add_on_id: str) -> tuple[MissionSpec, ...]:
    add_on = CONTENT_ADD_ONS.get(add_on_id)
    if add_on is None:
        raise KeyError(f"Unknown content add-on: {add_on_id}")
    return tuple(MISSION_SPECS[mission_id] for mission_id in add_on.missions)
