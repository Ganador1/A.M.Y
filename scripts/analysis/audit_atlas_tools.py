#!/usr/bin/env python3
"""Audit Atlas tools through the same subprocess bridge A.M.Y uses.

The goal is not to prove every Atlas service is publishable science. It is to
separate operational, non-mock tool outputs from errors, placeholders, and
external/API-dependent calls so A.M.Y can avoid treating weak outputs as
evidence.
"""

from __future__ import annotations

import argparse
import asyncio
import ast
import json
import re
import time
from pathlib import Path
from typing import Any

from core.atlas_tools import ATLAS_RESULT_MARKER, AtlasTools, assess_tool_output

ROOT = Path(__file__).parent

WEAK_EVIDENCE_MARKERS = (
    "fallback",
    "heuristic",
    "simulated random",
    "requires full",
    "use axiom",
)

CURATED_TOOL_TESTS: list[dict[str, Any]] = [
    {
        "tool_name": "sympy_solve_equation",
        "tool_input": "x**2 - 4 = 0",
        "domain": "mathematics",
        "expected": ["2"],
    },
    {
        "tool_name": "sympy_simplify",
        "tool_input": "sin(x)**2 + cos(x)**2",
        "domain": "mathematics",
        "expected": ["1"],
    },
    {
        "tool_name": "sympy_prime_analysis",
        "tool_input": "is_prime:97",
        "domain": "mathematics",
        "expected": ["true"],
    },
    {
        "tool_name": "number_theory_advanced",
        "tool_input": "goldbach:100",
        "domain": "mathematics",
        "expected": ["verified"],
    },
    {
        "tool_name": "prime_gap_analysis",
        "tool_input": "50000",
        "domain": "mathematics",
        "expected": ["prime", "gap"],
    },
    {
        "tool_name": "calculus_engine",
        "tool_input": "limit:sin(x)/x:x->0",
        "domain": "mathematics",
        "expected": ["1"],
    },
    {
        "tool_name": "graph_theory",
        "tool_input": "chromatic:petersen",
        "domain": "mathematics",
        "expected": ["3"],
    },
    {
        "tool_name": "sequence_analyzer",
        "tool_input": "analyze:1,1,2,3,5,8,13",
        "domain": "mathematics",
        "expected": ["fibonacci"],
    },
    {
        "tool_name": "topology_invariants",
        "tool_input": "euler_char:torus",
        "domain": "mathematics",
        "expected": ["0"],
    },
    {
        "tool_name": "automated_prover",
        "tool_input": "induction:sum(1..n)=n*(n+1)/2",
        "domain": "mathematics",
        "expected": ["qed"],
    },
    {
        "tool_name": "molecular_weight_calc",
        "tool_input": "C6H12O6",
        "domain": "chemistry",
        "expected": ["180"],
    },
    {
        "tool_name": "computational_chemistry",
        "tool_input": "analyze_molecule:C6H6",
        "domain": "chemistry",
        "expected": ["78"],
    },
    {
        "tool_name": "bond_energy_analyzer",
        "tool_input": "C-C",
        "domain": "chemistry",
        "expected": ["347"],
    },
    {
        "tool_name": "molecular_orbital_energy",
        "tool_input": "6:1.4",
        "domain": "chemistry",
        "expected": ["mo analysis", "gap"],
    },
    {
        "tool_name": "gnome_materials",
        "tool_input": "stability:Li2O",
        "domain": "chemistry",
        "expected": ["li2o"],
        "known_limitations": ["placeholder service"],
    },
    {
        "tool_name": "dna_analyzer",
        "tool_input": "ATCGATCGATCGATCGATCG",
        "domain": "biology",
        "expected": ["20", "bp"],
    },
    {
        "tool_name": "protein_properties",
        "tool_input": "MVLSPADKTNVKAAWGKVGA",
        "domain": "biology",
        "expected": ["molecular"],
    },
    {
        "tool_name": "quantum_energy_levels",
        "tool_input": "hydrogen:3",
        "domain": "physics",
        "expected": ["-1.51"],
    },
    {
        "tool_name": "quantum_circuit",
        "tool_input": "bell:2",
        "domain": "physics",
        "expected": ["bell"],
    },
    {
        "tool_name": "numpy_correlation",
        "tool_input": "[1,2,3,4,5];[2,4,6,8,10]",
        "domain": "statistics",
        "expected": ["1.000000"],
    },
    {
        "tool_name": "numpy_distribution",
        "tool_input": "normal:1000,0,1",
        "domain": "statistics",
        "expected": ["normal"],
    },
    {
        "tool_name": "numpy_statistics",
        "tool_input": "summary:[1,2,3,4,5,6,7,8,9,10]",
        "domain": "statistics",
        "expected": ["5.5000"],
    },
    {
        "tool_name": "hypothesis_tester",
        "tool_input": "ttest: [1,2,3,4,5]: [3,4,5,6,7]",
        "domain": "statistics",
        "expected": ["t-statistic"],
    },
    {
        "tool_name": "validate_hypothesis",
        "tool_input": "mathematics:prime gaps are not normally distributed",
        "domain": "research",
        "expected": ["validation"],
        "known_limitations": ["heuristic validator"],
    },
]

