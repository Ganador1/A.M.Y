#!/usr/bin/env python3
import argparse
import json
import os
import re
from typing import Dict, List, Tuple


PATTERNS = {
    "bare_except": re.compile(r"(?m)^[ \t]*except\s*:\s*$"),
    "except_exception": re.compile(r"except\s+Exception(\s+as\s+|:)"),
    "raise_exception": re.compile(r"raise\s+Exception\s*\("),
    "any_types": re.compile(r"(:\s*Any\b|->\s*Any\b)")
}


def scan_file(path: str) -> Dict[str, int]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        return {k: 0 for k in PATTERNS.keys()}

    results = {}
    for name, pattern in PATTERNS.items():
        results[name] = len(pattern.findall(text))
    return results


def should_include(path: str, include_dirs: List[str]) -> bool:
    if not include_dirs:
        return True
    return any(os.path.join("app", d) in path for d in include_dirs)


def walk_and_scan(root: str, include_dirs: List[str]) -> Tuple[Dict[str, Dict[str, int]], Dict[str, int]]:
    per_file: Dict[str, Dict[str, int]] = {}
    totals = {k: 0 for k in PATTERNS.keys()}

    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            full = os.path.join(dirpath, fn)
            if not should_include(full, include_dirs):
                continue

            counts = scan_file(full)
            per_file[full] = counts
            for k, v in counts.items():
                totals[k] += v

    return per_file, totals


def summarize(per_file: Dict[str, Dict[str, int]], totals: Dict[str, int]) -> Dict:
    def top_offenders(metric: str, limit: int = 10) -> List[Tuple[str, int]]:
        ranked = sorted(((path, counts.get(metric, 0)) for path, counts in per_file.items()), key=lambda x: x[1], reverse=True)
        return [(p, c) for p, c in ranked if c > 0][:limit]

    summary = {
        "totals": totals,
        "top": {
            "bare_except": top_offenders("bare_except"),
            "except_exception": top_offenders("except_exception"),
            "raise_exception": top_offenders("raise_exception"),
            "any_types": top_offenders("any_types"),
        },
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description="Audit exception usage and Any types in the codebase.")
    parser.add_argument("--path", default="app", help="Root path to scan (default: app)")
    parser.add_argument("--include", nargs="*", default=["services", "routers", "autonomous", "scientific"], help="Subdirectories under app to include")
    parser.add_argument("--output", default=os.path.join("reports", "exception_audit.json"), help="JSON report output path")
    args = parser.parse_args()

    per_file, totals = walk_and_scan(args.path, args.include)
    summary = summarize(per_file, totals)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"per_file": per_file, "summary": summary}, f, indent=2)

    # Console summary for quick visibility
    print("Audit Summary:")
    print(f"TOTAL bare_except: {summary['summary']['totals']['bare_except'] if 'summary' in summary else totals['bare_except']}")
    print(f"TOTAL except_exception: {summary['totals']['except_exception']}")
    print(f"TOTAL raise_exception: {summary['totals']['raise_exception']}")
    print(f"TOTAL any_types: {summary['totals']['any_types']}")

    # Combined generic Exception metric (except + raise)
    generic_exception = summary['totals']['except_exception'] + summary['totals']['raise_exception']
    print(f"TOTAL generic_exception (except+raise): {generic_exception}")

    # Show top offenders quick list
    for metric in ("bare_except", "except_exception", "raise_exception", "any_types"):
        offenders = summary["top"][metric]
        if offenders:
            print(f"Top {metric} offenders:")
            for path, count in offenders[:5]:
                print(f"  {path}: {count}")


if __name__ == "__main__":
    main()