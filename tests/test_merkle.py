import pytest

from src.merkle import MerkleInvestigation, MerkleNode, NodeType


def test_scan_and_decode_track_completion():
    investigation = MerkleInvestigation([
        MerkleNode("genesis", NodeType.ROOT, "impossible-block"),
        MerkleNode("leaf-01", NodeType.LEAF, "wallet-echo", corrupted=True),
    ])
    assert investigation.scan("genesis").node_type is NodeType.ROOT
    token = investigation.decode("leaf-01", "genesis")
    assert len(token) == 8
    assert investigation.completion == 0.5


def test_corrupted_node_rejects_wrong_key():
    investigation = MerkleInvestigation([
        MerkleNode("leaf-01", NodeType.LEAF, "wallet-echo", corrupted=True),
    ])
    with pytest.raises(ValueError, match="Corrupted node"):
        investigation.decode("leaf-01", "wrong-key")


def test_unknown_node_is_explicit():
    investigation = MerkleInvestigation([
        MerkleNode("root", NodeType.ROOT, "root-payload"),
    ])
    with pytest.raises(KeyError, match="Unknown Merkle node"):
        investigation.scan("missing")