EXTERNAL_OPTIONAL_CHECKS = [
    {
        "name": "search_literature",
        "reason": "Depends on network/API availability and literature indexes.",
    },
    {
        "name": "verify_hypothesis",
        "reason": "Depends on network/API availability and literature indexes.",
    },
]


def is_external_optional_tool(tool_name: str) -> bool:
    return tool_name.startswith("evidence_corroborate_") or tool_name.startswith("literature_")


def load_tool_tests(scope: str) -> list[dict[str, Any]]:
    if scope == "curated":
        return CURATED_TOOL_TESTS

    source = (ROOT / "test_atlas_exhaustive.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    raw_tests = None
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TOOL_TESTS":
                    raw_tests = ast.literal_eval(node.value)
                    break
        if raw_tests is not None:
            break
    if raw_tests is None:
        raise RuntimeError("Could not load TOOL_TESTS from test_atlas_exhaustive.py")

    cases = []
    for tool_name, test in raw_tests.items():
        is_external = is_external_optional_tool(tool_name)
        if scope == "all" and is_external:
            continue
        if scope == "external" and not is_external:
            continue
        cases.append(
            {
                "tool_name": tool_name,
                "tool_input": test["input"],
                "domain": test["domain"],
                "description": test.get("description", ""),
                "expected": [],
            }
        )
    return cases


def load_external_optional_tool_names(scope: str) -> list[str]:
    if scope == "curated":
        return [item["name"] for item in EXTERNAL_OPTIONAL_CHECKS]

    source = (ROOT / "test_atlas_exhaustive.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    raw_tests = None
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TOOL_TESTS":
                    raw_tests = ast.literal_eval(node.value)
                    break
        if raw_tests is not None:
            break
    if raw_tests is None:
        return [item["name"] for item in EXTERNAL_OPTIONAL_CHECKS]
    return sorted([name for name in raw_tests if is_external_optional_tool(name)])


def _weak_markers(output: object) -> list[str]:
    text = str(output or "").lower()
    return [marker for marker in WEAK_EVIDENCE_MARKERS if marker in text]


def _classify_result(case: dict[str, Any], output: object, elapsed: float) -> dict[str, Any]:
    text = str(output or "")
    text_lower = text.lower()
    expected = [str(item).lower() for item in case.get("expected", [])]
    expected_ok = all(item in text_lower for item in expected)
    assessment = assess_tool_output(text, tool_name=case["tool_name"])
    weak_markers = _weak_markers(text)
    limitations = list(case.get("known_limitations", []))

    is_external = is_external_optional_tool(case["tool_name"])
    if assessment["evidence_level"] == "weak" and expected_ok and not assessment["markers"][:-1]:
        status = "pass_but_suspicious"
    elif not assessment["usable"] or not expected_ok:
        status = "fail"
    elif is_external and _external_output_is_empty_or_weak(case["tool_name"], text):
        status = "pass_but_suspicious"
    elif is_external:
        status = "pass_external"
    elif weak_markers or limitations:
        status = "pass_but_suspicious"
    else:
        status = "pass_real"

    return {
        "tool_name": case["tool_name"],
        "domain": case["domain"],
        "tool_input": case["tool_input"],
        "status": status,
        "expected_ok": expected_ok,
        "unusable_markers": assessment["markers"],
        "weak_markers": weak_markers,
        "known_limitations": limitations,
        "elapsed_seconds": round(elapsed, 3),
        "output_preview": text[:700],
    }


def _external_output_is_empty_or_weak(tool_name: str, text: str) -> bool:
    text_lower = text.lower()
    if tool_name.startswith("literature_"):
        if '"results": []' in text_lower or '"sources": {}' in text_lower:
            return True
        return not any(marker in text_lower for marker in ('"results"', '"sources"', '"support_score"'))

    if tool_name.startswith("evidence_corroborate_"):
        if "top evidence:" not in text_lower:
            return True
        support = _extract_float_metric(text, "support_score")
        real_success = _extract_float_metric(text, "real_success_count")
        realism = _extract_float_metric(text, "tool_realism_score")
        if support is not None and support <= 0:
            return True
        if real_success is not None and real_success <= 0:
            return True
        if realism is not None and realism < 0.35:
            return True
        return not any(marker in text_lower for marker in ("support_score", "success=true", "success=True"))

    return False


def _extract_float_metric(text: str, metric: str) -> float | None:
    match = re.search(rf"{re.escape(metric)}:\s*([0-9]+(?:\.[0-9]+)?)", text)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


async def run_audit(scope: str = "curated") -> dict[str, Any]:
    tools = AtlasTools()
    started = time.time()
    test_cases = load_tool_tests(scope)
    external_optional_tool_names = load_external_optional_tool_names(scope)

    if not tools.available:
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "available": False,
            "error": "Atlas venv/root unavailable",
        }

    code = f"""
import asyncio, json, os, sys, time
sys.path.insert(0, {str((ROOT / 'atlas').resolve())!r})
os.chdir({str((ROOT / 'atlas').resolve())!r})
os.environ["ENABLE_REDIS_CACHE"] = "false"
os.environ.setdefault("LIT_HTTP_TIMEOUT", "8")
os.environ.setdefault("LIT_HTTP_MAX_RETRIES", "0")
from run_agent_with_tools import DynamicToolRegistry

CASES = {test_cases!r}
DOMAINS = [None, "mathematics", "physics", "chemistry", "biology", "statistics", "research"]

async def main():
    reg = DynamicToolRegistry()
    domains = {{}}
    for domain in DOMAINS:
        if domain is None:
            domains["all"] = reg.list_tools()
        else:
            domains[domain] = reg.list_tools_for_domain(domain)

    results = []
    for case in CASES:
        start = time.time()
        try:
            output = await asyncio.wait_for(
                reg.execute_tool(case["tool_name"], case["tool_input"]),
                timeout={75 if scope == "external" else 45},
            )
        except Exception as exc:
            output = "Audit Error: " + repr(exc)
        results.append({{
            "tool_name": case["tool_name"],
            "output": output,
            "elapsed_seconds": time.time() - start,
        }})

    print({ATLAS_RESULT_MARKER!r} + json.dumps({{"domains": domains, "results": results}}, default=str))

asyncio.run(main())
"""

    raw = tools._run_subprocess(code, timeout=900 if scope == "external" else 240)
    parsed = tools._parse_json_output(raw, {"error": "unparseable", "raw": raw[:1000]})
    if not isinstance(parsed, dict) or "results" not in parsed:
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "available": True,
            "error": "Atlas audit subprocess did not return results",
            "raw": raw[:1200],
        }

    outputs_by_name = {item["tool_name"]: item for item in parsed["results"]}
    classified = []
    for case in test_cases:
        result = outputs_by_name.get(case["tool_name"], {})
        classified.append(
            _classify_result(
                case,
                result.get("output", ""),
                float(result.get("elapsed_seconds", 0.0)),
            )
        )

    counts: dict[str, int] = {}
    for item in classified:
        counts[item["status"]] = counts.get(item["status"], 0) + 1

    domain_counts = {
        domain: len(names)
        for domain, names in (parsed.get("domains") or {}).items()
        if isinstance(names, list)
    }
    recommended_for_amy = [
        item["tool_name"] for item in classified if item["status"] == "pass_real"
    ]
    all_registered = set((parsed.get("domains") or {}).get("all") or [])
    tested = {case["tool_name"] for case in test_cases}

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "available": True,
        "scope": scope,
        "elapsed_seconds": round(time.time() - started, 3),
        "domain_counts": domain_counts,
        "untested_registered_tools": sorted(all_registered - tested),
        "summary": {
            "audited_tools": len(classified),
            "registered_tools": len(all_registered),
            "untested_registered_tools": len(all_registered - tested),
            **counts,
            "external_optional": len(external_optional_tool_names),
        },
        "recommended_for_amy": recommended_for_amy,
        "external_optional": external_optional_tool_names,
        "results": classified,
    }


