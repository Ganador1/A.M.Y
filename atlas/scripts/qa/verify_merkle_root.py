#!/usr/bin/env python3
"""Verify merkle_root.json against current manifests.

Exit codes:
 0 = OK / matches
 1 = mismatch or structural problem
 2 = usage / directory not found
"""
from __future__ import annotations
import argparse
import json
import hashlib
import pathlib
import sys
from typing import List

MANIFEST_GLOB = "*.manifest.json"
DEFAULT_FILE = "merkle_root.json"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rebuild_leaves(manifests):
    leaves = []
    entries = []
    for m in manifests:
        b = m.read_bytes()
        h = sha256_hex(b)
        leaves.append(h)
        entries.append({"file": str(m), "hash": h})
    return leaves, entries


def build_merkle_root(hashes: List[str]) -> str:
    if not hashes:
        return ""
    level = hashes[:]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else level[i]
            nxt.append(sha256_hex((left + right).encode()))
        level = nxt
    return level[0]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--models-dir", default="models")
    p.add_argument("--file", default=DEFAULT_FILE, help="Archivo merkle_root.json")
    args = p.parse_args()

    base = pathlib.Path(args.models_dir)
    if not base.is_dir():
        print(f"ERROR: No existe directorio {base}", file=sys.stderr)
        return 2

    target = pathlib.Path(args.file)
    if not target.is_file():
        print(f"ERROR: No existe archivo {target}", file=sys.stderr)
        return 2

    data = json.loads(target.read_text(encoding="utf-8"))
    expected_root = data.get("root", "")
    stored_manifests = {e["file"]: e["hash"] for e in data.get("manifests", [])}

    manifests = sorted([p for p in base.glob(MANIFEST_GLOB) if p.name != args.file])
    if not manifests:
        print("ADVERTENCIA: No hay manifests en disco, raíz esperada vacía")
        return 0 if expected_root == "" else 1

    leaves, entries = rebuild_leaves(manifests)
    current_root = build_merkle_root(leaves)

    ok = True

    if current_root != expected_root:
        print(f"MISMATCH: root actual {current_root} ≠ {expected_root}")
        ok = False

    # Revisa integridad de hashes individuales
    for e in entries:
        recorded = stored_manifests.get(e["file"])  # puede contener path completo
        if recorded is None:
            print(f"FALTA entrada para {e['file']}")
            ok = False
        elif recorded != e["hash"]:
            print(f"HASH MISMATCH {e['file']} registrado={recorded} actual={e['hash']}")
            ok = False

    print("VERIFICACIÓN OK" if ok else "VERIFICACIÓN FALLÓ")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
