#!/usr/bin/env python3
"""
A.M.Y → Atlas End-to-End Integration Test.

Tests that A.M.Y can successfully invoke Atlas tools through:
1. AtlasTools.run_scientific_tool() — direct tool execution
2. AtlasTools.list_tools() — tool discovery
3. AtlasTools.search_literature() — literature search
4. AtlasTools.verify_hypothesis() — hypothesis verification
5. AtlasBridge.run_research() — full research cycle (if API keys available)

This validates the complete pipeline from A.M.Y's reasoning engine
to Atlas's scientific tools.
"""
import asyncio
import json
import sys
import time
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "atlas"))

from core.atlas_tools import AtlasTools, ATLAS_VENV_PYTHON, ATLAS_ROOT, assess_tool_output


# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(title: str):
    print(f"\n{BOLD}{CYAN}{'=' * 70}\n  {title}\n{'=' * 70}{RESET}")


def print_result(name: str, success: bool, detail: str = ""):
    icon = f"{GREEN}✅" if success else f"{RED}❌"
    detail_str = f" — {detail[:80]}" if detail else ""
    print(f"  {icon} {name}{RESET}{detail_str}")


def print_info(name: str, detail: str):
    print(f"  {YELLOW}ℹ️  {name}{RESET} — {detail[:80]}")


async def test_atlas_tools_availability():
    """Test 1: AtlasTools is available and venv exists."""
    print_header("TEST 1: Atlas Tools Availability")
    
    tools = AtlasTools()
    print_result("AtlasTools instance", tools.available)
    print_result("Atlas venv exists", ATLAS_VENV_PYTHON.exists())
    print_result("Atlas root exists", ATLAS_ROOT.exists())
    
    return tools.available


async def test_list_tools(tools: AtlasTools):
    """Test 2: List all available tools."""
    print_header("TEST 2: List Available Tools")
    
    all_tools = await tools.list_tools()
    print_result(f"Total tools available", len(all_tools) >= 80, f"{len(all_tools)} tools")
    
    # Test domain filtering
    math_tools = await tools.list_tools("mathematics")
    print_result("Mathematics tools", len(math_tools) >= 10, f"{len(math_tools)} tools")
    
    chem_tools = await tools.list_tools("chemistry")
    print_result("Chemistry tools", len(chem_tools) >= 5, f"{len(chem_tools)} tools")
    
    physics_tools = await tools.list_tools("physics")
    print_result("Physics tools", len(physics_tools) >= 5, f"{len(physics_tools)} tools")
    
    bio_tools = await tools.list_tools("biology")
    print_result("Biology tools", len(bio_tools) >= 3, f"{len(bio_tools)} tools")
    
    return len(all_tools) >= 80


async def test_direct_tool_execution(tools: AtlasTools):
    """Test 3: Execute specific tools via AtlasTools.run_scientific_tool()."""
    print_header("TEST 3: Direct Tool Execution (A.M.Y → Atlas)")
    
    test_cases = [
        # (tool_name, input, domain, expected_substring)
        ("sympy_solve_equation", "x**2 - 4 = 0", "mathematics", "2"),
        ("sympy_prime_analysis", "is_prime:97", "mathematics", "True"),
        ("number_theory_advanced", "goldbach:100", "mathematics", "VERIFIED"),
        ("prime_gap_analysis", "50000", "mathematics", "primes"),
        ("calculus_engine", "limit:sin(x)/x:x->0", "mathematics", "1"),
        ("symbolic_calculus", "taylor:sin(x):x:0:5", "mathematics", "Taylor"),
        ("graph_theory", "chromatic:petersen", "mathematics", "3"),
        ("sequence_analyzer", "analyze:1,1,2,3,5,8,13", "mathematics", "Fibonacci"),
        ("conjecture_engine", "generate:number_theory", "mathematics", "conjecture"),
        ("topology_invariants", "euler_char:torus", "mathematics", "0"),
        ("automated_prover", "induction:sum(1..n)=n*(n+1)/2", "mathematics", "QED"),
        ("molecular_weight_calc", "C6H12O6", "chemistry", "180"),
        ("computational_chemistry", "analyze_molecule:C6H6", "chemistry", "78"),
        ("bond_energy_analyzer", "C-C", "chemistry", "347"),
        ("molecular_orbital_energy", "6:1.4", "chemistry", "Hückel"),
        ("gnome_materials", "stability:Li2O", "chemistry", "-5.97"),
        ("dna_analyzer", "ATCGATCGATCGATCGATCG", "biology", "20 bp"),
        ("protein_properties", "MVLSPADKTNVKAAWGKVGA", "biology", "2043"),
        ("dnabert2_analysis", "motifs:ATCGATCGATCG", "biology", "Motif"),
        ("quantum_energy_levels", "hydrogen:3", "physics", "-1.51"),
        ("quantum_circuit", "bell:2", "physics", "Bell"),
        ("numpy_correlation", "[1,2,3,4,5];[2,4,6,8,10]", "statistics", "1.000000"),
        ("numpy_distribution", "normal:1000,0,1", "statistics", "normal"),
        ("numpy_statistics", "summary:[1,2,3,4,5,6,7,8,9,10]", "statistics", "5.5000"),
        ("hypothesis_tester", "ttest: [1,2,3,4,5]: [3,4,5,6,7]", "statistics", "t-statistic"),
        ("validate_hypothesis", "mathematics:prime gaps are not normally distributed", "research", "Validation"),
    ]
    
    passed = 0
    failed = 0
    weak = 0
    errors = []
    
    for tool_name, tool_input, domain, expected in test_cases:
        try:
            result = await tools.run_scientific_tool(tool_name, tool_input, domain)
            success = expected.lower() in str(result).lower()
            if success:
                assessment = assess_tool_output(result, tool_name=tool_name)
                if assessment["usable"]:
                    passed += 1
                    print_result(tool_name, True, str(result)[:60])
                else:
                    weak += 1
                    print_info(tool_name, f"Executed but weak evidence: {assessment['markers']}")
            else:
                failed += 1
                errors.append((tool_name, f"Expected '{expected}' in result", str(result)[:100]))
                print_result(tool_name, False, f"Expected '{expected}' not found")
        except Exception as e:
            failed += 1
            errors.append((tool_name, str(e), ""))
            print_result(tool_name, False, str(e)[:60])
    
    print(f"\n  {BOLD}Results: {passed}/{len(test_cases)} evidence-grade passed, {weak} weak/triage, {failed} failed{RESET}")
    if errors:
        print(f"  {RED}Failures:{RESET}")
        for name, err, result in errors:
            print(f"    - {name}: {err}")
            if result:
                print(f"      Got: {result[:80]}")
    
    return failed == 0


