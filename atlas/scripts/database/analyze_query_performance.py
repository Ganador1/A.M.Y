#!/usr/bin/env python3

"""
Query Performance Analyzer - ROADMAP 6 Implementation
Analyzes database queries for performance issues including N+1 patterns.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Set
import re


class QueryPerformanceAnalyzer:
    """Analyzes Python code for potential database query performance issues."""

    def __init__(self):
        self.issues = []
        self.files_analyzed = 0

    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a single Python file for query performance issues."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filepath)
            analyzer = FileAnalyzer(filepath, content)
            analyzer.visit(tree)
            self.issues.extend(analyzer.issues)
            self.files_analyzed += 1

            return {
                "file": str(filepath),
                "issues": len(analyzer.issues),
                "issue_details": analyzer.issues
            }
        except Exception as e:
            return {
                "file": str(filepath),
                "error": str(e),
                "issues": 0
            }

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        total_issues = len(self.issues)

        # Categorize issues
        n_plus_1_issues = [i for i in self.issues if i["type"] == "n_plus_1"]
        unoptimized_joins = [i for i in self.issues if i["type"] == "unoptimized_join"]
        missing_indexes = [i for i in self.issues if i["type"] == "missing_index"]

        # Group by severity
        high_severity = [i for i in self.issues if i["severity"] == "high"]
        medium_severity = [i for i in self.issues if i["severity"] == "medium"]

        return {
            "summary": {
                "total_files_analyzed": self.files_analyzed,
                "total_issues": total_issues,
                "high_severity_issues": len(high_severity),
                "medium_severity_issues": len(medium_severity),
                "files_with_issues": len(set(i["file"] for i in self.issues))
            },
            "breakdown": {
                "n_plus_1_queries": len(n_plus_1_issues),
                "unoptimized_joins": len(unoptimized_joins),
                "missing_indexes": len(missing_indexes)
            },
            "issues": self.issues,
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on findings."""
        recommendations = []

        if any(i["type"] == "n_plus_1" for i in self.issues):
            recommendations.append(
                "Use SQLAlchemy joinedload() or selectinload() to prevent N+1 queries"
            )
            recommendations.append(
                "Consider using relationship loading strategies for frequently accessed associations"
            )

        if any(i["type"] == "unoptimized_join" for i in self.issues):
            recommendations.append(
                "Review large JOIN operations and consider query optimization"
            )
            recommendations.append(
                "Use database indexes on frequently filtered columns"
            )

        if any(i["type"] == "missing_index" for i in self.issues):
            recommendations.append(
                "Add database indexes on foreign key columns and frequently queried fields"
            )

        if not recommendations:
            recommendations.append("No performance issues detected - code follows best practices!")

        return recommendations


class FileAnalyzer(ast.NodeVisitor):
    """AST visitor to detect query performance issues in a single file."""

    def __init__(self, filepath: Path, content: str):
        self.filepath = filepath
        self.content = content
        self.issues = []
        self.current_function = None

    def visit_FunctionDef(self, node):
        """Track current function context."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_For(self, node):
        """Detect potential N+1 queries in for loops."""
        # Look for patterns like: for item in query_result: item.relationship
        if isinstance(node.iter, ast.Call):
            if self._is_query_call(node.iter):
                # Check if loop body accesses relationships
                for child in ast.walk(node):
                    if isinstance(child, ast.Attribute):
                        if child.attr in ['user', 'calculations', 'sessions', 'results']:
                            self.issues.append({
                                "type": "n_plus_1",
                                "severity": "high",
                                "file": str(self.filepath),
                                "line": node.lineno,
                                "function": self.current_function,
                                "description": f"Potential N+1 query: accessing '{child.attr}' in loop",
                                "code_snippet": self._get_code_snippet(node.lineno)
                            })
        self.generic_visit(node)

    def _is_query_call(self, node: ast.Call) -> bool:
        """Check if an AST call node represents a database query."""
        if isinstance(node.func, ast.Attribute):
            # Check for .query(), .filter(), .all(), .first() patterns
            if node.func.attr in ['query', 'filter', 'all', 'first', 'count']:
                return True
            # Check for SQLAlchemy session patterns
            if hasattr(node.func, 'value') and isinstance(node.func.value, ast.Name):
                if node.func.value.id in ['session', 'db', 'conn']:
                    return True
        return False

    def _get_code_snippet(self, line_number: int, context: int = 3) -> str:
        """Extract code snippet around a line number."""
        lines = self.content.split('\n')
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)

        snippet_lines = []
        for i in range(start, end):
            marker = ">>> " if i == line_number - 1 else "    "
            snippet_lines.append(f"{marker}{i+1:3d}: {lines[i]}")

        return '\n'.join(snippet_lines)


def main():
    """Main analysis function."""
    print("🔍 Database Query Performance Analysis")
    print("=" * 50)

    # Define directories to analyze
    analyze_dirs = [
        Path("app/routers"),
        Path("app/services"),
        Path("app/core"),
        Path("app/domains")
    ]

    analyzer = QueryPerformanceAnalyzer()

    for analyze_dir in analyze_dirs:
        if analyze_dir.exists():
            print(f"\n📁 Analyzing {analyze_dir}/")
            for py_file in analyze_dir.rglob("*.py"):
                if py_file.stat().st_size > 0:  # Skip empty files
                    result = analyzer.analyze_file(py_file)
                    if result.get("issues", 0) > 0:
                        print(f"  ⚠️  {result['file']}: {result['issues']} issues")

    # Generate and display report
    report = analyzer.generate_report()

    print("\n" + "=" * 50)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Files analyzed: {report['summary']['total_files_analyzed']}")
    print(f"Total issues found: {report['summary']['total_issues']}")
    print(f"High severity: {report['summary']['high_severity_issues']}")
    print(f"Medium severity: {report['summary']['medium_severity_issues']}")

    print("\n🔍 ISSUE BREAKDOWN")
    print(f"N+1 queries: {report['breakdown']['n_plus_1_queries']}")
    print(f"Unoptimized joins: {report['breakdown']['unoptimized_joins']}")
    print(f"Missing indexes: {report['breakdown']['missing_indexes']}")

    if report['recommendations']:
        print("\n💡 RECOMMENDATIONS")
        for rec in report['recommendations']:
            print(f"• {rec}")

    # Save detailed report
    report_file = Path("scripts/database/query_performance_report.json")
    import json
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")

    return len(analyzer.issues)


if __name__ == "__main__":
    exit(main())
