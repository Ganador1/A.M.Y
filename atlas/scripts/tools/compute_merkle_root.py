#!/usr/bin/env python3
"""Compute a Merkle tree over all *.manifest.json files (excluding merkle_root.json) and emit merkle_root.json.

Deterministic ordering: sort by relative path.
Leaf hash: sha256 of raw file bytes.
Internal node: sha256( concat( left_hash + right_hash ) ) where hashes are hex strings encoded as ascii bytes.
If odd number of leaves, last is duplicated (classic Bitcoin-style) for stability.
"""
from __future__ import annotations
import argparse
import json
import hashlib
import pathlib
import datetime
import sys
from typing import List, Tuple

MANIFEST_GLOB = "*.manifest.json"
OUTPUT_FILE = "merkle_root.json"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_merkle_root(hashes: List[str]) -> Tuple[str, List[List[str]]]:
    """Return (root, levels) where levels[0] are leaves, last entry contains root.
    Each level: list of node hashes (hex)."""
    if not hashes:
        return "", []
    level = hashes[:]
    levels = [level]
    while len(level) > 1:
        nxt: List[str] = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else level[i]
            combined = (left + right).encode()
            nxt.append(sha256_hex(combined))
        level = nxt
        levels.append(level)
    return level[0], levels


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--models-dir", default="models", help="Directorio con manifests")
    p.add_argument("--output", default=OUTPUT_FILE, help="Archivo de salida JSON")
    args = p.parse_args()

    base = pathlib.Path(args.models_dir)
    if not base.is_dir():
        print(f"ERROR: No existe directorio {base}", file=sys.stderr)
        return 2

    manifests = sorted([p for p in base.glob(MANIFEST_GLOB) if p.name != OUTPUT_FILE])
    if not manifests:
        print("No se encontraron manifests.")
        data = {
            "algorithm": "sha256",
            "root": "",
            "generated_at": f"{datetime.datetime.utcnow().isoformat()}Z",
            "manifests": [],
        }
        pathlib.Path(args.output).write_text(
            json.dumps(data, indent=2, sort_keys=True), encoding="utf-8"
        )
        return 0

    leaves = []
    manifest_entries = []
    for m in manifests:
        b = m.read_bytes()
        h = sha256_hex(b)
        leaves.append(h)
        manifest_entries.append({"file": str(m), "hash": h})

    root, levels = build_merkle_root(leaves)

    out = {
        "algorithm": "sha256",
        "root": root,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "manifests": manifest_entries,
        "leaf_hashes": leaves,
        "tree_levels": levels,  # opcional ayuda para debug/verificación manual
    }
    pathlib.Path(args.output).write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"Merkle root: {root} ({len(leaves)} leaves)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
