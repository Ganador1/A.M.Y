"""Verify the curated witness without changing any package file."""
from pathlib import Path
from fractions import Fraction
import copy
import hashlib
import json
import exact_verifier

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    for name, expected in manifest["sha256"].items():
        path = ROOT / name
        if path.parent != ROOT or path.is_symlink():
            raise ValueError("invalid manifest path")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("package hash mismatch: " + name)
    document = json.loads((ROOT / "candidate.json").read_text())
    result = exact_verifier.verify_document(document)
    if result["exact_ratio"] < Fraction("0.40863826"):
        raise ValueError("displayed lower bound exceeds witness")
    if result["exact_ratio"] <= Fraction(2378625, 5958277):
        raise ValueError("no improvement over pinned baseline")
    controls = []
    for label in ("inflated_ratio", "changed_height"):
        mutated = copy.deepcopy(document)
        if label == "inflated_ratio":
            mutated["exact_ratio"] = str(Fraction(document["exact_ratio"]) + Fraction(1, 1000))
        else:
            mutated["heights_over_denom"][0] = str(Fraction(mutated["heights_over_denom"][0]) + 1)
        try:
            exact_verifier.verify_document(mutated)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError("corruption accepted: " + label)
    print(json.dumps({"passed": True, "exact_ratio": str(result["exact_ratio"]),
                      "certified_display_lower_bound": "0.40863826", "n": result["n"],
                      "nodes_checked": result["nodes_checked"], "midpoints_checked": result["midpoints_checked"],
                      "negative_controls_rejected": controls, "worldwide_priority_verified": False,
                      "full_search_lineage_verified": False}, indent=2))


if __name__ == "__main__":
    main()
