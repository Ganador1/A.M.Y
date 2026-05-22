#!/usr/bin/env python3
"""
Script para auto-generar Pydantic response models desde routers con Dict[str, Any].

Este script:
1. Analiza routers para encontrar Dict[str, Any] en returns
2. Infiere la estructura del response desde el código
3. Genera Pydantic models automáticamente
4. Actualiza el router para usar los models

Usage:
    python scripts/maintenance/auto_create_pydantic_models.py --analyze
    python scripts/maintenance/auto_create_pydantic_models.py --generate --router app/routers/uncertainty_quantification.py
    python scripts/maintenance/auto_create_pydantic_models.py --generate-all --limit 10
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import argparse
from dataclasses import dataclass


@dataclass
class ResponseField:
    """Representa un campo de un response model"""
    name: str
    type_hint: str
    description: str = ""
    optional: bool = False


@dataclass
class ResponseModel:
    """Representa un Pydantic response model a generar"""
    class_name: str
    fields: List[ResponseField]
    description: str = ""


def analyze_router_file(filepath: Path) -> List[Dict]:
    """
    Analiza un router para encontrar funciones que retornan Dict[str, Any].

    Returns:
        Lista de diccionarios con info de cada función
    """
    results = []

    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
                # Check if return type is Dict[str, Any]
                if node.returns:
                    return_annotation = ast.unparse(node.returns)

                    if 'Dict[str, Any]' in return_annotation:
                        # Extract return statements
                        return_stmts = extract_return_statements(node)

                        # Infer fields from return statements
                        fields = infer_response_fields(return_stmts, content)

                        results.append({
                            'function_name': node.name,
                            'line': node.lineno,
                            'return_type': return_annotation,
                            'fields': fields,
                            'is_async': isinstance(node, ast.AsyncFunctionDef)
                        })

    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")

    return results


def extract_return_statements(func_node: ast.FunctionDef) -> List[ast.Return]:
    """Extrae todos los return statements de una función"""
    returns = []

    for node in ast.walk(func_node):
        if isinstance(node, ast.Return) and node.value:
            returns.append(node)

    return returns


def infer_response_fields(return_stmts: List[ast.Return], source_code: str) -> List[ResponseField]:
    """
    Infiere los campos del response desde los return statements.

    Analiza los dict literals y dict comprehensions en los returns.
    """
    fields_dict: Dict[str, ResponseField] = {}

    for ret in return_stmts:
        if isinstance(ret.value, ast.Dict):
            # Dict literal: return {"key": value, ...}
            for key_node, value_node in zip(ret.value.keys, ret.value.values):
                if isinstance(key_node, ast.Constant):
                    field_name = key_node.value
                    field_type = infer_type_from_node(value_node)

                    if field_name not in fields_dict:
                        fields_dict[field_name] = ResponseField(
                            name=field_name,
                            type_hint=field_type,
                            optional=False
                        )

        elif isinstance(ret.value, ast.Call):
            # Puede ser dict() constructor u otra función
            if isinstance(ret.value.func, ast.Name) and ret.value.func.id == 'dict':
                # dict(key=value, ...)
                for keyword in ret.value.keywords:
                    field_name = keyword.arg
                    field_type = infer_type_from_node(keyword.value)

                    if field_name not in fields_dict:
                        fields_dict[field_name] = ResponseField(
                            name=field_name,
                            type_hint=field_type,
                            optional=False
                        )

    return list(fields_dict.values())


def infer_type_from_node(node: ast.AST) -> str:
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
            return "Optional[Any]"

    elif isinstance(node, ast.List):
        if node.elts:
            # Infer from first element
            elem_type = infer_type_from_node(node.elts[0])
            return f"List[{elem_type}]"
        return "List[Any]"

    elif isinstance(node, ast.Dict):
        if node.keys and node.values:
            key_type = infer_type_from_node(node.keys[0])
            val_type = infer_type_from_node(node.values[0])
            return f"Dict[{key_type}, {val_type}]"
        return "Dict[str, Any]"

    elif isinstance(node, ast.Call):
        func_name = ast.unparse(node.func)

        # Common constructors
        if func_name == 'list':
            return "List[Any]"
        elif func_name == 'dict':
            return "Dict[str, Any]"
        elif func_name == 'str':
            return "str"
        elif func_name == 'int':
            return "int"
        elif func_name == 'float':
            return "float"

    elif isinstance(node, ast.Name):
        # Variable reference - can't infer, use Any
        return "Any"

    elif isinstance(node, ast.BinOp):
        # Binary operation - try to infer
        left_type = infer_type_from_node(node.left)
        if left_type in ["int", "float"]:
            return left_type
        return "float"  # Default for numeric ops

    return "Any"


def generate_pydantic_model(
    model: ResponseModel,
    imports: Set[str]
) -> str:
    """
    Genera el código de un Pydantic model.

    Returns:
        String con el código del model
    """
    lines = []

    # Class declaration
    lines.append(f"class {model.class_name}(BaseModel):")

    if model.description:
        lines.append(f'    """{model.description}"""')

    # Model config
    lines.append("    model_config = ConfigDict(")
    lines.append("        from_attributes=True,")
    lines.append("        validate_assignment=True")
    lines.append("    )")
    lines.append("")

    # Fields
    if not model.fields:
        lines.append("    # No fields detected - manual review needed")
        lines.append("    pass")
    else:
        for field in model.fields:
            field_type = field.type_hint

            # Add to imports if needed
            if "List" in field_type:
                imports.add("List")
            if "Dict" in field_type:
                imports.add("Dict")
            if "Optional" in field_type:
                imports.add("Optional")
            if "Union" in field_type:
                imports.add("Union")

            # Generate field
            if field.optional:
                field_type = f"Optional[{field_type}]"
                default = " = None"
            else:
                default = ""

            if field.description:
                lines.append(f'    {field.name}: {field_type}{default}  # {field.description}')
            else:
                lines.append(f'    {field.name}: {field_type}{default}')

    return '\n'.join(lines)


def create_response_model_name(function_name: str) -> str:
    """Genera el nombre del response model desde el nombre de la función"""

    # Remove common prefixes
    name = function_name
    for prefix in ['get_', 'fetch_', 'calculate_', 'process_', 'analyze_']:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Convert to PascalCase
    parts = name.split('_')
    pascal = ''.join(word.capitalize() for word in parts)

    return f"{pascal}Response"


def generate_models_file(
    router_path: Path,
    functions_data: List[Dict]
) -> Tuple[str, Set[str]]:
    """
    Genera el contenido completo del archivo de models.

    Returns:
        (contenido del archivo, set de imports necesarios)
    """
    imports = {"BaseModel", "ConfigDict", "Field"}
    models = []

    for func_data in functions_data:
        model_name = create_response_model_name(func_data['function_name'])

        response_model = ResponseModel(
            class_name=model_name,
            fields=func_data['fields'],
            description=f"Response model for {func_data['function_name']}"
        )

        model_code = generate_pydantic_model(response_model, imports)
        models.append(model_code)

    # Build file content
    lines = []
    lines.append('"""')
    lines.append(f'Response models for {router_path.stem} router.')
    lines.append('')
    lines.append('Auto-generated by scripts/maintenance/auto_create_pydantic_models.py')
    lines.append('"""')
    lines.append('')

    # Imports
    lines.append('from pydantic import BaseModel, ConfigDict, Field')

    typing_imports = sorted(imports - {"BaseModel", "ConfigDict", "Field"})
    if typing_imports:
        lines.append(f'from typing import {", ".join(typing_imports)}')

    lines.append('')
    lines.append('')

    # Models
    lines.append('\n\n\n'.join(models))

    return '\n'.join(lines), imports


