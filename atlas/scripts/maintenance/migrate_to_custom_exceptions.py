#!/usr/bin/env python3
"""
Script para migrar excepciones genéricas a excepciones personalizadas de AXIOM ATLAS.

Este script analiza el código y reemplaza patrones de Exception genéricos
con excepciones específicas del dominio.

Usage:
    python scripts/maintenance/migrate_to_custom_exceptions.py --dry-run
    python scripts/maintenance/migrate_to_custom_exceptions.py --execute
    python scripts/maintenance/migrate_to_custom_exceptions.py --file app/services/my_service.py
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import argparse


# Mapping de patrones a excepciones específicas
EXCEPTION_MAPPINGS = {
    # Domain exceptions - Biology
    'biology': [
        (r'(protein|gene|dna|rna|genome)', 'from app.exceptions.domain.biology import BiologyError', 'BiologyError'),
        (r'(uniprot|ncbi|genbank)', 'from app.exceptions.domain.biology import BiologyError', 'BiologyError'),
    ],

    # Domain exceptions - Chemistry
    'chemistry': [
        (r'(molecule|molecular|pubchem|smiles|inchi)', 'from app.exceptions.domain.chemistry import ChemistryError', 'ChemistryError'),
        (r'(rdkit|openbabel|chemical)', 'from app.exceptions.domain.chemistry import ChemistryError', 'ChemistryError'),
    ],

    # Domain exceptions - Physics/Quantum
    'physics': [
        (r'(quantum|qiskit|circuit|qubit)', 'from app.exceptions.domain.physics import QuantumError', 'QuantumError'),
        (r'(physics|simulation)', 'from app.exceptions.domain.physics import PhysicsError', 'PhysicsError'),
    ],

    # Domain exceptions - Mathematics
    'mathematics': [
        (r'(sympy|symbolic|equation|matrix)', 'from app.exceptions.domain.mathematics import MathematicsError', 'MathematicsError'),
        (r'(numerical|computation|algorithm)', 'from app.exceptions.domain.mathematics import MathematicsError', 'MathematicsError'),
    ],

    # Domain exceptions - Medicine
    'medicine': [
        (r'(dicom|nifti|medical|clinical)', 'from app.exceptions.domain.medicine import MedicalError', 'MedicalError'),
        (r'(diagnosis|patient|imaging)', 'from app.exceptions.domain.medicine import MedicalError', 'MedicalError'),
    ],

    # Domain exceptions - Neuroscience
    'neuroscience': [
        (r'(brain|neural|neuroscience)', 'from app.exceptions.domain.neuroscience import NeuroscienceError', 'NeuroscienceError'),
    ],

    # Infrastructure exceptions - Database
    'database': [
        (r'(database|db\.|session|query|sql)', 'from app.exceptions.infrastructure.database import DatabaseError', 'DatabaseError'),
        (r'(commit|rollback|transaction)', 'from app.exceptions.infrastructure.database import DatabaseError', 'DatabaseError'),
    ],

    # Infrastructure exceptions - Cache
    'cache': [
        (r'(redis|cache|memcached)', 'from app.exceptions.infrastructure.cache import CacheError', 'CacheError'),
    ],

    # Infrastructure exceptions - API
    'api': [
        (r'(api|endpoint|request|response)', 'from app.exceptions.infrastructure.api import APIError', 'APIError'),
        (r'(http|status_code)', 'from app.exceptions.infrastructure.api import APIError', 'APIError'),
    ],

    # External exceptions - LLM
    'llm': [
        (r'(llm|ollama|openai|gpt)', 'from app.exceptions.external.llm import LLMError', 'LLMError'),
        (r'(generate|completion|model)', 'from app.exceptions.external.llm import LLMError', 'LLMError'),
    ],

    # Validation exceptions
    'validation': [
        (r'(validation|validate|invalid|schema)', 'from app.exceptions.validation.input import InputValidationError', 'InputValidationError'),
    ],

    # Ethics exceptions
    'ethics': [
        (r'(ethics|safety|risk)', 'from app.exceptions.validation.ethics import EthicsViolationError', 'EthicsViolationError'),
    ],
}


def detect_domain(filepath: Path, content: str) -> str:
    """
    Detectar el dominio del archivo basado en ruta y contenido.

    Returns:
        Nombre del dominio detectado o 'generic'
    """
    path_str = str(filepath).lower()
    content_lower = content.lower()

    # Check by path first
    if 'biology' in path_str:
        return 'biology'
    elif 'chemistry' in path_str:
        return 'chemistry'
    elif 'physics' in path_str or 'quantum' in path_str:
        return 'physics'
    elif 'mathematics' in path_str or 'math' in path_str:
        return 'mathematics'
    elif 'medicine' in path_str or 'medical' in path_str:
        return 'medicine'
    elif 'neuroscience' in path_str:
        return 'neuroscience'
    elif 'database' in path_str or 'db' in path_str:
        return 'database'
    elif 'cache' in path_str or 'redis' in path_str:
        return 'cache'

    # Check by content patterns
    for domain, patterns in EXCEPTION_MAPPINGS.items():
        for pattern, _, _ in patterns:
            if re.search(pattern, content_lower):
                return domain

    return 'generic'


def find_exception_blocks(content: str) -> List[Tuple[int, str, str]]:
    """
    Encuentra bloques try/except que usan Exception genérico.

    Returns:
        Lista de tuplas (line_number, full_line, exception_var)
    """
    results = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # Pattern: except Exception as e:
        match = re.search(r'except\s+Exception\s+as\s+(\w+):', line)
        if match:
            var_name = match.group(1)
            results.append((i, line, var_name))

        # Pattern: except Exception:
        match = re.search(r'except\s+Exception:', line)
        if match:
            results.append((i, line, None))

    return results


def suggest_replacement(filepath: Path, content: str, line_num: int, line: str) -> Tuple[str, str, str]:
    """
    Sugerir reemplazo de excepción basado en contexto.

    Returns:
        Tupla (import_statement, exception_class, reason)
    """
    domain = detect_domain(filepath, content)

    # Get import and exception for domain
    if domain in EXCEPTION_MAPPINGS and EXCEPTION_MAPPINGS[domain]:
        _, import_stmt, exc_class = EXCEPTION_MAPPINGS[domain][0]
        return import_stmt, exc_class, f"Detected domain: {domain}"

    # Fallback to generic AtlasException
    return (
        'from app.exceptions.base import AtlasException',
        'AtlasException',
        'Generic fallback (no specific domain detected)'
    )


def migrate_file(filepath: Path, dry_run: bool = True) -> Dict:
    """
    Migrar un archivo a excepciones personalizadas.

    Returns:
        Dict con estadísticas de cambios
    """
    stats = {
        'file': str(filepath),
        'replacements': 0,
        'lines_changed': [],
        'imports_added': set(),
        'errors': []
    }

    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content

        # Find exception blocks
        exception_blocks = find_exception_blocks(content)

        if not exception_blocks:
            return stats

        # Process each exception block
        for line_num, line, var_name in exception_blocks:
            import_stmt, exc_class, reason = suggest_replacement(filepath, content, line_num, line)

            # Replace Exception with specific exception
            if var_name:
                new_line = line.replace(f'except Exception as {var_name}:', f'except {exc_class} as {var_name}:')
            else:
                new_line = line.replace('except Exception:', f'except {exc_class}:')

            content = content.replace(line, new_line, 1)

            stats['replacements'] += 1
            stats['lines_changed'].append({
                'line_num': line_num,
                'old': line.strip(),
                'new': new_line.strip(),
                'reason': reason
            })
            stats['imports_added'].add(import_stmt)

        # Add imports at top of file if changes were made
        if stats['replacements'] > 0:
            # Find where to insert imports (after existing imports)
            lines = content.split('\n')
            insert_pos = 0

            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    insert_pos = i + 1
                elif insert_pos > 0 and line.strip() and not line.startswith('#'):
                    break

            # Insert new imports
            for import_stmt in sorted(stats['imports_added']):
                # Check if import already exists
                if import_stmt not in content:
                    lines.insert(insert_pos, import_stmt)
                    insert_pos += 1

            content = '\n'.join(lines)

        # Write back if not dry run
        if not dry_run and content != original_content:
            filepath.write_text(content, encoding='utf-8')
            print(f"✅ Migrated {filepath} ({stats['replacements']} replacements)")
        elif dry_run and content != original_content:
            print(f"🔍 Would migrate {filepath} ({stats['replacements']} replacements)")
            for change in stats['lines_changed']:
                print(f"   Line {change['line_num']}: {change['old']} → {change['new']}")
                print(f"   Reason: {change['reason']}")

    except Exception as e:
        stats['errors'].append(str(e))
        print(f"❌ Error processing {filepath}: {e}")

    return stats


def main():
    parser = argparse.ArgumentParser(description='Migrate to custom exceptions')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    parser.add_argument('--execute', action='store_true', help='Execute changes')
    parser.add_argument('--file', type=str, help='Migrate specific file')
    parser.add_argument('--domain', type=str, help='Migrate specific domain (e.g., biology)')

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("ERROR: Must specify either --dry-run or --execute")
        sys.exit(1)

    dry_run = args.dry_run

    # Determine files to process
    if args.file:
        files = [Path(args.file)]
    elif args.domain:
        files = list(Path(f'app/domains/{args.domain}').rglob('*.py'))
    else:
        # Process high-priority files first
        priority_patterns = [
            'app/services/*.py',
            'app/domains/*/services/*.py',
            'app/routers/*.py',
            'app/autonomous/**/*.py',
        ]
        files = []
        for pattern in priority_patterns:
            files.extend(Path('.').glob(pattern))

    print(f"{'🔍 DRY RUN MODE' if dry_run else '✅ EXECUTION MODE'}")
    print(f"Processing {len(files)} files...\n")

    total_stats = {
        'files_processed': 0,
        'files_changed': 0,
        'total_replacements': 0,
        'errors': 0
    }

    for filepath in files:
        if filepath.is_file():
            stats = migrate_file(filepath, dry_run=dry_run)
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
    print(f"Total replacements: {total_stats['total_replacements']}")
    print(f"Errors: {total_stats['errors']}")

    if dry_run:
        print(f"\n⚠️  This was a dry run. Use --execute to apply changes.")
    else:
        print(f"\n✅ Migration complete!")
        print(f"\n⚠️  IMPORTANT: Run tests to verify changes:")
        print(f"   pytest tests/ -v")


if __name__ == '__main__':
    main()
