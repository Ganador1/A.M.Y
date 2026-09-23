#!/usr/bin/env python3
"""Mathematics tools.

Requires the Atlas worker with SymPy, NumPy and SciPy. These are finite calculations, not discovery or proof of a general conjecture.
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

DOMAIN = 'mathematics'
CASES = [('sympy_solve_equation', 'x**2 - 5*x + 6 = 0', 'Solve a polynomial equation; expected roots are 2 and 3.'), ('prime_gap_analysis', '1000', 'Enumerate primes and gaps only up to the specified finite limit.'), ('hypothesis_tester', 'ttest:[2.5,2.8,3.1,2.9,3.2,2.7,3.0]:[1.8,2.1,2.0,1.9,2.2,1.7,2.0]', 'Two independent synthetic samples; SciPy equal-variance t-test, not a clinical inference.')]


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
