"""
Merkle Tree Engine — Tamper-evident hierarchical hashing for A.M.Y.

Supports:
- RFC 6962 domain-separated hashing (preventing second-preimage attacks)
- Inclusion proof generation and O(log N) offline verification
- Digest-bound grouping of experiment outputs, artifacts, and paper claims
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Sequence

_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
LEAF_PREFIX = bytes([0])
NODE_PREFIX = bytes([1])


def _hash_leaf(data: bytes) -> bytes:
    """RFC 6962 domain separation for leaf node: SHA-256(0x00 || data)"""
    return hashlib.sha256(LEAF_PREFIX + data).digest()


def _hash_internal(left: bytes, right: bytes) -> bytes:
    """RFC 6962 domain separation for internal node: SHA-256(0x01 || left || right)"""
    return hashlib.sha256(NODE_PREFIX + left + right).digest()


def _normalize_leaf_to_bytes(leaf: str | bytes) -> bytes:
    if isinstance(leaf, bytes):
        return leaf
    if isinstance(leaf, str):
        if _HEX_SHA256.fullmatch(leaf.strip()):
            return bytes.fromhex(leaf.strip().lower())
        return leaf.encode("utf-8")
    raise TypeError(f"unsupported leaf type: {type(leaf).__name__}")


class MerkleTree:
    """Deterministic binary Merkle Tree."""

    def __init__(self, leaves: Sequence[str | bytes]):
        if not leaves:
            raise ValueError("cannot construct MerkleTree with zero leaves")
        self.raw_leaves = list(leaves)
        self.leaf_bytes = [_normalize_leaf_to_bytes(l) for l in leaves]
        self.leaf_hashes = [_hash_leaf(b) for b in self.leaf_bytes]
        self.layers: list[list[bytes]] = [self.leaf_hashes]
        self._build_tree()

    def _build_tree(self) -> None:
        current = self.leaf_hashes
        while len(current) > 1:
            next_layer: list[bytes] = []
            for i in range(0, len(current), 2):
                left = current[i]
                if i + 1 < len(current):
                    right = current[i + 1]
                else:
                    right = current[i]
                next_layer.append(_hash_internal(left, right))
            self.layers.append(next_layer)
            current = next_layer

    @property
    def root(self) -> str:
        """Return the Merkle Root as a 64-character lowercase hex string."""
        return self.layers[-1][0].hex()

    @property
    def root_bytes(self) -> bytes:
        return self.layers[-1][0]

    def get_proof(self, index: int) -> list[dict[str, str]]:
        """Generate an audit / inclusion proof for leaf at index."""
        if not (0 <= index < len(self.leaf_hashes)):
            raise IndexError(f"leaf index {index} out of bounds (0..{len(self.leaf_hashes)-1})")
        proof: list[dict[str, str]] = []
        current_idx = index
        for layer in self.layers[:-1]:
            is_right_child = (current_idx % 2 == 1)
            if is_right_child:
                sibling_idx = current_idx - 1
                position = "left"
            else:
                sibling_idx = current_idx + 1 if current_idx + 1 < len(layer) else current_idx
                position = "right"
            sibling_hash = layer[sibling_idx].hex()
            proof.append({"position": position, "hash": sibling_hash})
            current_idx //= 2
        return proof

    def get_proof_for_leaf(self, leaf: str | bytes) -> list[dict[str, str]]:
        """Find leaf and generate inclusion proof."""
        norm = _normalize_leaf_to_bytes(leaf)
        target_hash = _hash_leaf(norm)
        for idx, h in enumerate(self.leaf_hashes):
            if h == target_hash:
                return self.get_proof(idx)
        raise ValueError("leaf not found in tree")

    @classmethod
    def verify_proof(
        cls,
        leaf: str | bytes,
        proof: list[dict[str, str]],
        root_hex: str,
    ) -> bool:
        """Verify an inclusion proof offline against a known Merkle Root."""
        try:
            norm = _normalize_leaf_to_bytes(leaf)
            current = _hash_leaf(norm)
            for step in proof:
                sibling = bytes.fromhex(step["hash"])
                pos = step["position"]
                if pos == "left":
                    current = _hash_internal(sibling, current)
                elif pos == "right":
                    current = _hash_internal(current, sibling)
                else:
                    return False
            return current.hex() == root_hex.lower().strip()
        except Exception:
            return False

    def to_dict(self) -> dict[str, Any]:
        """Serialize tree metadata for publication / inclusion in manifests."""
        return {
            "merkle_root": self.root,
            "algorithm": "sha256-rfc6962",
            "leaf_count": len(self.raw_leaves),
            "leaf_hashes": [h.hex() for h in self.leaf_hashes],
        }
