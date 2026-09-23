#!/usr/bin/env python3
"""
Script para corregir bare except clauses (except:) con Exception específico.

Un bare except clause captura TODAS las excepciones incluyendo SystemExit,
KeyboardInterrupt, etc., lo cual es un anti-pattern peligroso.

Usage:
    python scripts/maintenance/fix_bare_except.py --dry-run
    python scripts/maintenance/fix_bare_except.py --execute
    python scripts/maintenance/fix_bare_except.py --file app/services/my_service.py
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import argparse


def find_bare_except(filepath: Path) -> List[Tuple[int, str, str]]:
    """
    Encuentra bare except clauses en un archivo.

    Returns:
        Lista de tuplas (line_number, full_line, indentation)
    """
    results = []
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # Pattern: except: (without any exception type)
        # Must have only whitespace before 'except' and nothing between 'except' and ':'
        match = re.match(r'^(\s*)except\s*:\s*(?:#.*)?$', line)
        if match:
            indentation = match.group(1)
            results.append((i, line, indentation))

    return results


def get_context_lines(lines: List[str], except_line_idx: int, context: int = 5) -> str:
    """
    Obtener líneas de contexto alrededor del except.

    Returns:
        String con contexto
    """
    start = max(0, except_line_idx - context)
    end = min(len(lines), except_line_idx + context + 1)

    context_lines = []
    for i in range(start, end):
        marker = ">>> " if i == except_line_idx else "    "
        context_lines.append(f"{marker}{i+1:4d}: {lines[i]}")

    return "\n".join(context_lines)


def suggest_exception_type(filepath: Path, line_idx: int, lines: List[str]) -> str:
    """
    Sugerir tipo de excepción basado en contexto.

    Returns:
        Nombre de la excepción sugerida
    """
    # Get context around the except
    context_start = max(0, line_idx - 10)
    context = '\n'.join(lines[context_start:line_idx]).lower()

    # Domain detection
    path_str = str(filepath).lower()

    # Check for specific patterns
    if 'json' in context or 'parse' in context:
        return 'Exception  # TODO: Change to JSONDecodeError or ValueError'
    elif 'file' in context or 'open(' in context:
        return 'Exception  # TODO: Change to IOError or FileNotFoundError'
    elif 'database' in context or 'session' in context:
        return 'Exception  # TODO: Change to DatabaseError'
    elif 'api' in context or 'request' in context or 'http' in context:
        return 'Exception  # TODO: Change to APIError or HTTPException'

    # Domain-specific
    if 'biology' in path_str:
        return 'Exception  # TODO: Consider BiologyError'
    elif 'chemistry' in path_str:
        return 'Exception  # TODO: Consider ChemistryError'
    elif 'physics' in path_str or 'quantum' in path_str:
        return 'Exception  # TODO: Consider PhysicsError or QuantumError'
    elif 'mathematics' in path_str or 'math' in path_str:
        return 'Exception  # TODO: Consider MathematicsError'
    elif 'medicine' in path_str:
        return 'Exception  # TODO: Consider MedicalError'
    elif 'neuroscience' in path_str:
        return 'Exception  # TODO: Consider NeuroscienceError'

    # Generic fallback
    return 'Exception  # TODO: Use specific exception type'


def fix_bare_except(filepath: Path, dry_run: bool = True) -> Dict:
    """
    Corregir bare except clauses en un archivo.

    Returns:
        Dict con estadísticas
    """
    stats = {
        'file': str(filepath),
        'replacements': 0,
        'lines_changed': [],
        'errors': []
    }

    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')
        original_content = content

        bare_excepts = find_bare_except(filepath)

        if not bare_excepts:
            return stats

        # Process from bottom to top to preserve line numbers
        for line_num, line, indentation in reversed(bare_excepts):
            line_idx = line_num - 1

            # Suggest exception type
            exception_type = suggest_exception_type(filepath, line_idx, lines)

            # Replace bare except with Exception
            old_line = line
            new_line = f"{indentation}except {exception_type}:"

            # Get context for reporting
            context = get_context_lines(lines, line_idx, context=3)

            lines[line_idx] = new_line

            stats['replacements'] += 1
            stats['lines_changed'].append({
                'line_num': line_num,
                'old': old_line.strip(),
                'new': new_line.strip(),
                'context': context
            })

        # Reconstruct content
        new_content = '\n'.join(lines)

        # Write back if not dry run
        if not dry_run and new_content != original_content:
            filepath.write_text(new_content, encoding='utf-8')
            print(f"✅ Fixed {filepath} ({stats['replacements']} bare except clauses)")
        elif dry_run and new_content != original_content:
            print(f"\n🔍 Would fix {filepath} ({stats['replacements']} bare except clauses)")
            for change in stats['lines_changed']:
                print(f"\n   Line {change['line_num']}:")
                print(f"   Old: {change['old']}")
                print(f"   New: {change['new']}")
                print(f"\n   Context:")
                print(change['context'])

    except Exception as e:
        stats['errors'].append(str(e))
        print(f"❌ Error processing {filepath}: {e}")

    return stats


def main():
    parser = argparse.ArgumentParser(description='Fix bare except clauses')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    parser.add_argument('--execute', action='store_true', help='Execute changes')
    parser.add_argument('--file', type=str, help='Fix specific file')

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("ERROR: Must specify either --dry-run or --execute")
        sys.exit(1)

    dry_run = args.dry_run

    # Determine files to process
    if args.file:
        files = [Path(args.file)]
    else:
        # Find all files with bare except
        import subprocess
        result = subprocess.run(
            ['grep', '-rl', '-E', r'^\s*except\s*:', 'app', '--include=*.py'],
            capture_output=True,
            text=True
        )
        files = [Path(f.strip()) for f in result.stdout.split('\n') if f.strip()]

    print(f"{'🔍 DRY RUN MODE' if dry_run else '✅ EXECUTION MODE'}")
    print(f"Processing {len(files)} files with bare except clauses...\n")

    total_stats = {
        'files_processed': 0,
        'files_changed': 0,
        'total_replacements': 0,
        'errors': 0
    }

    for filepath in files:
        if filepath.is_file():
            stats = fix_bare_except(filepath, dry_run=dry_run)
            total_stats['files_processed'] += 1

            if stats['replacements'] > 0:
                total_stats['files_changed'] += 1
                total_stats['total_replacements'] += stats['replacements']

            if stats['errors']:
                total_stats['errors'] += len(stats['errors'])

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Summary")
    print(f"{'='*60}")
    print(f"Files processed: {total_stats['files_processed']}")
    print(f"Files changed: {total_stats['files_changed']}")
    print(f"Total bare except fixed: {total_stats['total_replacements']}")
    print(f"Errors: {total_stats['errors']}")

    if dry_run:
        print(f"\n⚠️  This was a dry run. Use --execute to apply changes.")
        print(f"\n⚠️  IMPORTANT: Review TODO comments and replace with specific exceptions!")
    else:
        print(f"\n✅ Bare except clauses fixed!")
        print(f"\n⚠️  NEXT STEPS:")
        print(f"   1. Review files and replace 'Exception  # TODO' with specific exceptions")
        print(f"   2. Run tests: pytest tests/ -v")
        print(f"   3. Check for any issues: grep -r 'TODO.*Exception' app")


if __name__ == '__main__':
    main()
