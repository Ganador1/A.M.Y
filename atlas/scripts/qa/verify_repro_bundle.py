#!/usr/bin/env python3
"""Verify reproducible bundle integrity.

Steps:
 1. Re-hash listed files and compare with metadata.
 2. Re-hash the bundle file itself (if present) and compare.
Exit codes: 0 ok, 1 mismatch, 2 usage error.
"""
from __future__ import annotations
import argparse
import json
import hashlib
import pathlib
import sys

BUNDLE_META = pathlib.Path("dist/bundle_metadata.json")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", default=str(BUNDLE_META))
    args = p.parse_args()

    meta_path = pathlib.Path(args.metadata)
    if not meta_path.is_file():
        print(f"ERROR metadata no existe: {meta_path}", file=sys.stderr)
        return 2

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    files = meta.get("files", [])
    ok = True
    for entry in files:
        path = pathlib.Path(entry["path"]) if isinstance(entry, dict) else None
        if not path or not path.is_file():
            print(f"FALTA archivo listado: {entry}")
            ok = False
            continue
        current = sha256_hex(path.read_bytes())
        if current != entry.get("sha256"):
            print(f"MISMATCH {path} esperado={entry.get('sha256')} actual={current}")
            ok = False

    bundle_info = meta.get("bundle", {})
    bundle_file = pathlib.Path(bundle_info.get("file", ""))
    if bundle_file.is_file():
        bh = sha256_hex(bundle_file.read_bytes())
        if bh != bundle_info.get("sha256"):
            print(f"MISMATCH BUNDLE esperado={bundle_info.get('sha256')} actual={bh}")
            ok = False
    else:
        print("ADVERTENCIA: archivo bundle ausente (se verifica solo contenido listado)")

    print("BUNDLE OK" if ok else "BUNDLE FAIL")
    return 0 if ok else 1

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
