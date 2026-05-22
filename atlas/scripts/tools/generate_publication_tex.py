#!/usr/bin/env python3
"""Generate publication LaTeX with embedded integrity metadata.

Reads merkle_root.json, bundle_metadata.json and git info to populate template placeholders.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import subprocess
import datetime
import sys

DEFAULT_TEMPLATE = "publications/template.tex"
DEFAULT_OUTPUT = "publications/output.tex"
MERKLE_FILE = "models/merkle_root.json"
BUNDLE_META = "dist/bundle_metadata.json"


def get_git_commit() -> str:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return result.stdout.strip()[:8]
    except FileNotFoundError:
        pass
    return "unknown"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--template", default=DEFAULT_TEMPLATE)
    p.add_argument("--output", default=DEFAULT_OUTPUT)
    p.add_argument("--merkle-file", default=MERKLE_FILE)
    p.add_argument("--bundle-meta", default=BUNDLE_META)
    args = p.parse_args()

    template_path = pathlib.Path(args.template)
    if not template_path.is_file():
        print(f"ERROR: Template no encontrado: {template_path}", file=sys.stderr)
        return 2

    # Read template content
    content = template_path.read_text(encoding="utf-8")

    # Get Merkle root
    merkle_root = "not-computed"
    merkle_path = pathlib.Path(args.merkle_file)
    if merkle_path.is_file():
        try:
            merkle_data = json.loads(merkle_path.read_text(encoding="utf-8"))
            merkle_root = merkle_data.get("root", "invalid-format")[:16] + "..."
        except Exception:  # noqa: BLE001
            merkle_root = "parse-error"

    # Get bundle hash
    bundle_hash = "not-built"
    bundle_path = pathlib.Path(args.bundle_meta)
    if bundle_path.is_file():
        try:
            bundle_data = json.loads(bundle_path.read_text(encoding="utf-8"))
            full_hash = bundle_data.get("bundle", {}).get("sha256", "invalid-format")
            bundle_hash = full_hash[:16] + "..." if len(full_hash) > 16 else full_hash
        except Exception:  # noqa: BLE001
            bundle_hash = "parse-error"

    # Get git commit and timestamp
    git_commit = get_git_commit()
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Replace placeholders
    replacements = {
        "MERKLE_ROOT_PLACEHOLDER": merkle_root,
        "BUNDLE_HASH_PLACEHOLDER": bundle_hash,
        "TIMESTAMP_PLACEHOLDER": timestamp,
        "GIT_COMMIT_PLACEHOLDER": git_commit,
    }

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    # Write output
    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    print(f"Generated: {output_path}")
    print(f"  Merkle: {merkle_root}")
    print(f"  Bundle: {bundle_hash}")
    print(f"  Commit: {git_commit}")
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
