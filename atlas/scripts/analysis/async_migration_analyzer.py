#!/usr/bin/env python3

"""
Advanced Async Migration Scanner - ROADMAP 5 Implementation
Comprehensive analysis of async/sync patterns in the codebase.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Set
import json


class AsyncMigrationAnalyzer:
    """Advanced analyzer for async migration opportunities."""

    def __init__(self):
        self.analysis_results = []
        self.blocking_patterns = [
            'time.sleep', 'requests.', 'urllib', 'db.query', 'session.execute',
            'open(', 'json.load', 'json.dump', 'pickle.load', 'pickle.dump'
        ]

    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a single file for async migration opportunities."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filepath)

            # Basic stats
            async_functions = []
            sync_functions = []
            blocking_calls = []

            for node in ast.walk(tree):
                if isinstance(node, ast.AsyncFunctionDef):
                    async_functions.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    # Check if function has async decorator
                    has_async_decorator = False
                    for decorator in node.decorator_list:
                        if hasattr(decorator, 'id') and decorator.id in ['async', 'asyncio']:
                            has_async_decorator = True
                            break
                    if has_async_decorator:
                        async_functions.append(node.name)
                    else:
                        sync_functions.append(node.name)

                # Check for blocking patterns in async functions
                if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                    function_content = content.split('\n')[node.lineno-1:node.end_lineno] if hasattr(node, 'end_lineno') else []
                    function_code = '\n'.join(function_content)

                    for pattern in self.blocking_patterns:
                        if pattern in function_code and node.name in async_functions:
                            blocking_calls.append({
                                'function': node.name,
                                'pattern': pattern,
                                'line': self._find_pattern_line(function_code, pattern)
                            })

            # Calculate scores
            total_functions = len(async_functions) + len(sync_functions)
            async_ratio = len(async_functions) / total_functions if total_functions > 0 else 0

            # Priority score based on blocking patterns and function count
            priority_score = len(blocking_calls) * 10 + total_functions

            result = {
                'filepath': str(filepath),
                'total_functions': total_functions,
                'async_functions': len(async_functions),
                'sync_functions': len(sync_functions),
                'async_ratio': round(async_ratio, 3),
                'blocking_calls': blocking_calls,
                'priority_score': priority_score,
                'recommendations': self._generate_recommendations(async_functions, blocking_calls)
            }

            self.analysis_results.append(result)
            return result

        except Exception as e:
            return {
                'filepath': str(filepath),
                'error': str(e),
                'total_functions': 0,
                'async_functions': 0,
                'sync_functions': 0,
                'async_ratio': 0,
                'blocking_calls': [],
                'priority_score': 0
            }

    def _find_pattern_line(self, code: str, pattern: str) -> int:
        """Find the line number of a pattern in code."""
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if pattern in line:
                return i
        return 0

    def _generate_recommendations(self, async_functions: List[str], blocking_calls: List[Dict]) -> List[str]:
        """Generate migration recommendations."""
        recommendations = []

        if blocking_calls:
            recommendations.append(f"Migrate {len(blocking_calls)} blocking calls in async functions")

        if len(async_functions) < 10:
            recommendations.append("Consider migrating more functions to async")

        if any('time.sleep' in call['pattern'] for call in blocking_calls):
            recommendations.append("Replace time.sleep with await asyncio.sleep")

        if any('requests.' in call['pattern'] for call in blocking_calls):
            recommendations.append("Replace requests with httpx async client")

        if any('db.query' in call['pattern'] for call in blocking_calls):
            recommendations.append("Migrate to async database operations")

        return recommendations

    def analyze_directory(self, directory: Path) -> Dict[str, Any]:
        """Analyze all Python files in a directory."""
        results = []

        for py_file in directory.rglob('*.py'):
            if py_file.stat().st_size > 0:  # Skip empty files
                result = self.analyze_file(py_file)
                results.append(result)

        # Sort by priority score
        results.sort(key=lambda x: x.get('priority_score', 0), reverse=True)

        return {
            'total_files': len(results),
            'files_with_async': len([r for r in results if r.get('async_functions', 0) > 0]),
            'total_async_functions': sum(r.get('async_functions', 0) for r in results),
            'total_sync_functions': sum(r.get('sync_functions', 0) for r in results),
            'overall_async_ratio': round(
                sum(r.get('async_functions', 0) for r in results) /
                (sum(r.get('async_functions', 0) for r in results) +
                 sum(r.get('sync_functions', 0) for r in results)),
                3
            ) if (sum(r.get('async_functions', 0) for r in results) +
                  sum(r.get('sync_functions', 0) for r in results)) > 0 else 0,
            'files_with_blocking_calls': len([r for r in results if r.get('blocking_calls')]),
            'results': results
        }

    def generate_report(self) -> str:
        """Generate a comprehensive report."""
        return json.dumps(self.analysis_results, indent=2)


def main():
    """Main analysis function."""
    print("🔍 Advanced Async Migration Analysis")
    print("=" * 60)

    # Analyze main application directories
    analyze_dirs = [
        Path("app/services"),
        Path("app/routers"),
        Path("app/domains"),
        Path("app/core"),
        Path("app/connectors"),
        Path("app/monitoring")
    ]

    analyzer = AsyncMigrationAnalyzer()
    all_results = []

    for analyze_dir in analyze_dirs:
        if analyze_dir.exists():
            print(f"\n📁 Analyzing {analyze_dir}/")
            dir_results = analyzer.analyze_directory(analyze_dir)
            all_results.append(dir_results)

            print(f"  📊 {dir_results['total_files']} files analyzed")
            print(f"  ⚡ {dir_results['files_with_async']} files with async functions")
            print(f"  📈 Async ratio: {dir_results['overall_async_ratio']:.1%}")
            print(f"  ⚠️  {dir_results['files_with_blocking_calls']} files with blocking calls in async functions")

    # Generate summary
    total_files = sum(r['total_files'] for r in all_results)
    total_async = sum(r['total_async_functions'] for r in all_results)
    total_sync = sum(r['total_sync_functions'] for r in all_results)
    overall_ratio = total_async / (total_async + total_sync) if (total_async + total_sync) > 0 else 0

    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE SUMMARY")
    print("=" * 60)
    print(f"Total files analyzed: {total_files}")
    print(f"Total async functions: {total_async}")
    print(f"Total sync functions: {total_sync}")
    print(f"Overall async ratio: {overall_ratio:.1%}")
    print(f"Files with blocking calls: {sum(r['files_with_blocking_calls'] for r in all_results)}")

    # Top priority files for migration
    priority_files = []
    for result in analyzer.analysis_results:
        if result.get('blocking_calls') or result.get('priority_score', 0) > 50:
            priority_files.append(result)

    priority_files.sort(key=lambda x: x.get('priority_score', 0), reverse=True)

    print("\n🔥 TOP PRIORITY FILES FOR MIGRATION:")
    for i, file_info in enumerate(priority_files[:20], 1):
        filepath = file_info['filepath']
        async_count = file_info.get('async_functions', 0)
        blocking_count = len(file_info.get('blocking_calls', []))
        score = file_info.get('priority_score', 0)

        print(f"{i:2d}. {filepath}")
        print(f"    ⚡ Async functions: {async_count}")
        print(f"    ⚠️  Blocking calls: {blocking_count}")
        print(f"    📊 Priority score: {score}")

        if file_info.get('recommendations'):
            for rec in file_info['recommendations'][:2]:  # Show top 2 recommendations
                print(f"    💡 {rec}")

    # Save detailed report
    report_file = Path("scripts/analysis/async_migration_report.json")
    with open(report_file, 'w') as f:
        json.dump({
            'summary': {
                'total_files': total_files,
                'overall_async_ratio': overall_ratio,
                'files_needing_migration': len(priority_files)
            },
            'results': analyzer.analysis_results
        }, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")
    print("\n💡 RECOMMENDATIONS:")
    print("• Focus on files with high priority scores first")
    print("• Replace blocking I/O operations with async alternatives")
    print("• Use run_in_executor for CPU-bound operations in async functions")
    print("• Consider migrating entire service classes to async patterns")
    return len(priority_files)


if __name__ == "__main__":
    priority_count = main()
    print(f"\n🎯 {priority_count} high-priority files identified for async migration")
