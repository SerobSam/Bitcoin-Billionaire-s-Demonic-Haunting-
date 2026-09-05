import pytest

from src.merkle import MerkleInvestigation, MerkleNode, NodeType


def test_scan_decode_and_completion():
    investigation = MerkleInvestigation([
        MerkleNode("root", NodeType.ROOT, "genesis-payload"),
        MerkleNode("leaf", NodeType.LEAF, "fragment"),
    ])
    assert investigation.scan("root").node_type is NodeType.ROOT
    assert len(investigation.decode("root", "key")) == 8
    assert investigation.completion == 0.5


def test_corrupted_node_rejects_wrong_key():
    investigation = MerkleInvestigation([
        MerkleNode("corrupt", NodeType.BRANCH, "haunted", corrupted=True),
    ])
    with pytest.raises(ValueError):
        investigation.decode("corrupt", "wrong")
    assert investigation.completion == 0.0
    investigation.decode("corrupt", "genesis")
    assert investigation.completion == 1.0


def test_unknown_node_is_explicit():
    investigation = MerkleInvestigation([MerkleNode("known", NodeType.LEAF, "x")])
    with pytest.raises(KeyError, match="Unknown Merkle node"):
        investigation.scan("missing")
