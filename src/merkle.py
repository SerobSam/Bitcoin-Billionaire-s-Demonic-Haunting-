"""Gameplay-facing Merkle chain mechanics for investigation and decoding."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib


class NodeType(str, Enum):
    LEAF = "leaf"
    BRANCH = "branch"
    ROOT = "root"


@dataclass(frozen=True)
class MerkleNode:
    node_id: str
    node_type: NodeType
    payload: str
    corrupted: bool = False

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.payload.encode("utf-8")).hexdigest()


class MerkleInvestigation:
    """Tracks discovered nodes and turns clean decoded nodes into evidence."""

    def __init__(self, nodes: list[MerkleNode]):
        if not nodes:
            raise ValueError("At least one Merkle node is required")
        self.nodes = {node.node_id: node for node in nodes}
        self.decoded: set[str] = set()

    def scan(self, node_id: str) -> MerkleNode:
        try:
            return self.nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"Unknown Merkle node: {node_id}") from exc

    def decode(self, node_id: str, key: str) -> str:
        node = self.scan(node_id)
        expected = hashlib.sha256(f"{node.payload}:{key}".encode("utf-8")).hexdigest()[:8]
        if node.corrupted and key != "genesis":
            raise ValueError("Corrupted node rejected the supplied key")
        self.decoded.add(node_id)
        return expected

    @property
    def completion(self) -> float:
        return len(self.decoded) / len(self.nodes)
