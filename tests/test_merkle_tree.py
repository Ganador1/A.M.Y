#!/usr/bin/env python3
"""Tests for the Merkle Tree engine."""
from __future__ import annotations

import pytest
from core.merkle import MerkleTree


def test_merkle_tree_single_leaf():
    tree = MerkleTree([b"single_leaf_data"])
    assert len(tree.root) == 64
    proof = tree.get_proof(0)
    assert len(proof) == 0  # 1 layer only
    assert MerkleTree.verify_proof(b"single_leaf_data", proof, tree.root) is True


def test_merkle_tree_multiple_leaves_and_proofs():
    leaves = [
        "5d1274581e6c35783536308f66f034a641cc7097200d425253801a4f509f9b66",
        "b8e1bc023f2ef67dc91c1adc303ed8eb884f4fc7f24baf1460a65f5e663f34ad",
        "4fa116958c84158d0d1724eadc62c0d1daee1fc9d7901bc5c2695b6fb5279f3b",
        "d7acb68a463375ee41ac1ca53f1202d05faf58b0ef7e8b7bd4954de8d00fdb6e",
        "7bafc7494784073545a1054bebed3b0ef6d7bda0a408b4d7f35ff8b08ee9d1a5",
    ]
    tree = MerkleTree(leaves)
    assert len(tree.root) == 64

    # Verify proof for each leaf
    for idx, leaf in enumerate(leaves):
        proof = tree.get_proof(idx)
        assert MerkleTree.verify_proof(leaf, proof, tree.root) is True
        # Proof by leaf content
        proof_by_leaf = tree.get_proof_for_leaf(leaf)
        assert MerkleTree.verify_proof(leaf, proof_by_leaf, tree.root) is True

    # Tampered leaf must fail verification
    assert MerkleTree.verify_proof("0" * 64, tree.get_proof(0), tree.root) is False
    # Wrong root must fail verification
    assert MerkleTree.verify_proof(leaves[0], tree.get_proof(0), "f" * 64) is False


def test_merkle_tree_empty_raises():
    with pytest.raises(ValueError, match="cannot construct MerkleTree with zero leaves"):
        MerkleTree([])


def test_merkle_tree_to_dict():
    leaves = [b"leaf1", b"leaf2"]
    tree = MerkleTree(leaves)
    d = tree.to_dict()
    assert d["merkle_root"] == tree.root
    assert d["leaf_count"] == 2
    assert len(d["leaf_hashes"]) == 2
