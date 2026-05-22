#!/usr/bin/env python3
"""
Script para refinar TypedDicts existentes basándose en el código real.

Reemplaza campos genéricos con tipos específicos y marca campos required.

Usage:
    python scripts/maintenance/refine_typeddict.py --analyze
    python scripts/maintenance/refine_typeddict.py --refine --file app/types/mathlab_types.py
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional
import argparse


def analyze_router_returns(router_path: Path) -> Dict[str, Dict]:
    """
    Analiza un router para encontrar qué retorna cada función.

    Returns:
        Dict con función_name -> estructura de datos retornada
    """
    content = router_path.read_text(encoding='utf-8')
    tree = ast.parse(content)

    function_returns = {}

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_name = node.name
            returns = []

            # Find all return statements
            for child in ast.walk(node):
                if isinstance(child, ast.Return) and child.value:
                    if isinstance(child.value, ast.Dict):
                        # Extract dict keys and infer types
                        return_fields = {}
                        for key, value in zip(child.value.keys, child.value.values):
                            if isinstance(key, ast.Constant):
                                field_name = key.value
                                field_type = infer_type_from_ast_node(value)
                                return_fields[field_name] = field_type

                        returns.append(return_fields)

            if returns:
                # Merge all returns to find common fields
                function_returns[func_name] = merge_return_fields(returns)

    return function_returns


def infer_type_from_ast_node(node: ast.AST) -> str:
    """Infiere el tipo Python desde un AST node"""
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, str):
            return "str"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, bool):
            return "bool"
        elif value is None:
            return "Optional[str]"
    elif isinstance(node, ast.List):
        if node.elts:
            elem_type = infer_type_from_ast_node(node.elts[0])
            return f"List[{elem_type}]"
        return "List[Any]"
    elif isinstance(node, ast.Dict):
        return "Dict[str, Any]"
    elif isinstance(node, ast.Name):
        # Variable - can't infer
        return "Any"
    elif isinstance(node, ast.Attribute):
        # Property access
        return "Any"

    return "Any"


def merge_return_fields(returns: List[Dict]) -> Dict:
    """
    Merge multiple return dictionaries to find common pattern.

    Returns:
        Dict with field_name -> (type, is_required)
    """
    all_fields = {}

    for ret in returns:
        for field, ftype in ret.items():
            if field not in all_fields:
                all_fields[field] = {
                    'type': ftype,
                    'count': 1,
                    'types_seen': {ftype}
                }
            else:
                all_fields[field]['count'] += 1
                all_fields[field]['types_seen'].add(ftype)

    # Determine if required (appears in all returns)
    total_returns = len(returns)
    result = {}

    for field, info in all_fields.items():
        is_required = info['count'] == total_returns
        # If multiple types seen, use Union or Any
        if len(info['types_seen']) > 1:
            field_type = "Any"  # Could use Union
        else:
            field_type = info['type']

        result[field] = {
            'type': field_type,
            'required': is_required
        }

    return result


def generate_refined_typedef(
    class_name: str,
    fields: Dict[str, Dict],
    docstring: str
) -> str:
    """
    Genera un TypedDict refinado con campos específicos.

    Args:
        class_name: Nombre de la clase TypedDict
        fields: Dict con field_name -> {'type': str, 'required': bool}
        docstring: Docstring para la clase

    Returns:
        String con el código del TypedDict mejorado
    """
    lines = []

    # Separar campos required y optional
    required_fields = {k: v for k, v in fields.items() if v['required']}
    optional_fields = {k: v for k, v in fields.items() if not v['required']}

    if not required_fields:
        # All optional
        lines.append(f"class {class_name}(TypedDict, total=False):")
        lines.append(f'    """{docstring}"""')

        for field, info in fields.items():
            lines.append(f"    {field}: {info['type']}")

    elif not optional_fields:
        # All required
        lines.append(f"class {class_name}(TypedDict):")
        lines.append(f'    """{docstring}"""')

        for field, info in fields.items():
            lines.append(f"    {field}: {info['type']}")

    else:
        # Mixed - use inheritance pattern
        # Create base with required fields
        base_name = f"_{class_name}Required"
        lines.append(f"class {base_name}(TypedDict):")
        lines.append(f'    """Required fields for {class_name}."""')
        for field, info in required_fields.items():
            lines.append(f"    {field}: {info['type']}")

        lines.append("")
        lines.append("")

        # Extend with optional fields
        lines.append(f"class {class_name}({base_name}, total=False):")
        lines.append(f'    """{docstring}"""')
        for field, info in optional_fields.items():
            lines.append(f"    {field}: {info['type']}")

    return '\n'.join(lines)


def refine_typedef_file(
    typedef_path: Path,
    router_path: Path,
    dry_run: bool = True
) -> str:
    """
    Refina un archivo TypedDict completo.

    Args:
        typedef_path: Path al archivo TypedDict
        router_path: Path al router correspondiente
        dry_run: Si True, solo muestra cambios

    Returns:
        Contenido refinado
    """
    # Analyze router
    function_returns = analyze_router_returns(router_path)

    print(f"Analyzed {router_path.name}")
    print(f"Found {len(function_returns)} functions with returns")
    print()

    # Read current typedef file
    typedef_content = typedef_path.read_text(encoding='utf-8')

    # Extract existing TypedDict classes
    class_pattern = r'class (\w+)\(TypedDict.*?\):\s*"""(.+?)"""'
    matches = re.findall(class_pattern, typedef_content, re.DOTALL)

    print(f"Found {len(matches)} TypedDict classes")
    print()

    # Generate refined version
    lines = []
    lines.append('"""')
    lines.append(f'Refined TypedDict definitions for {router_path.stem} router.')
    lines.append('')
    lines.append('Auto-refined by scripts/maintenance/refine_typeddict.py')
    lines.append('Based on actual return values from router code.')
    lines.append('"""')
    lines.append('')
    lines.append('from typing import TypedDict, Dict, List, Any, Optional, Union')
    lines.append('')
    lines.append('')

    for class_name, docstring in matches:
        # Try to find corresponding function
        func_name = class_name.replace('Result', '').replace('Response', '')

        # Convert PascalCase to snake_case
        snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', func_name).lower()

        if snake_name in function_returns:
            fields = function_returns[snake_name]
            refined = generate_refined_typedef(class_name, fields, docstring.strip())
            lines.append(refined)
        else:
            # Keep original if no match found
            print(f"⚠️  No match found for {class_name} (tried {snake_name})")
            lines.append(f"class {class_name}(TypedDict, total=False):")
            lines.append(f'    """{docstring.strip()}"""')
            lines.append("    # TODO: Could not infer fields from router")
            lines.append("    pass")

        lines.append('')
        lines.append('')

    refined_content = '\n'.join(lines)

    if not dry_run:
        typedef_path.write_text(refined_content, encoding='utf-8')
        print(f"✅ Refined: {typedef_path}")
    else:
        print("=" * 80)
        print("REFINED VERSION (preview):")
        print("=" * 80)
        print(refined_content[:1000])
        print("...")

    return refined_content


