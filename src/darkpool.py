"""Third playable mission: Dark Pool Descent."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

try:
    from .merkle import MerkleInvestigation, MerkleNode, NodeType
    from .runtime import Choice, Encounter, GameState
except ImportError:
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
class DarkPoolDescentMission:
    """Coordinates the subterranean Dark Pool mission as an engine-neutral slice."""

    game: GameState = field(default_factory=lambda: GameState(mission="dark_pool_descent"))
    objectives: list[Objective] = field(default_factory=lambda: [
        Objective("enter_dungeons", "Descend into the Dark Pool dungeons"),
        Objective("find_choir", "Locate the Blackwater Choir signal"),
        Objective("break_warden", "Break the Dark Pool Warden"),
        Objective("decode_liturgy", "Decode the submerged chain liturgy"),
        Objective("make_choice", "Decide the fate of the Dark Pool"),
        Objective("extract", "Escape through the flooded service shaft"),
    ])
    merkle: MerkleInvestigation = field(default_factory=lambda: MerkleInvestigation([
        MerkleNode("dark_pool_liturgy", NodeType.ROOT, "blackwater-choir-liturgy", corrupted=True),
    ]))
    encounter: Encounter = Encounter("Dark Pool Warden", 60, 14, 8)

    def __post_init__(self) -> None:
        self._activate("enter_dungeons")

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

    def enter_dungeons(self) -> None:
        if self.current_objective.objective_id != "enter_dungeons":
            raise RuntimeError("The Dark Pool has already been entered")
        self.game.investigate()
        self._complete("enter_dungeons", "find_choir")

    def find_choir(self) -> str:
        if self.current_objective.objective_id != "find_choir":
            raise RuntimeError("The Blackwater Choir is not the current objective")
        node = self.merkle.scan("dark_pool_liturgy")
        self._complete("find_choir", "break_warden")
        return node.digest

    def break_warden(self, damage: int = 30) -> bool:
        if self.current_objective.objective_id != "break_warden":
            raise RuntimeError("The Dark Pool Warden is not the current objective")
        if self.game.phase == "encounter":
            self.game.begin_encounter(self.encounter)
        defeated = self.game.attack(damage)
        if defeated:
            self._complete("break_warden", "decode_liturgy")
        return defeated

    def decode_liturgy(self, key: str = "genesis") -> str:
        if self.current_objective.objective_id != "decode_liturgy":
            raise RuntimeError("The chain liturgy is not ready to decode")
        digest = self.merkle.decode("dark_pool_liturgy", key)
        self.game.decode()
        self._complete("decode_liturgy", "make_choice")
        return digest

    def make_choice(self, choice: Choice) -> None:
        if self.current_objective.objective_id != "make_choice":
            raise RuntimeError("The Dark Pool moral choice is not available")
        self.game.choose(choice)
        self._complete("make_choice", "extract")

    def extract(self) -> None:
        if self.current_objective.objective_id != "extract":
            raise RuntimeError("Dark Pool extraction is not available")
        if self.game.phase != "complete":
            raise RuntimeError("Dark Pool extraction requires a completed choice")
        self._complete("extract")