def print_report(report: dict[str, Any]) -> None:
    print("Atlas tool audit")
    print(f"available: {report.get('available')}")
    if report.get("error"):
        print(f"error: {report['error']}")
        return

    print(f"elapsed_seconds: {report.get('elapsed_seconds')}")
    print(f"domain_counts: {json.dumps(report.get('domain_counts', {}), sort_keys=True)}")
    print(f"summary: {json.dumps(report.get('summary', {}), sort_keys=True)}")
    print()
    for item in report.get("results", []):
        print(
            f"{item['status']:20} {item['domain']:12} {item['tool_name']}"
            f" ({item['elapsed_seconds']}s)"
        )
        markers = item["unusable_markers"] or item["weak_markers"] or item["known_limitations"]
        if markers:
            print(f"  markers: {markers}")
        if item["status"] == "fail":
            print(f"  preview: {item['output_preview'][:220]}")


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=str(ROOT / "atlas_tool_validation_report.json"),
        help="Path to write the JSON audit report.",
    )
    parser.add_argument(
        "--scope",
        choices=("curated", "all", "external"),
        default="curated",
        help="curated runs evidence-grade smoke checks; all runs local cases; external runs literature/evidence cases.",
    )
    args = parser.parse_args()

    report = await run_audit(scope=args.scope)
    output_path = Path(args.output)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print_report(report)
    print(f"\nreport: {output_path}")
    return 0 if not report.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
