"""Engine-neutral mission orchestration for the Genesis Protocol vertical slice."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .merkle import MerkleInvestigation, MerkleNode, NodeType
from .runtime import Choice, Encounter, GameState


class ObjectiveStatus(str, Enum):
    LOCKED = "locked"
    ACTIVE = "active"
    COMPLETE = "complete"


@dataclass
class Objective:
    objective_id: str
    title: str
    status: ObjectiveStatus = ObjectiveStatus.LOCKED


@dataclass
class BelAirBlackoutMission:
    """Coordinates the playable objective sequence without owning a renderer."""

    game: GameState = field(default_factory=GameState)
    objectives: list[Objective] = field(default_factory=lambda: [
        Objective("reach_estate", "Reach the blacked-out Bel Air estate"),
        Objective("scan_terminal", "Scan the corrupted genesis terminal"),
        Objective("survive_wraith", "Survive the Digital Wraith"),
        Objective("decode_fragment", "Decode the recovered chain fragment"),
        Objective("make_choice", "Decide the fate of the corrupted node"),
        Objective("extract", "Extract before the blackout collapses"),
    ])
    merkle: MerkleInvestigation = field(default_factory=lambda: MerkleInvestigation([
        MerkleNode("genesis_terminal", NodeType.ROOT, "bel-air-genesis-spark", corrupted=True),
    ]))
    encounter: Encounter = Encounter("Digital Wraith", 40, 12, 7)

    def __post_init__(self) -> None:
        self._activate("reach_estate")

    def _find(self, objective_id: str) -> Objective:
        for objective in self.objectives:
            if objective.objective_id == objective_id:
                return objective
        raise KeyError(f"Unknown objective: {objective_id}")

    def _activate(self, objective_id: str) -> None:
        objective = self._find(objective_id)
        objective.status = ObjectiveStatus.ACTIVE

    def _complete(self, objective_id: str, next_id: str | None = None) -> None:
        objective = self._find(objective_id)
        objective.status = ObjectiveStatus.COMPLETE
        if next_id is not None:
            self._activate(next_id)

    @property
    def current_objective(self) -> Objective:
        for objective in self.objectives:
            if objective.status is ObjectiveStatus.ACTIVE:
                return objective
        raise RuntimeError("Mission has no active objective")

    @property
    def complete(self) -> bool:
        return all(objective.status is ObjectiveStatus.COMPLETE for objective in self.objectives)

    def reach_estate(self) -> None:
        if self.current_objective.objective_id != "reach_estate":
            raise RuntimeError("The estate has already been reached")
        self.game.investigate()
        self._complete("reach_estate", "scan_terminal")

    def scan_terminal(self) -> str:
        if self.current_objective.objective_id != "scan_terminal":
            raise RuntimeError("The genesis terminal is not the current objective")
        node = self.merkle.scan("genesis_terminal")
        self._complete("scan_terminal", "survive_wraith")
        return node.digest

    def survive_wraith(self, damage: int = 20) -> bool:
        if self.current_objective.objective_id != "survive_wraith":
            raise RuntimeError("The Digital Wraith is not the current objective")
        if self.game.phase == "encounter":
            self.game.begin_encounter(self.encounter)
        defeated = self.game.attack(damage)
        if defeated:
            self._complete("survive_wraith", "decode_fragment")
        return defeated

    def decode_fragment(self, key: str = "genesis") -> str:
        if self.current_objective.objective_id != "decode_fragment":
            raise RuntimeError("The chain fragment is not ready to decode")
        digest = self.merkle.decode("genesis_terminal", key)
        self.game.decode()
        self._complete("decode_fragment", "make_choice")
        return digest

    def make_choice(self, choice: Choice) -> None:
        if self.current_objective.objective_id != "make_choice":
            raise RuntimeError("The moral choice is not available")
        self.game.choose(choice)
        self._complete("make_choice", "extract")

    def extract(self) -> None:
        if self.current_objective.objective_id != "extract":
            raise RuntimeError("Extraction is not available")
        self._complete("extract")
        if self.game.phase != "complete":
            raise RuntimeError("Mission extraction requires a completed choice")
