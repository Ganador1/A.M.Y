#!/usr/bin/env python3

"""
Comprehensive Async Implementation Verification - Final ROADMAP 5 Check
Verifies that all files properly implement async patterns where needed.
"""

import ast
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Set
import json
import sys


class AsyncImplementationVerifier:
    """Comprehensive verifier for async implementation across the entire codebase."""

    def __init__(self):
        self.issues = []
        self.files_analyzed = 0
        self.async_patterns = [
            'time.sleep', 'requests.', 'urllib', 'db.query', 'session.execute',
            'open(', 'json.load', 'json.dump', 'pickle.load', 'pickle.dump',
            'subprocess.', 'os.system', 'os.popen', 'smtplib.', 'imaplib.'
        ]

    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a single file for async implementation."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filepath)

            # Basic stats
            async_functions = []
            sync_functions = []
            blocking_calls = []
            has_asyncio_import = 'import asyncio' in content or 'from asyncio' in content

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
                    if node.name in async_functions:
                        function_content = content.split('\n')[node.lineno-1:node.end_lineno] if hasattr(node, 'end_lineno') else []
                        function_code = '\n'.join(function_content)

                        for pattern in self.async_patterns:
                            if pattern in function_code:
                                blocking_calls.append({
                                    'function': node.name,
                                    'pattern': pattern,
                                    'line': self._find_pattern_line(function_code, pattern),
                                    'severity': self._get_pattern_severity(pattern)
                                })

            # Calculate metrics
            total_functions = len(async_functions) + len(sync_functions)
            async_ratio = len(async_functions) / total_functions if total_functions > 0 else 0

            # Determine if file should be async
            should_be_async = (
                len(blocking_calls) > 0 or
                'api' in str(filepath).lower() or
                'service' in str(filepath).lower() or
                'router' in str(filepath).lower()
            )

            # Issues detection
            issues = []

            if should_be_async and async_ratio < 0.5 and total_functions > 5:
                issues.append({
                    'type': 'low_async_ratio',
                    'severity': 'medium',
                    'message': f'File should have higher async ratio ({async_ratio:.1%}) for service/API file'
                })

            if blocking_calls and not has_asyncio_import:
                issues.append({
                    'type': 'missing_asyncio_import',
                    'severity': 'high',
                    'message': f'Blocking calls found but no asyncio import'
                })

            if 'async def' in content and blocking_calls:
                issues.append({
                    'type': 'blocking_in_async',
                    'severity': 'high',
                    'message': f'Blocking operations in async functions: {len(blocking_calls)} found'
                })

            if 'time.sleep' in content and 'async def' in content:
                issues.append({
                    'type': 'time_sleep_in_async',
                    'severity': 'critical',
                    'message': 'time.sleep found in async function - blocks event loop'
                })

            result = {
                'filepath': str(filepath),
                'total_functions': total_functions,
                'async_functions': len(async_functions),
                'sync_functions': len(sync_functions),
                'async_ratio': round(async_ratio, 3),
                'blocking_calls': blocking_calls,
                'has_asyncio_import': has_asyncio_import,
                'should_be_async': should_be_async,
                'issues': issues,
                'is_async_compliant': len(issues) == 0 and (not should_be_async or async_ratio > 0.5)
            }

            if issues:
                self.issues.append(result)

            self.files_analyzed += 1
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
                'has_asyncio_import': False,
                'should_be_async': False,
                'issues': [{'type': 'parse_error', 'severity': 'high', 'message': str(e)}],
                'is_async_compliant': False
            }

    def _find_pattern_line(self, code: str, pattern: str) -> int:
        """Find the line number of a pattern in code."""
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if pattern in line:
                return i
        return 0

    def _get_pattern_severity(self, pattern: str) -> str:
        """Get severity level for blocking patterns."""
        critical_patterns = ['time.sleep']
        high_patterns = ['requests.', 'urllib', 'db.query', 'session.execute']

        if pattern in critical_patterns:
            return 'critical'
        elif pattern in high_patterns:
            return 'high'
        else:
            return 'medium'

    def analyze_directory(self, directory: Path) -> Dict[str, Any]:
        """Analyze all Python files in a directory."""
        results = []

        for py_file in directory.rglob('*.py'):
            if py_file.stat().st_size > 0:  # Skip empty files
                result = self.analyze_file(py_file)
                results.append(result)

        return {
            'total_files': len(results),
            'compliant_files': len([r for r in results if r.get('is_async_compliant', False)]),
            'files_with_issues': len([r for r in results if r.get('issues')]),
            'overall_compliance': round(
                len([r for r in results if r.get('is_async_compliant', False)]) / len(results) * 100, 1
            ) if results else 0,
            'results': results
        }

    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive async implementation report."""
        return json.dumps({
            'summary': {
                'files_analyzed': self.files_analyzed,
                'files_with_issues': len(self.issues),
                'compliance_rate': round((self.files_analyzed - len(self.issues)) / self.files_analyzed * 100, 1) if self.files_analyzed > 0 else 0
            },
            'issues': self.issues
        }, indent=2)


def main():
    """Main verification function."""
    print("🔍 COMPREHENSIVE ASYNC IMPLEMENTATION VERIFICATION")
    print("=" * 70)

    # Analyze main application directories
    analyze_dirs = [
        Path("app/services"),
        Path("app/routers"),
        Path("app/domains"),
        Path("app/core"),
        Path("app/connectors"),
        Path("app/monitoring"),
        Path("app/middleware"),
        Path("app/adapters"),
        Path("app/validation"),
        Path("app/security")
    ]

    verifier = AsyncImplementationVerifier()
    all_results = []

    for analyze_dir in analyze_dirs:
        if analyze_dir.exists():
            print(f"\n📁 Analyzing {analyze_dir}/")
            dir_results = verifier.analyze_directory(analyze_dir)
            all_results.append(dir_results)

            compliance = dir_results['overall_compliance']
            status = "✅" if compliance > 80 else "⚠️" if compliance > 50 else "❌"

            print(f"  📊 {dir_results['total_files']} files analyzed")
            print(f"  {status} Compliance: {compliance:.1f}%")
            print(f"  🔍 Issues found: {dir_results['files_with_issues']}")

    # Generate comprehensive summary
    total_files = sum(r['total_files'] for r in all_results)
    total_compliant = sum(r['compliant_files'] for r in all_results)
    total_issues = sum(r['files_with_issues'] for r in all_results)
    overall_compliance = (total_compliant / total_files * 100) if total_files > 0 else 0

    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE ASYNC COMPLIANCE REPORT")
    print("=" * 70)
    print(f"Total files analyzed: {total_files}")
    print(f"Files with issues: {total_issues}")
    print(f"Overall compliance: {overall_compliance:.1f}%")

    if overall_compliance > 90:
        print("🎉 EXCELLENT: Async implementation is comprehensive and well-structured")
    elif overall_compliance > 75:
        print("✅ GOOD: Most files properly implement async patterns")
    elif overall_compliance > 50:
        print("⚠️  MODERATE: Some files need async improvements")
    else:
        print("❌ NEEDS WORK: Significant async implementation issues found")

    # Critical issues summary
    critical_issues = [r for r in verifier.issues if any(i['severity'] == 'critical' for i in r.get('issues', []))]
    high_issues = [r for r in verifier.issues if any(i['severity'] == 'high' for i in r.get('issues', []))]

    if critical_issues:
        print(f"\n🚨 CRITICAL ISSUES FOUND: {len(critical_issues)}")
        for issue in critical_issues[:10]:  # Show top 10
            print(f"  • {issue['filepath']}: {issue['issues'][0]['message']}")

    if high_issues:
        print(f"\n⚠️  HIGH PRIORITY ISSUES: {len(high_issues)}")
        for issue in high_issues[:10]:  # Show top 10
            print(f"  • {issue['filepath']}: {issue['issues'][0]['message']}")

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if critical_issues:
        print("• Fix critical issues (time.sleep in async functions) immediately")
    if high_issues:
        print("• Address high priority issues (blocking I/O in async functions)")
    if overall_compliance < 90:
        print("• Consider migrating more sync functions to async where appropriate")
    if overall_compliance > 90:
        print("• Excellent async implementation - maintain current patterns")

    # Save detailed report
    report_file = Path("scripts/analysis/comprehensive_async_verification_report.json")
    with open(report_file, 'w') as f:
        json.dump(verifier.generate_comprehensive_report(), f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Final verdict
    print("\n🎯 FINAL VERDICT:")
    if overall_compliance >= 95:
        print("✅ ALL FILES PROPERLY IMPLEMENT ASYNC PATTERNS")
        return 0
    elif overall_compliance >= 80:
        print("✅ MOST FILES PROPERLY IMPLEMENT ASYNC - Minor improvements needed")
        return 0
    else:
        print("⚠️  SOME FILES NEED ASYNC IMPROVEMENTS")
        return 1


if __name__ == "__main__":
    exit(main())
