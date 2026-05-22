#!/usr/bin/env python3
"""
Script para analizar documentación y tests faltantes en archivos Python
"""

import os
import ast
from typing import Dict, List, Tuple

def has_docstring(file_path: str) -> bool:
    """Check if a Python file has a module-level docstring"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the AST to check for module docstring
        tree = ast.parse(content)

        # Check if first statement is a docstring
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, (ast.Str, ast.Constant)):
            return True

        # Check for triple-quoted string at the beginning
        lines = content.strip().split('\n')
        if lines and lines[0].startswith('"""'):
            return True

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")

    return False

def has_class_docstrings(file_path: str) -> Tuple[bool, List[str]]:
    """Check if classes in the file have docstrings"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)
        classes_without_docs = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class has docstring
                if not (node.body and isinstance(node.body[0], ast.Expr) and
                       isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                    classes_without_docs.append(node.name)

        return not classes_without_docs, classes_without_docs

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return False, []

def has_function_docstrings(file_path: str) -> Tuple[bool, List[str]]:
    """Check if functions in the file have docstrings"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)
        functions_without_docs = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private methods (starting with _)
                if node.name.startswith('_'):
                    continue

                # Check if function has docstring
                if not (node.body and isinstance(node.body[0], ast.Expr) and
                       isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                    functions_without_docs.append(node.name)

        return not functions_without_docs, functions_without_docs

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return False, []

def find_test_file(service_file: str) -> str:
    """Find corresponding test file for a service file"""
    # Convert service path to test path
    if service_file.startswith('app/'):
        # app/services/file.py -> tests/unit/test_file.py
        parts = service_file.split('/')
        if len(parts) >= 3 and parts[1] == 'services':
            filename = parts[-1].replace('.py', '')
            test_path = f"tests/unit/test_{filename}.py"
            if os.path.exists(test_path):
                return test_path

            # Also check integration tests
            test_path = f"tests/integration/test_{filename}.py"
            if os.path.exists(test_path):
                return test_path

    return ""

def analyze_python_files(root_dir: str = 'app') -> Dict[str, Dict]:
    """Analyze all Python files in the given directory"""
    results = {}

    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)

                # Skip test files themselves
                if 'test_' in file:
                    continue

                print(f"Analyzing {file_path}...")

                has_module_doc = has_docstring(file_path)
                has_class_docs, classes_without = has_class_docstrings(file_path)
                has_func_docs, funcs_without = has_function_docstrings(file_path)
                test_file = find_test_file(file_path)

                results[file_path] = {
                    'relative_path': relative_path,
                    'has_module_docstring': has_module_doc,
                    'has_class_docstrings': has_class_docs,
                    'classes_without_docs': classes_without,
                    'has_function_docstrings': has_func_docs,
                    'functions_without_docs': funcs_without,
                    'has_test_file': bool(test_file),
                    'test_file': test_file
                }

    return results

def print_report(results: Dict[str, Dict]):
    """Print analysis report"""
    print("\n" + "="*80)
    print("ANÁLISIS DE DOCUMENTACIÓN Y TESTS - ARCHIVOS PYTHON")
    print("="*80)

    # Files without module docstrings
    no_module_docs = [k for k, v in results.items() if not v['has_module_docstring']]
    print(f"\n📄 ARCHIVOS SIN DOCSTRING DE MÓDULO: {len(no_module_docs)}")
    for file in sorted(no_module_docs):
        print(f"  ❌ {results[file]['relative_path']}")

    # Files without class docstrings
    no_class_docs = [k for k, v in results.items() if not v['has_class_docstrings']]
    print(f"\n🏗️  ARCHIVOS CON CLASES SIN DOCSTRINGS: {len(no_class_docs)}")
    for file in sorted(no_class_docs):
        classes = results[file]['classes_without_docs']
        print(f"  ❌ {results[file]['relative_path']} - Clases: {', '.join(classes)}")

    # Files without function docstrings
    no_func_docs = [k for k, v in results.items() if not v['has_function_docstrings']]
    print(f"\n🔧 ARCHIVOS CON FUNCIONES SIN DOCSTRINGS: {len(no_func_docs)}")
    for file in sorted(no_func_docs):
        funcs = results[file]['functions_without_docs']
        print(f"  ❌ {results[file]['relative_path']} - Funciones: {', '.join(funcs[:5])}{'...' if len(funcs) > 5 else ''}")

    # Files without tests
    no_tests = [k for k, v in results.items() if not v['has_test_file']]
    print(f"\n🧪 ARCHIVOS SIN TESTS: {len(no_tests)}")
    for file in sorted(no_tests):
        print(f"  ❌ {results[file]['relative_path']}")

    # Summary
    total_files = len(results)
    with_docs = sum(1 for v in results.values() if v['has_module_docstring'])
    with_tests = sum(1 for v in results.values() if v['has_test_file'])

    print("\n📊 RESUMEN:")
    print(f"  Total archivos analizados: {total_files}")
    print(f"  Con docstring de módulo: {with_docs} ({with_docs/total_files*100:.1f}%)")
    print(f"  Con tests: {with_tests} ({with_tests/total_files*100:.1f}%)")

if __name__ == "__main__":
    results = analyze_python_files()
    print_report(results)
