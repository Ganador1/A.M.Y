#!/usr/bin/env python3
"""
Audit services for async migration prioritization.

This script analyzes all services in the codebase to identify which ones
should be prioritized for async migration based on I/O patterns, CPU usage,
and current async/sync ratio.
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set
import sys


def analyze_service_file(filepath: Path) -> Dict[str, Any]:
    """Analyze a service file for async migration potential."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e), "filepath": str(filepath)}
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {"error": f"Syntax error: {e}", "filepath": str(filepath)}
    
    stats = {
        "filepath": str(filepath),
        "total_functions": 0,
        "async_functions": 0,
        "sync_functions": 0,
        "has_db_queries": False,
        "has_http_calls": False,
        "has_file_io": False,
        "has_cpu_intensive": False,
        "has_time_sleep": False,
        "has_external_apis": False,
        "priority_score": 0,
        "migration_difficulty": "low",
        "recommended_approach": "async",
        "blocking_patterns": [],
        "async_ratio": 0.0,
    }
    
    # Analyze functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            stats["total_functions"] += 1
            stats["sync_functions"] += 1
        elif isinstance(node, ast.AsyncFunctionDef):
            stats["total_functions"] += 1
            stats["async_functions"] += 1
    
    # Calculate async ratio
    if stats["total_functions"] > 0:
        stats["async_ratio"] = stats["async_functions"] / stats["total_functions"]
    
    # Check for I/O patterns
    patterns = {
        "has_db_queries": [
            r"db\.query\(",
            r"session\.execute\(",
            r"session\.add\(",
            r"session\.commit\(",
            r"\.filter\(",
            r"\.all\(",
            r"\.first\(",
            r"\.scalar\(",
        ],
        "has_http_calls": [
            r"requests\.",
            r"urllib\.",
            r"httpx\.",
            r"aiohttp\.",
            r"client\.get\(",
            r"client\.post\(",
            r"\.json\(",
        ],
        "has_file_io": [
            r"open\(",
            r"\.read\(",
            r"\.write\(",
            r"\.save\(",
            r"\.load\(",
            r"Path\(",
            r"\.exists\(",
            r"\.mkdir\(",
        ],
        "has_cpu_intensive": [
            r"sympy\.",
            r"numpy\.",
            r"scipy\.",
            r"sklearn\.",
            r"torch\.",
            r"tensorflow\.",
            r"qiskit\.",
            r"matplotlib\.",
            r"\.fit\(",
            r"\.predict\(",
            r"\.train\(",
        ],
        "has_time_sleep": [
            r"time\.sleep\(",
            r"asyncio\.sleep\(",
        ],
        "has_external_apis": [
            r"uniprot",
            r"pubchem",
            r"pubmed",
            r"arxiv",
            r"doi",
            r"api\.",
            r"\.com/",
            r"https://",
            r"http://",
        ],
    }
    
    # Check patterns
    for pattern_name, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, content, re.IGNORECASE):
                stats[pattern_name] = True
                break
    
    # Calculate priority score
    score = 0
    
    # High priority: I/O operations
    if stats["has_db_queries"]:
        score += 5
        stats["blocking_patterns"].append("database_queries")
    
    if stats["has_http_calls"]:
        score += 8
        stats["blocking_patterns"].append("http_calls")
    
    if stats["has_external_apis"]:
        score += 6
        stats["blocking_patterns"].append("external_apis")
    
    if stats["has_file_io"]:
        score += 3
        stats["blocking_patterns"].append("file_io")
    
    # Medium priority: CPU-intensive operations
    if stats["has_cpu_intensive"]:
        score += 4
        stats["blocking_patterns"].append("cpu_intensive")
    
    # Low priority: time.sleep (already handled)
    if stats["has_time_sleep"]:
        score += 2
        stats["blocking_patterns"].append("time_sleep")
    
    # Bonus for already having some async functions
    if stats["async_ratio"] > 0.3:
        score += 2
    elif stats["async_ratio"] > 0.1:
        score += 1
    
    # Penalty for high sync ratio
    if stats["async_ratio"] < 0.1 and stats["total_functions"] > 5:
        score += 1  # Higher priority to migrate
    
    stats["priority_score"] = score
    
    # Determine migration difficulty
    if stats["total_functions"] > 20:
        stats["migration_difficulty"] = "high"
    elif stats["total_functions"] > 10:
        stats["migration_difficulty"] = "medium"
    else:
        stats["migration_difficulty"] = "low"
    
    # Determine recommended approach
    if stats["has_cpu_intensive"] and not stats["has_db_queries"] and not stats["has_http_calls"]:
        stats["recommended_approach"] = "executor"
    elif stats["has_db_queries"] or stats["has_http_calls"]:
        stats["recommended_approach"] = "async"
    else:
        stats["recommended_approach"] = "low_priority"
    
    return stats


