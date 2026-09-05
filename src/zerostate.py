"""Campaign finale: Zero-State Relay."""
from __future__ import annotations

from dataclasses import dataclass, field

try:
    from .merkle import MerkleInvestigation, MerkleNode, NodeType
    from .runtime import Choice, Encounter, GameState
except ImportError:
    from merkle import MerkleInvestigation, MerkleNode, NodeType
    from runtime import Choice, Encounter, GameState


class ObjectiveStatus(str):
    LOCKED = "locked"
    ACTIVE = "active"
    COMPLETE = "complete"


@dataclass
class Objective:
    objective_id: str
    title: str
    status: str = ObjectiveStatus.LOCKED


@dataclass
class ZeroStateRelayMission:
    """Coordinates the final relay tower confrontation."""

    game: GameState = field(default_factory=lambda: GameState(mission="zero_state_relay"))
    objectives: list[Objective] = field(default_factory=lambda: [
        Objective("reach_relay", "Reach the Zero-State Relay tower"),
        Objective("stabilize_relay", "Stabilize the collapsing genesis relay"),
        Objective("break_entity", "Survive the Genesis Entity phase transition"),
        Objective("decode_genesis", "Decode the final genesis signal"),
        Objective("make_choice", "Choose the fate of the Genesis Entity"),
        Objective("extract", "Escape the relay before it resets"),
    ])
    merkle: MerkleInvestigation = field(default_factory=lambda: MerkleInvestigation([
        MerkleNode("zero_state_root", NodeType.ROOT, "zero-state-genesis-signal", corrupted=True),
    ]))
    encounter: Encounter = Encounter("Genesis Entity — Phase 1", 80, 14, 9)

    def __post_init__(self) -> None:
        self._activate("reach_relay")

    def _find(self, objective_id: str) -> Objective:
        for item in self.objectives:
            if item.objective_id == objective_id:
                return item
        raise KeyError(f"Unknown objective: {objective_id}")

    def _activate(self, objective_id: str) -> None:
        self._find(objective_id).status = ObjectiveStatus.ACTIVE

    def _complete(self, objective_id: str, next_id: str | None = None) -> None:
        self._find(objective_id).status = ObjectiveStatus.COMPLETE
        if next_id:
            self._activate(next_id)

    @property
    def current_objective(self) -> Objective:
        for item in self.objectives:
            if item.status == ObjectiveStatus.ACTIVE:
                return item
        raise RuntimeError("Mission has no active objective")

    @property
    def complete(self) -> bool:
        return all(item.status == ObjectiveStatus.COMPLETE for item in self.objectives)

    def reach_relay(self) -> None:
        if self.current_objective.objective_id != "reach_relay":
            raise RuntimeError("The relay has already been reached")
        self.game.investigate()
        self._complete("reach_relay", "stabilize_relay")

    def stabilize_relay(self) -> str:
        if self.current_objective.objective_id != "stabilize_relay":
            raise RuntimeError("The relay is not ready for stabilization")
        digest = self.merkle.scan("zero_state_root").digest
        self.game.player.evidence += 2
        self.game.phase = "encounter"
        self._complete("stabilize_relay", "break_entity")
        return digest

    def break_entity(self, damage: int = 40) -> bool:
        if self.current_objective.objective_id != "break_entity":
            raise RuntimeError("The Genesis Entity is not the current objective")
        if self.game.phase == "encounter":
            self.game.begin_encounter(self.encounter)
        defeated = self.game.attack(damage)
        if defeated:
            self._complete("break_entity", "decode_genesis")
        return defeated

    def decode_genesis(self, key: str = "genesis") -> str:
        if self.current_objective.objective_id != "decode_genesis":
            raise RuntimeError("The final genesis signal is not ready")
        digest = self.merkle.decode("zero_state_root", key)
        self.game.decode()
        self.game.player.hashrate += 20
        self._complete("decode_genesis", "make_choice")
        return digest

    def make_choice(self, choice: Choice) -> None:
        if self.current_objective.objective_id != "make_choice":
            raise RuntimeError("The final choice is not available")
        self.game.choose(choice)
        self._complete("make_choice", "extract")

    def extract(self) -> None:
        if self.current_objective.objective_id != "extract":
            raise RuntimeError("Final extraction is not available")
        if self.game.phase != "complete":
            raise RuntimeError("Final extraction requires a completed choice")
        self._complete("extract")