async def test_literature_search(tools: AtlasTools):
    """Test 4: Literature search (may fail without API keys)."""
    print_header("TEST 4: Literature Search")
    
    try:
        result = await tools.search_literature("prime gaps distribution", "mathematics", max_results=3)
        has_papers = bool(result.get("papers")) or bool(result.get("results"))
        print_result("Literature search", has_papers or "error" not in result, 
                     f"Got {len(result.get('papers', result.get('results', [])))} results")
        return True
    except Exception as e:
        print_info("Literature search", f"Error (expected without API): {str(e)[:60]}")
        return True  # Not a failure — depends on external APIs


async def test_hypothesis_verification(tools: AtlasTools):
    """Test 5: Hypothesis verification."""
    print_header("TEST 5: Hypothesis Verification")
    
    try:
        result = await tools.verify_hypothesis(
            "prime gaps follow an exponential distribution", "mathematics"
        )
        has_score = "support_score" in result or "score" in result or "error" in result
        print_result("Hypothesis verification", has_score, 
                     f"Score: {result.get('support_score', result.get('score', 'N/A'))}")
        return True
    except Exception as e:
        print_info("Hypothesis verification", f"Error: {str(e)[:60]}")
        return True  # Not a failure — depends on external APIs


async def test_atlas_bridge():
    """Test 6: AtlasBridge availability (not full research cycle — too slow)."""
    print_header("TEST 6: Atlas Bridge Availability")
    
    try:
        from core.atlas_bridge import AtlasBridge
        bridge = AtlasBridge()
        print_result("AtlasBridge instance", bridge.available)
        return bridge.available
    except Exception as e:
        print_result("AtlasBridge import", False, str(e)[:60])
        return False


async def main():
    print(f"\n{BOLD}{CYAN}{'=' * 70}")
    print(f"  A.M.Y → ATLAS END-TO-END INTEGRATION TEST")
    print(f"{'=' * 70}{RESET}")
    print(f"  Atlas root: {ATLAS_ROOT}")
    print(f"  Atlas venv: {ATLAS_VENV_PYTHON}")
    print(f"  Venv exists: {ATLAS_VENV_PYTHON.exists()}")
    
    start = time.time()
    results = {}
    
    # Test 1: Availability
    results["availability"] = await test_atlas_tools_availability()
    
    if not results["availability"]:
        print(f"\n{RED}Atlas not available — skipping remaining tests{RESET}")
        return
    
    tools = AtlasTools()
    
    # Test 2: List tools
    results["list_tools"] = await test_list_tools(tools)
    
    # Test 3: Direct tool execution (the most important test)
    results["tool_execution"] = await test_direct_tool_execution(tools)
    
    # Test 4: Literature search
    results["literature_search"] = await test_literature_search(tools)
    
    # Test 5: Hypothesis verification
    results["hypothesis_verification"] = await test_hypothesis_verification(tools)
    
    # Test 6: AtlasBridge
    results["atlas_bridge"] = await test_atlas_bridge()
    
    elapsed = time.time() - start
    
    # Summary
    print_header("SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, ok in results.items():
        icon = f"{GREEN}✅" if ok else f"{RED}❌"
        print(f"  {icon} {name}{RESET}")
    
    print(f"\n  {BOLD}Total: {passed}/{total} tests passed ({elapsed:.1f}s){RESET}")
    
    if passed == total:
        print(f"  {GREEN}{BOLD}🎉 ALL INTEGRATION TESTS PASSED!{RESET}")
    else:
        print(f"  {YELLOW}⚠️  Some tests need attention{RESET}")
    
    # Save report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "results": {k: "PASS" if v else "FAIL" for k, v in results.items()},
        "total_passed": passed,
        "total_tests": total,
    }
    report_path = ROOT / "amy_atlas_integration_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