def find_service_files() -> List[Path]:
    """Find all service files in the codebase."""
    project_root = Path(__file__).parent.parent.parent
    service_files = []
    
    # Search in app directory
    for py_file in project_root.glob("app/**/*.py"):
        # Skip __pycache__ and test files
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue
        
        # Look for service files
        if (
            "service" in py_file.name.lower() or
            "connector" in py_file.name.lower() or
            "adapter" in py_file.name.lower() or
            "client" in py_file.name.lower() or
            "manager" in py_file.name.lower() or
            "handler" in py_file.name.lower()
        ):
            service_files.append(py_file)
    
    return service_files


def generate_migration_plan(analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a migration plan based on analysis results."""
    
    # Sort by priority score
    sorted_results = sorted(analysis_results, key=lambda x: x.get("priority_score", 0), reverse=True)
    
    # Group by recommended approach
    by_approach = {
        "async": [],
        "executor": [],
        "low_priority": []
    }
    
    for result in sorted_results:
        if "error" not in result:
            approach = result.get("recommended_approach", "low_priority")
            by_approach[approach].append(result)
    
    # Generate phases
    phases = {
        "phase_1_critical": [],  # High priority, async approach
        "phase_2_cpu_bound": [],  # CPU-intensive, executor approach
        "phase_3_remaining": [],  # Remaining async
        "phase_4_low_priority": []  # Low priority
    }
    
    # Phase 1: Critical async migrations (top 10)
    phases["phase_1_critical"] = by_approach["async"][:10]
    
    # Phase 2: CPU-bound services (top 5)
    phases["phase_2_cpu_bound"] = by_approach["executor"][:5]
    
    # Phase 3: Remaining async
    phases["phase_3_remaining"] = by_approach["async"][10:]
    
    # Phase 4: Low priority
    phases["phase_4_low_priority"] = by_approach["low_priority"]
    
    return {
        "total_services": len([r for r in analysis_results if "error" not in r]),
        "by_approach": by_approach,
        "phases": phases,
        "summary": {
            "high_priority_async": len(phases["phase_1_critical"]),
            "cpu_bound_executor": len(phases["phase_2_cpu_bound"]),
            "remaining_async": len(phases["phase_3_remaining"]),
            "low_priority": len(phases["phase_4_low_priority"]),
        }
    }


def main():
    """Main entry point for the service audit."""
    print("🔍 Auditing services for async migration prioritization...")
    print("=" * 70)
    
    # Find service files
    service_files = find_service_files()
    print(f"📁 Found {len(service_files)} service files")
    print()
    
    # Analyze each file
    analysis_results = []
    for file_path in service_files:
        print(f"📊 Analyzing {file_path}...")
        result = analyze_service_file(file_path)
        analysis_results.append(result)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"  - Functions: {result['total_functions']} total, {result['async_functions']} async ({result['async_ratio']:.1%})")
            print(f"  - Patterns: {', '.join(result['blocking_patterns']) if result['blocking_patterns'] else 'none'}")
            print(f"  - Priority: {result['priority_score']}, Approach: {result['recommended_approach']}")
        print()
    
    # Generate migration plan
    migration_plan = generate_migration_plan(analysis_results)
    
    # Save results
    output_file = Path(__file__).parent.parent.parent / "reports" / "async_migration_audit.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            "analysis_results": analysis_results,
            "migration_plan": migration_plan,
            "summary": migration_plan["summary"]
        }, f, indent=2)
    
    # Print summary
    print("=" * 70)
    print("📋 MIGRATION PLAN SUMMARY")
    print("=" * 70)
    
    summary = migration_plan["summary"]
    print(f"Total services analyzed: {migration_plan['total_services']}")
    print(f"Phase 1 (Critical Async): {summary['high_priority_async']} services")
    print(f"Phase 2 (CPU-bound Executor): {summary['cpu_bound_executor']} services")
    print(f"Phase 3 (Remaining Async): {summary['remaining_async']} services")
    print(f"Phase 4 (Low Priority): {summary['low_priority']} services")
    print()
    
    # Top 10 services to migrate
    print("🎯 TOP 10 SERVICES TO MIGRATE (Phase 1):")
    for i, service in enumerate(migration_plan["phases"]["phase_1_critical"], 1):
        print(f"{i:2d}. {service['filepath']}")
        print(f"    Priority: {service['priority_score']}, Functions: {service['total_functions']}, Async: {service['async_ratio']:.1%}")
        print(f"    Patterns: {', '.join(service['blocking_patterns'])}")
        print()
    
    print(f"📄 Full report saved to: {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
