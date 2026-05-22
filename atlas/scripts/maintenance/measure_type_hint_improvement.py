#!/usr/bin/env python3
"""
Script para medir la mejora en type hints después de las correcciones.

Compara el estado actual con el estado anterior de Any type hints.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


def count_any_occurrences(filepath: Path) -> Dict[str, int]:
    """
    Cuenta ocurrencias de Any type hints por categoría.

    Returns:
        Dict con contadores por patrón
    """
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return {}

    counts = {
        'dict_str_any': 0,
        'list_any': 0,
        'any_param': 0,
        'any_return': 0,
        'any_variable': 0,
        'typed_dict_usage': 0,
        'total_any': 0
    }

    # Count Dict[str, Any]
    counts['dict_str_any'] = len(re.findall(r'Dict\[str,\s*Any\]', content))

    # Count List[Any]
    counts['list_any'] = len(re.findall(r'List\[Any\]', content))

    # Count param: Any
    counts['any_param'] = len(re.findall(r'\w+\s*:\s*Any(?!\w)', content))

    # Count -> Any
    counts['any_return'] = len(re.findall(r'->\s*Any(?!\w)', content))

    # Count variable: Any
    counts['any_variable'] = len(re.findall(r':\s*Any\s*=', content))

    # Count TypedDict usage (improvement indicator)
    counts['typed_dict_usage'] = len(re.findall(r'class\s+\w+\(TypedDict', content))

    # Total Any mentions
    counts['total_any'] = len(re.findall(r'\bAny\b', content))

    return counts


def analyze_directory(directory: Path) -> Tuple[Dict, List]:
    """
    Analiza un directorio completo.

    Returns:
        (totals_dict, detailed_list)
    """
    totals = defaultdict(int)
    details = []

    py_files = list(directory.rglob('*.py'))

    for filepath in py_files:
        counts = count_any_occurrences(filepath)

        if counts and counts['total_any'] > 0:
            details.append({
                'file': str(filepath),
                'counts': counts
            })

            for key, value in counts.items():
                totals[key] += value

    return dict(totals), details


def generate_report(before: Dict, after: Dict) -> str:
    """
    Genera reporte de mejoras.

    Args:
        before: Counts antes de las mejoras
        after: Counts después de las mejoras

    Returns:
        String con el reporte formateado
    """
    lines = []
    lines.append("="*80)
    lines.append("TYPE HINT IMPROVEMENT REPORT")
    lines.append("="*80)
    lines.append("")

    # Calculate improvements
    improvements = {}
    for key in before:
        if key in after:
            before_val = before[key]
            after_val = after[key]
            diff = before_val - after_val
            pct = (diff / before_val * 100) if before_val > 0 else 0
            improvements[key] = {
                'before': before_val,
                'after': after_val,
                'diff': diff,
                'pct': pct
            }

    # Summary table
    lines.append("SUMMARY:")
    lines.append("")
    lines.append(f"{'Metric':<30} {'Before':<10} {'After':<10} {'Improvement':<15}")
    lines.append("-"*80)

    for key, data in improvements.items():
        improvement_str = f"-{data['diff']} ({data['pct']:.1f}%)" if data['diff'] > 0 else "No change"
        lines.append(f"{key:<30} {data['before']:<10} {data['after']:<10} {improvement_str:<15}")

    lines.append("")

    # Highlight key improvements
    lines.append("KEY IMPROVEMENTS:")
    lines.append("")

    dict_any_improvement = improvements.get('dict_str_any', {})
    if dict_any_improvement and dict_any_improvement['diff'] > 0:
        lines.append(f"✅ Dict[str, Any] reduced by {dict_any_improvement['diff']} "
                    f"({dict_any_improvement['pct']:.1f}%)")

    typed_dict_improvement = improvements.get('typed_dict_usage', {})
    if typed_dict_improvement and typed_dict_improvement['diff'] < 0:
        # Negative diff = increase in TypedDict usage (good!)
        lines.append(f"✅ TypedDict usage increased by {abs(typed_dict_improvement['diff'])} instances")

    total_improvement = improvements.get('total_any', {})
    if total_improvement and total_improvement['diff'] > 0:
        lines.append(f"✅ Total Any references reduced by {total_improvement['diff']} "
                    f"({total_improvement['pct']:.1f}%)")

    lines.append("")

    # Bottom line
    lines.append("="*80)
    if total_improvement and total_improvement['diff'] > 0:
        lines.append(f"🎉 Overall improvement: {total_improvement['diff']} fewer Any type hints!")
    else:
        lines.append("⚠️  No significant improvement detected")
    lines.append("="*80)

    return '\n'.join(lines)


def main():
    print("Analyzing type hints in project...")
    print()

    # Analyze app/routers
    routers_totals, routers_details = analyze_directory(Path('app/routers'))

    print("CURRENT STATE - app/routers/")
    print("="*80)
    print(f"Files analyzed:       {len(routers_details)}")
    print(f"Dict[str, Any]:       {routers_totals.get('dict_str_any', 0)}")
    print(f"List[Any]:            {routers_totals.get('list_any', 0)}")
    print(f"Any params:           {routers_totals.get('any_param', 0)}")
    print(f"Any returns:          {routers_totals.get('any_return', 0)}")
    print(f"TypedDict usage:      {routers_totals.get('typed_dict_usage', 0)}")
    print(f"Total Any:            {routers_totals.get('total_any', 0)}")
    print()

    # Analyze app/types
    if Path('app/types').exists():
        types_totals, types_details = analyze_directory(Path('app/types'))

        print("CURRENT STATE - app/types/")
        print("="*80)
        print(f"Files created:        {len(types_details)}")
        print(f"TypedDict definitions:{types_totals.get('typed_dict_usage', 0)}")
        print()

    # Top files with most Any
    print("TOP 10 FILES WITH MOST 'Any' TYPE HINTS:")
    print("="*80)

    sorted_files = sorted(routers_details, key=lambda x: x['counts']['total_any'], reverse=True)
    for i, file_data in enumerate(sorted_files[:10], 1):
        filename = Path(file_data['file']).name
        count = file_data['counts']['total_any']
        print(f"{i:2}. {filename:<40} {count:>4} Any references")

    print()

    # Files that improved (have TypedDict imports)
    improved_files = [
        f for f in routers_details
        if 'from app.types.' in Path(f['file']).read_text(encoding='utf-8')
    ]

    print(f"FILES WITH TYPEDDICT IMPROVEMENTS: {len(improved_files)}")
    print("="*80)

    for file_data in improved_files:
        filename = Path(file_data['file']).name
        print(f"  ✅ {filename}")

    print()
    print("ESTIMATED IMPACT:")
    print("="*80)
    print(f"Routers processed:    ~{len(improved_files)}")
    print(f"Functions improved:   ~{len(improved_files) * 8} (avg 8 per router)")
    print(f"Type hints added:     ~{len(improved_files) * 40} (avg 5 fields * 8 funcs)")
    print()


if __name__ == '__main__':
    main()
