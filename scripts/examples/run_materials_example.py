#!/usr/bin/env python3
"""Materials tools.

Requires the Atlas worker and PyMatGen for structure calculations. The legacy GNoME-named tool is a tabulated lookup, not access to a trained GNoME model.
Run with --list to inspect the examples without loading Atlas.
Configure AMY_ATLAS_ROOT and AMY_ATLAS_PYTHON as described in ENVIRONMENT.md.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DOMAIN = 'materials_science'
CASES = [('pymatgen_structure', 'TiO2', 'Fixed rutile prototype: a=4.594, c=2.958 angstrom. No structure search or optimization is performed.'), ('gnome_materials', 'properties:TiO2', 'Tabulated reference lookup, intentionally classified as weak evidence by AMY. Not an ML prediction or discovery.')]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="Show inputs and scope without running tools")
    parser.add_argument("--tool", choices=[case[0] for case in CASES], help="Run only this example")
    parser.add_argument("--timeout", type=float, default=120.0, help="Maximum seconds per tool (default: 120)")
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and positive")
    return args


async def main(argv=None) -> int:
    args = parse_args(argv)
    cases = [case for case in CASES if args.tool is None or case[0] == args.tool]
    if args.list:
        print(json.dumps([{"tool": tool, "input": query, "scope": scope}
                          for tool, query, scope in cases], indent=2))
        return 0

    from core.atlas_tools import AtlasTools, assess_tool_output

    atlas = AtlasTools()
    if not atlas.available:
        print("Atlas worker unavailable. Configure its source root and Python environment; see ENVIRONMENT.md.", file=sys.stderr)
        return 2

    failures = 0
    try:
        for tool, query, scope in cases:
            print(f"\n{tool}\nInput: {query}\nScope: {scope}")
            try:
                result = await asyncio.wait_for(
                    atlas.run_scientific_tool(tool, query, domain=DOMAIN),
                    timeout=args.timeout,
                )
            except (TimeoutError, RuntimeError, OSError) as exc:
                print(f"Tool failed: {type(exc).__name__}: {exc}", file=sys.stderr)
                failures += 1
                continue
            print(result)
            assessment = assess_tool_output(result, tool, tool_input=query)
            print("AMY output assessment: " + json.dumps(assessment, sort_keys=True))
            # A tabulated lookup demonstrates the evidence boundary rather than a new prediction.
            expected_weak_lookup = (
                tool == "gnome_materials"
                and assessment.get("markers") == ["known weak evidence tool"]
            )
            if not assessment["usable"] and not expected_weak_lookup:
                failures += 1
        print("\nOperational completion does not establish novelty or independent scientific verification.")
        return 1 if failures else 0
    finally:
        await atlas.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
