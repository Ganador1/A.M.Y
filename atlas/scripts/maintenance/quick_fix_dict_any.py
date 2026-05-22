#!/usr/bin/env python3
"""
Script para hacer quick fixes de Dict[str, Any] reemplazándolos con TypedDicts básicos.

Este enfoque es más conservador pero más seguro:
1. Detecta Dict[str, Any] en returns
2. Crea TypedDicts genéricos con campos básicos
3. Reemplaza gradualmente

Usage:
    python scripts/maintenance/quick_fix_dict_any.py --file app/routers/mathlab.py --dry-run
    python scripts/maintenance/quick_fix_dict_any.py --file app/routers/mathlab.py --execute
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
import argparse


def extract_dict_any_functions(filepath: Path) -> List[Dict]:
    """
    Extrae funciones que retornan Dict[str, Any].

    Returns:
        Lista de info de funciones
    """
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    functions = []
    current_func = None

    for i, line in enumerate(lines, 1):
        # Detect function with Dict[str, Any] return
        match = re.search(
            r'(async\s+)?def\s+(\w+)\([^)]*\)\s*->\s*Dict\[str,\s*Any\]',
            line
        )

        if match:
            is_async = match.group(1) is not None
            func_name = match.group(2)

            # Extract docstring if exists
            docstring = ""
            if i < len(lines):
                next_line = lines[i].strip()
                if next_line.startswith('"""') or next_line.startswith("'''"):
                    docstring = next_line.strip('"\'')

            functions.append({
                'name': func_name,
                'line': i,
                'is_async': is_async,
                'docstring': docstring
            })

    return functions


def create_basic_response_dict(func_name: str, docstring: str = "") -> str:
    """
    Crea un TypedDict básico para un response.

    Por ahora, creamos una estructura genérica con campos comunes.
    """
    # Convert function name to TypedDict name
    parts = func_name.split('_')
    class_name = ''.join(word.capitalize() for word in parts) + 'Result'

    lines = []

    # TypedDict definition
    lines.append(f"class {class_name}(TypedDict, total=False):")

    if docstring:
        lines.append(f'    """{docstring}"""')
    else:
        lines.append(f'    """Response type for {func_name}."""')

    # Common fields (total=False means all optional)
    lines.append("    success: bool")
    lines.append("    message: str")
    lines.append("    data: Dict[str, Any]  # TODO: Specify data structure")
    lines.append("    error: str")
    lines.append("    timestamp: str")

    return '\n'.join(lines)


def generate_typeddict_file(
    router_path: Path,
    functions: List[Dict]
) -> str:
    """
    Genera un archivo de TypedDicts para el router.

    Returns:
        Contenido del archivo
    """
    lines = []

    # Header
    lines.append('"""')
    lines.append(f'TypedDict definitions for {router_path.stem} router responses.')
    lines.append('')
    lines.append('NOTE: This is a first-pass auto-generation.')
    lines.append('TODO: Refine types based on actual return values.')
    lines.append('"""')
    lines.append('')

    # Imports
    lines.append('from typing import TypedDict, Dict, List, Any, Optional')
    lines.append('')
    lines.append('')

    # Generate TypedDicts
    for func_data in functions:
        typedef = create_basic_response_dict(
            func_data['name'],
            func_data['docstring']
        )
        lines.append(typedef)
        lines.append('')
        lines.append('')

    return '\n'.join(lines)


def update_router_imports(content: str, typedef_module: str) -> str:
    """
    Agrega import de TypedDicts al router.

    Args:
        content: Contenido actual del router
        typedef_module: Nombre del módulo de typedefs (sin .py)

    Returns:
        Contenido actualizado
    """
    lines = content.split('\n')

    # Find last import line
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            last_import_idx = i

    # Add import after last import
    import_line = f"from app.types.{typedef_module} import ("

    # We'll add this later after we know which types to import
    # For now, just mark the position
    insert_position = last_import_idx + 1

    return content, insert_position


def replace_dict_any_simple(
    filepath: Path,
    functions: List[Dict],
    dry_run: bool = True
) -> str:
    """
    Reemplaza Dict[str, Any] con los TypedDicts generados.

    Estrategia simple: solo reemplazar el type hint, no el código.
    """
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Build replacements
    replacements = {}
    for func_data in functions:
        func_name = func_data['name']
        line_num = func_data['line'] - 1  # 0-indexed

        # Generate TypedDict name
        parts = func_name.split('_')
        typedef_name = ''.join(word.capitalize() for word in parts) + 'Result'

        # Replace in that line
        old_line = lines[line_num]
        new_line = old_line.replace('Dict[str, Any]', typedef_name)

        if old_line != new_line:
            replacements[line_num] = (old_line, new_line)
            lines[line_num] = new_line

    new_content = '\n'.join(lines)

    # Add import at top
    typedef_module = filepath.stem + '_types'

    # Find where to insert import
    import_insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            import_insert_idx = i + 1

    # Create import line with all TypedDict names
    typedef_names = []
    for func_data in functions:
        parts = func_data['name'].split('_')
        typedef_name = ''.join(word.capitalize() for word in parts) + 'Result'
        typedef_names.append(typedef_name)

    import_block = f"from app.types.{typedef_module} import (\n"
    for name in typedef_names:
        import_block += f"    {name},\n"
    import_block += ")"

    lines.insert(import_insert_idx, import_block)

    new_content = '\n'.join(lines)

    if not dry_run:
        filepath.write_text(new_content, encoding='utf-8')

    return new_content


def main():
    parser = argparse.ArgumentParser(
        description='Quick fix for Dict[str, Any] using TypedDicts'
    )
    parser.add_argument(
        '--file',
        type=str,
        required=True,
        help='Router file to process'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show changes without applying'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Apply changes'
    )

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("ERROR: Must specify --dry-run or --execute")
        return

    filepath = Path(args.file)

    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        return

    print(f"Processing: {filepath}")
    print()

    # Extract functions
    functions = extract_dict_any_functions(filepath)

    if not functions:
        print("No functions with Dict[str, Any] found.")
        return

    print(f"Found {len(functions)} functions with Dict[str, Any]:")
    for func in functions:
        print(f"  - Line {func['line']}: {func['name']}()")
    print()

    # Generate TypedDict file
    typedef_content = generate_typeddict_file(filepath, functions)

    typedef_module = filepath.stem + '_types'
    typedef_path = Path('app/types') / f"{typedef_module}.py"

    print(f"TypedDict file: {typedef_path}")
    print()

    if args.dry_run:
        print("="*80)
        print("TYPEDDICT FILE CONTENT (preview):")
        print("="*80)
        print(typedef_content[:800])
        print("...")
        print()

    if args.execute:
        # Create types directory
        Path('app/types').mkdir(exist_ok=True)

        # Write TypedDict file
        typedef_path.write_text(typedef_content, encoding='utf-8')
        print(f"✅ Created: {typedef_path}")

        # Update router
        updated_content = replace_dict_any_simple(filepath, functions, dry_run=False)
        print(f"✅ Updated: {filepath}")

        print()
        print("✅ DONE!")
        print()
        print("Next steps:")
        print("  1. Review generated types in app/types/")
        print("  2. Refine TypedDict fields based on actual returns")
        print("  3. Replace 'total=False' with specific required fields")
        print("  4. Run: mypy app/routers/ --show-error-codes")
        print("  5. Run: pytest tests/")
    else:
        print("💡 Run with --execute to apply changes")

    print()
    print("Summary:")
    print(f"  Functions to fix: {len(functions)}")
    print(f"  Potential type improvements: {len(functions) * 5}")  # 5 fields avg


if __name__ == '__main__':
    main()