def main():
    parser = argparse.ArgumentParser(description='Refine TypedDict definitions')
    parser.add_argument('--analyze', action='store_true', help='Analyze routers')
    parser.add_argument('--refine', action='store_true', help='Refine TypedDict files')
    parser.add_argument('--file', type=str, help='Specific TypedDict file to refine')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without writing')

    args = parser.parse_args()

    if args.refine and args.file:
        typedef_path = Path(args.file)

        # Find corresponding router
        router_name = typedef_path.stem.replace('_types', '.py')
        router_path = Path('app/routers') / router_name

        if not router_path.exists():
            print(f"❌ Router not found: {router_path}")
            return

        refine_typedef_file(typedef_path, router_path, dry_run=args.dry_run)

    elif args.analyze:
        # Analyze all typedef files
        types_dir = Path('app/types')

        for typedef_file in types_dir.glob('*_types.py'):
            router_name = typedef_file.stem.replace('_types', '.py')
            router_path = Path('app/routers') / router_name

            if router_path.exists():
                print(f"\n{'='*80}")
                print(f"Analyzing: {typedef_file.name}")
                print(f"{'='*80}")

                function_returns = analyze_router_returns(router_path)

                for func_name, fields in function_returns.items():
                    print(f"\n{func_name}():")
                    for field_name, info in fields.items():
                        req = "required" if info['required'] else "optional"
                        print(f"  - {field_name}: {info['type']} ({req})")

    else:
        print("Use --analyze or --refine")


if __name__ == '__main__':
    main()
