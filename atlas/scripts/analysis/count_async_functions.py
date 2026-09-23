#!/usr/bin/env python3
"""
Count Async Functions Script for AXIOM ATLAS.

This script analyzes the codebase to count async vs sync functions
and calculate the async/sync ratio.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Any
import json


def analyze_file_for_async_functions(filepath: Path) -> Dict[str, Any]:
    """Analyze a file for async vs sync functions."""
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
        "async_ratio": 0.0,
        "functions": []
    }
    
    # Analyze functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            stats["total_functions"] += 1
            stats["sync_functions"] += 1
            
            func_info = {
                "name": node.name,
                "line": node.lineno,
                "is_async": False,
                "type": "sync"
            }
            stats["functions"].append(func_info)
            
        elif isinstance(node, ast.AsyncFunctionDef):
            stats["total_functions"] += 1
            stats["async_functions"] += 1
            
            func_info = {
                "name": node.name,
                "line": node.lineno,
                "is_async": True,
                "type": "async"
            }
            stats["functions"].append(func_info)
    
    # Calculate async ratio
    if stats["total_functions"] > 0:
        stats["async_ratio"] = stats["async_functions"] / stats["total_functions"]
    
    return stats


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in directory."""
    python_files = []
    
    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and test files for main analysis
        if "__pycache__" in str(py_file):
            continue
        python_files.append(py_file)
    
    return python_files


def main():
    """Main entry point for async function counting."""
    print("🔍 Analyzing async/sync function ratio...")
    print("=" * 60)
    
    # Find all Python files
    project_root = Path(__file__).parent.parent.parent
    python_files = find_python_files(project_root / "app")
    
    print(f"📁 Found {len(python_files)} Python files in app/")
    
    # Analyze each file
    all_stats = []
    total_functions = 0
    total_async_functions = 0
    total_sync_functions = 0
    
    for file_path in python_files:
        stats = analyze_file_for_async_functions(file_path)
        
        if "error" in stats:
            print(f"❌ Error analyzing {file_path}: {stats['error']}")
            continue
        
        all_stats.append(stats)
        total_functions += stats["total_functions"]
        total_async_functions += stats["async_functions"]
        total_sync_functions += stats["sync_functions"]
    
    # Calculate overall ratio
    overall_async_ratio = total_async_functions / total_functions if total_functions > 0 else 0
    
    # Sort files by async ratio
    all_stats.sort(key=lambda x: x["async_ratio"], reverse=True)
    
    # Print summary
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"  Total Functions: {total_functions}")
    print(f"  Async Functions: {total_async_functions}")
    print(f"  Sync Functions: {total_sync_functions}")
    print(f"  Async Ratio: {overall_async_ratio:.1%}")
    
    # Check if target is met
    target_ratio = 0.70  # 70%
    if overall_async_ratio >= target_ratio:
        print(f"✅ Target async ratio ({target_ratio:.0%}) met!")
    else:
        print(f"⚠️  Target async ratio ({target_ratio:.0%}) not met. Current: {overall_async_ratio:.1%}")
    
    # Top 10 files by async ratio
    print(f"\n🏆 TOP 10 FILES BY ASYNC RATIO:")
    for i, stats in enumerate(all_stats[:10], 1):
        if stats["total_functions"] > 0:
            print(f"{i:2d}. {stats['filepath']}")
            print(f"    Functions: {stats['total_functions']}, Async: {stats['async_functions']} ({stats['async_ratio']:.1%})")
    
    # Files with 0% async ratio (need attention)
    zero_async_files = [s for s in all_stats if s["async_ratio"] == 0 and s["total_functions"] > 5]
    if zero_async_files:
        print(f"\n⚠️  FILES WITH 0% ASYNC RATIO (need attention):")
        for stats in zero_async_files[:10]:  # Show top 10
            print(f"  - {stats['filepath']} ({stats['total_functions']} functions)")
    
    # Save detailed results
    output_file = project_root / "reports" / "async_function_analysis.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    results = {
        "analysis_timestamp": "2025-01-01T00:00:00Z",
        "overall_stats": {
            "total_functions": total_functions,
            "async_functions": total_async_functions,
            "sync_functions": total_sync_functions,
            "async_ratio": overall_async_ratio,
            "target_ratio": target_ratio,
            "target_met": overall_async_ratio >= target_ratio,
        },
        "file_stats": all_stats,
        "zero_async_files": [s["filepath"] for s in zero_async_files],
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    
    return 0 if overall_async_ratio >= target_ratio else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
