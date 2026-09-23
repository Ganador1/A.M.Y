#!/usr/bin/env python3
"""Build a deterministic reproducible bundle (tar.gz) containing:
 - All manifests (models/*.manifest.json)
 - merkle_root.json (if exists)
 - Optionally referenced model artifacts listed inside manifests (field artifacts -> list of paths)
Generates bundle metadata JSON with SHA-256 hashes and final bundle hash.
Determinism strategies: sorted file list, fixed mtime=0, owner/group=0.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import tarfile
import pathlib
import time
import sys
import io

BUNDLE_DIR = pathlib.Path("dist")
BUNDLE_META = BUNDLE_DIR / "bundle_metadata.json"
DEFAULT_NAME = "repro_bundle"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect_files(models_dir: pathlib.Path, include_artifacts: bool) -> list[pathlib.Path]:
    manifests = sorted(models_dir.glob("*.manifest.json"))
    files = list(manifests)
    merkle = models_dir / "merkle_root.json"
    if merkle.is_file():
        files.append(merkle)
    if include_artifacts:
        for m in manifests:
            txt = m.read_text(encoding="utf-8")
            try:
                obj = json.loads(txt)
            except json.JSONDecodeError:
                continue
            for art in obj.get("artifacts", []):
                p = pathlib.Path(art)
                if p.is_file():
                    files.append(p)
    # deduplicate
    uniq = []
    seen = set()
    for f in files:
        if f not in seen:
            uniq.append(f)
            seen.add(f)
    return sorted(uniq)


def add_file(tar: tarfile.TarFile, path: pathlib.Path, arcname: str):
    """Add a file with deterministic metadata."""
    data = path.read_bytes()
    info = tarfile.TarInfo(name=arcname)
    info.size = len(data)
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    tar.addfile(info, io.BytesIO(data))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--models-dir", default="models")
    p.add_argument("--name", default=DEFAULT_NAME)
    p.add_argument("--include-artifacts", action="store_true")
    args = p.parse_args()

    models_dir = pathlib.Path(args.models_dir)
    if not models_dir.is_dir():
        print(f"ERROR no existe {models_dir}", file=sys.stderr)
        return 2

    files = collect_files(models_dir, args.include_artifacts)
    if not files:
        print("No files to bundle")
        return 0

    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    bundle_name = f"{args.name}_{ts}.tar.gz"
    bundle_path = BUNDLE_DIR / bundle_name

    # Build tar deterministically
    with tarfile.open(bundle_path, mode="w:gz", compresslevel=9, format=tarfile.GNU_FORMAT) as tar:
        for f in files:
            rel = f.relative_to('.') if not f.is_absolute() else f
            arc = str(rel)
            add_file(tar, f, arc)

    bundle_hash = sha256_hex(bundle_path.read_bytes())

    manifest = {
        "generated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "files": [
            {"path": str(f), "sha256": sha256_hex(f.read_bytes())} for f in files
        ],
        "bundle": {"file": str(bundle_path), "sha256": bundle_hash},
        "include_artifacts": args.include_artifacts,
    }
    BUNDLE_META.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Bundle creado: {bundle_path} sha256={bundle_hash}")
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
