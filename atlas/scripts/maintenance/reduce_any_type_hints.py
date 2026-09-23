#!/usr/bin/env python3
"""
Script para reducir el uso de Any type hint sugiriendo tipos más específicos.

Usage:
    python scripts/maintenance/reduce_any_type_hints.py --dry-run
    python scripts/maintenance/reduce_any_type_hints.py --execute
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Tuple
import argparse


def analyze_any_usage(filepath: Path) -> List[Dict]:
    """
    Analiza uso de Any en un archivo y sugiere reemplazos.

    Returns:
        Lista de diccionarios con info de cada Any encontrado
    """
    results = []

    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Pattern 1: variable: Any = ...
            match = re.search(r'(\w+)\s*:\s*Any\s*=', line)
            if match:
                var_name = match.group(1)
                # Try to infer type from assignment
                suggested_type = infer_type_from_assignment(line)
                results.append({
                    'line': i,
                    'text': line.strip(),
                    'variable': var_name,
                    'current': 'Any',
                    'suggested': suggested_type,
                    'pattern': 'variable_assignment'
                })

            # Pattern 2: function param: Any
            match = re.search(r'def\s+\w+\([^)]*(\w+)\s*:\s*Any', line)
            if match:
                param_name = match.group(1)
                suggested_type = suggest_param_type(param_name, line)
                results.append({
                    'line': i,
                    'text': line.strip(),
                    'variable': param_name,
                    'current': 'Any',
                    'suggested': suggested_type,
                    'pattern': 'function_parameter'
                })

            # Pattern 3: return type -> Any
            match = re.search(r'def\s+(\w+)\([^)]*\)\s*->\s*Any', line)
            if match:
                func_name = match.group(1)
                suggested_type = suggest_return_type(func_name, lines, i)
                results.append({
                    'line': i,
                    'text': line.strip(),
                    'variable': func_name,
                    'current': 'Any',
                    'suggested': suggested_type,
                    'pattern': 'return_type'
                })

            # Pattern 4: Dict[str, Any]
            match = re.search(r'Dict\[([^,]+),\s*Any\]', line)
            if match:
                key_type = match.group(1)
                suggested = suggest_dict_value_type(line)
                results.append({
                    'line': i,
                    'text': line.strip(),
                    'variable': 'dict_value',
                    'current': f'Dict[{key_type}, Any]',
                    'suggested': suggested,
                    'pattern': 'dict_value'
                })

    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")

    return results


def infer_type_from_assignment(line: str) -> str:
    """Infer type from assignment value"""
    if '= {}' in line or '= dict()' in line:
        return 'Dict[str, Any]  # TODO: Specify value type'
    elif '= []' in line or '= list()' in line:
        return 'List[Any]  # TODO: Specify element type'
    elif '= ""' in line or "= ''" in line:
        return 'str'
    elif re.search(r'= \d+\.', line):
        return 'float'
    elif re.search(r'= \d+', line):
        return 'int'
    elif '= True' in line or '= False' in line:
        return 'bool'
    elif '= None' in line:
        return 'Optional[Any]  # TODO: Specify type'
    else:
        return 'Any  # TODO: Infer from usage'


def suggest_param_type(param_name: str, line: str) -> str:
    """Suggest type for parameter based on name and context"""
    param_lower = param_name.lower()

    # Common patterns
    if param_lower in ['data', 'config', 'params', 'kwargs']:
        return 'Dict[str, Any]  # TODO: Create specific model'
    elif param_lower in ['items', 'results', 'values']:
        return 'List[Any]  # TODO: Specify element type'
    elif param_lower.endswith('_id'):
        if 'str' in line:
            return 'str'
        return 'Union[str, int]'
    elif param_lower.endswith('_dict'):
        return 'Dict[str, Any]  # TODO: Specify value type'
    elif param_lower.endswith('_list'):
        return 'List[Any]  # TODO: Specify element type'
    elif 'callback' in param_lower:
        return 'Callable[..., Any]  # TODO: Specify signature'
    else:
        return 'Any  # TODO: Analyze usage in function body'


def suggest_return_type(func_name: str, lines: List[str], func_line: int) -> str:
    """Suggest return type by analyzing function body"""

    # Find return statements in function
    in_function = False
    indent_level = 0
    returns = []

    for i in range(func_line, min(func_line + 50, len(lines))):
        line = lines[i]

        if i == func_line:
            in_function = True
            indent_level = len(line) - len(line.lstrip())
            continue

        if not in_function:
            continue

        # Check if still in function
        current_indent = len(line) - len(line.lstrip())
        if line.strip() and current_indent <= indent_level:
            break

        # Find return statements
        if 'return' in line:
            # Extract what's being returned
            match = re.search(r'return\s+(.+)', line)
            if match:
                ret_val = match.group(1).strip().rstrip(',;')
                returns.append(ret_val)

    # Analyze returns
    if not returns:
        return 'None'
    elif all(r == 'None' for r in returns):
        return 'None'
    elif all('{' in r or 'dict(' in r for r in returns):
        return 'Dict[str, Any]  # TODO: Create response model'
    elif all('[' in r or 'list(' in r for r in returns):
        return 'List[Any]  # TODO: Specify element type'
    elif all(r.startswith('"') or r.startswith("'") for r in returns):
        return 'str'
    elif any('await' in r for r in returns):
        return 'Any  # TODO: Check async return type'
    else:
        return 'Any  # TODO: Analyze return values'


def suggest_dict_value_type(line: str) -> str:
    """Suggest more specific type for Dict[str, Any]"""
    if 'config' in line.lower() or 'params' in line.lower():
        return 'Dict[str, Union[str, int, float, bool]]  # Common config types'
    elif 'result' in line.lower() or 'response' in line.lower():
        return 'Dict[str, Any]  # TODO: Create response model class'
    elif 'data' in line.lower():
        return 'Dict[str, Any]  # TODO: Define data structure'
    else:
        return 'Dict[str, Any]  # TODO: Specify value types'


def generate_report(filepath: Path, findings: List[Dict]) -> str:
    """Generate report for findings"""
    if not findings:
        return ""

    report = []
    report.append(f"\n{'='*80}")
    report.append(f"File: {filepath}")
    report.append(f"{'='*80}")
    report.append(f"Found {len(findings)} uses of Any type hint\n")

    for finding in findings:
        report.append(f"Line {finding['line']}: {finding['pattern']}")
        report.append(f"  Current:   {finding['text']}")
        report.append(f"  Variable:  {finding['variable']}")
        report.append(f"  Suggested: {finding['current']} → {finding['suggested']}")
        report.append("")

    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='Reduce Any type hints')
    parser.add_argument('--dry-run', action='store_true', help='Show analysis only')
    parser.add_argument('--execute', action='store_true', help='Not implemented yet')
    parser.add_argument('--path', type=str, default='app', help='Path to analyze')

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("ERROR: Must specify --dry-run or --execute")
        return

    # Find all Python files
    app_path = Path(args.path)
    py_files = list(app_path.rglob('*.py'))

    print(f"Analyzing {len(py_files)} Python files for Any type hints...")
    print()

    total_findings = 0
    files_with_any = 0

    for filepath in py_files:
        findings = analyze_any_usage(filepath)

        if findings:
            files_with_any += 1
            total_findings += len(findings)

            if args.dry_run:
                print(generate_report(filepath, findings))

    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Files analyzed:     {len(py_files)}")
    print(f"Files with Any:     {files_with_any}")
    print(f"Total Any found:    {total_findings}")
    print()
    print(f"💡 Suggestions:")
    print(f"   1. Replace simple cases (int, str, bool) immediately")
    print(f"   2. Create Pydantic models for Dict[str, Any] in APIs")
    print(f"   3. Specify List element types where possible")
    print(f"   4. Use Union types for parameters that accept multiple types")
    print(f"   5. Review function bodies to infer accurate return types")
    print()
    print(f"⚠️  Note: Auto-fixing not implemented. Manual review recommended.")


if __name__ == '__main__':
    main()
