"""Second playable mission: Irvine Consensus."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

try:
    from .merkle import MerkleInvestigation, MerkleNode, NodeType
    from .runtime import Choice, Encounter, GameState
except ImportError:  # Allows direct script-style imports.
    from merkle import MerkleInvestigation, MerkleNode, NodeType
    from runtime import Choice, Encounter, GameState


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
class IrvineConsensusMission:
    """Coordinates the Irvine Consensus mission as an engine-neutral slice."""

    game: GameState = field(default_factory=lambda: GameState(mission="irvine_consensus"))
    objectives: list[Objective] = field(default_factory=lambda: [
        Objective("enter_suburbs", "Enter the silent Irvine consensus district"),
        Objective("trace_consensus", "Trace the compromised neighborhood consensus node"),
        Objective("break_vanguard", "Break the Grid Vanguard security construct"),
        Objective("decode_vote", "Decode the stolen consensus vote"),
        Objective("make_choice", "Decide whether to cleanse, exploit, or quarantine the node"),
        Objective("extract", "Escape before the district reconnects"),
    ])
    merkle: MerkleInvestigation = field(default_factory=lambda: MerkleInvestigation([
        MerkleNode("irvine_consensus", NodeType.ROOT, "irvine-consensus-vote", corrupted=True),
    ]))
    encounter: Encounter = Encounter("Grid Vanguard", 50, 10, 5)

    def __post_init__(self) -> None:
        self._activate("enter_suburbs")

    def _find(self, objective_id: str) -> Objective:
        for objective in self.objectives:
            if objective.objective_id == objective_id:
                return objective
        raise KeyError(f"Unknown objective: {objective_id}")

    def _activate(self, objective_id: str) -> None:
        self._find(objective_id).status = ObjectiveStatus.ACTIVE

    def _complete(self, objective_id: str, next_id: str | None = None) -> None:
        self._find(objective_id).status = ObjectiveStatus.COMPLETE
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
        return all(item.status is ObjectiveStatus.COMPLETE for item in self.objectives)

    def enter_suburbs(self) -> None:
        if self.current_objective.objective_id != "enter_suburbs":
            raise RuntimeError("The Irvine district has already been entered")
        self.game.investigate()
        self._complete("enter_suburbs", "trace_consensus")

    def trace_consensus(self) -> str:
        if self.current_objective.objective_id != "trace_consensus":
            raise RuntimeError("The consensus node is not the current objective")
        node = self.merkle.scan("irvine_consensus")
        self._complete("trace_consensus", "break_vanguard")
        return node.digest

    def break_vanguard(self, damage: int = 25) -> bool:
        if self.current_objective.objective_id != "break_vanguard":
            raise RuntimeError("The Grid Vanguard is not the current objective")
        if self.game.phase == "encounter":
            self.game.begin_encounter(self.encounter)
        defeated = self.game.attack(damage)
        if defeated:
            self._complete("break_vanguard", "decode_vote")
        return defeated

    def decode_vote(self, key: str = "genesis") -> str:
        if self.current_objective.objective_id != "decode_vote":
            raise RuntimeError("The consensus vote is not ready to decode")
        digest = self.merkle.decode("irvine_consensus", key)
        self.game.decode()
        self._complete("decode_vote", "make_choice")
        return digest

    def make_choice(self, choice: Choice) -> None:
        if self.current_objective.objective_id != "make_choice":
            raise RuntimeError("The Irvine moral choice is not available")
        self.game.choose(choice)
        self._complete("make_choice", "extract")

    def extract(self) -> None:
        if self.current_objective.objective_id != "extract":
            raise RuntimeError("Irvine extraction is not available")
        if self.game.phase != "complete":
            raise RuntimeError("Irvine extraction requires a completed choice")
        self._complete("extract")