def update_router_with_models(
    router_path: Path,
    functions_data: List[Dict],
    dry_run: bool = True
) -> str:
    """
    Actualiza el router para usar los response models generados.

    Returns:
        Contenido actualizado del router
    """
    content = router_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Add model import at top
    models_import = f"from app.models.responses.{router_path.stem}_responses import ("

    for i, func_data in enumerate(functions_data):
        model_name = create_response_model_name(func_data['function_name'])
        models_import += f"\n    {model_name},"

    models_import += "\n)"

    # Find where to insert import (after existing imports)
    insert_line = 0
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            insert_line = i + 1

    # Insert import
    new_lines = lines[:insert_line] + [models_import, ""] + lines[insert_line:]

    # Replace Dict[str, Any] with specific models
    for func_data in functions_data:
        model_name = create_response_model_name(func_data['function_name'])
        func_name = func_data['function_name']

        # Find and replace return type
        for i, line in enumerate(new_lines):
            if f"def {func_name}(" in line:
                # Replace Dict[str, Any] with model
                new_lines[i] = line.replace('Dict[str, Any]', model_name)

    updated_content = '\n'.join(new_lines)

    if not dry_run:
        router_path.write_text(updated_content, encoding='utf-8')

    return updated_content


def main():
    parser = argparse.ArgumentParser(
        description='Auto-generate Pydantic response models from routers'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze routers and show what would be generated'
    )
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate models for specified router'
    )
    parser.add_argument(
        '--generate-all',
        action='store_true',
        help='Generate models for all routers'
    )
    parser.add_argument(
        '--router',
        type=str,
        help='Path to specific router file'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of routers to process'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be generated without writing files'
    )

    args = parser.parse_args()

    if args.router:
        router_files = [Path(args.router)]
    else:
        # Find all router files
        routers_path = Path('app/routers')
        router_files = list(routers_path.glob('*.py'))
        router_files = [f for f in router_files if f.name != '__init__.py']

    if args.limit:
        router_files = router_files[:args.limit]

    print(f"Processing {len(router_files)} router files...")
    print()

    total_functions = 0
    total_models = 0

    for router_path in router_files:
        functions_data = analyze_router_file(router_path)

        if not functions_data:
            continue

        total_functions += len(functions_data)

        print(f"\n{'='*80}")
        print(f"Router: {router_path}")
        print(f"{'='*80}")
        print(f"Found {len(functions_data)} functions with Dict[str, Any] returns")
        print()

        if args.analyze or args.dry_run:
            # Show what would be generated
            for func_data in functions_data:
                model_name = create_response_model_name(func_data['function_name'])
                print(f"  {func_data['function_name']}() -> {model_name}")
                print(f"    Line: {func_data['line']}")
                print(f"    Fields detected: {len(func_data['fields'])}")

                if func_data['fields']:
                    for field in func_data['fields']:
                        print(f"      - {field.name}: {field.type_hint}")
                else:
                    print(f"      (No fields detected - manual review needed)")
                print()

        if args.generate or args.generate_all:
            # Generate models file
            models_content, imports = generate_models_file(router_path, functions_data)

            # Create models directory if needed
            models_dir = Path('app/models/responses')
            models_dir.mkdir(parents=True, exist_ok=True)

            # Write models file
            models_file = models_dir / f"{router_path.stem}_responses.py"

            if args.dry_run:
                print(f"\nWould create: {models_file}")
                print(f"\n{models_content[:500]}...")
            else:
                models_file.write_text(models_content, encoding='utf-8')
                print(f"✅ Created: {models_file}")
                total_models += len(functions_data)

            # Update router (if not dry-run)
            if not args.dry_run:
                updated_router = update_router_with_models(
                    router_path,
                    functions_data,
                    dry_run=False
                )
                print(f"✅ Updated: {router_path}")

    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Routers processed:        {len(router_files)}")
    print(f"Functions with Dict[str, Any]:  {total_functions}")

    if not args.dry_run and (args.generate or args.generate_all):
        print(f"Models generated:         {total_models}")
        print()
        print(f"✅ Next steps:")
        print(f"   1. Review generated models in app/models/responses/")
        print(f"   2. Add Field() descriptions where needed")
        print(f"   3. Refine inferred types (especially Any types)")
        print(f"   4. Run tests: pytest tests/")
        print(f"   5. Run mypy: mypy app/routers/")
    else:
        print(f"Models that would be generated: {total_functions}")
        print()
        print(f"💡 Run with --generate or --generate-all to create files")

    print()


if __name__ == '__main__':
    main()