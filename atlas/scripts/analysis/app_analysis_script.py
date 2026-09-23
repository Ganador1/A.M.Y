#!/usr/bin/env python3
"""
Script para analizar la estructura de la carpeta app/ y generar reporte detallado.
"""
import os
import ast
import json
from pathlib import Path
from datetime import datetime

def analyze_python_file(filepath):
    """Analiza un archivo Python y extrae metadatos importantes."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content, filename=str(filepath))
        
        # Extract imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Extract classes and functions
        classes = []
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                functions.append(node.name)
        
        # Extract docstring
        docstring = ast.get_docstring(tree) or ""
        
        # Analyze file characteristics
        lines = content.split('\n')
        loc = len(lines)
        
        # Determine purpose category based on name and content
        filename = Path(filepath).stem
        purpose_hints = {
            'service': any(word in filename for word in ['service', 'api', 'client']),
            'model': any(word in filename for word in ['model', 'schema', 'entity']),
            'router': 'router' in filename,
            'middleware': any(word in filename for word in ['middleware', 'auth', 'security']),
            'util': any(word in filename for word in ['util', 'helper', 'tool']),
            'config': any(word in filename for word in ['config', 'setting']),
            'database': any(word in filename for word in ['db', 'database', 'connection']),
            'core': any(word in filename for word in ['core', 'base', 'foundation']),
            'monitoring': any(word in filename for word in ['monitoring', 'metrics', 'health']),
            'advanced': filename.startswith('advanced_')
        }
        
        # Additional analysis based on content
        has_fastapi = any('fastapi' in imp.lower() for imp in imports)
        has_sqlalchemy = any('sqlalchemy' in imp.lower() for imp in imports)
        has_pydantic = any('pydantic' in imp.lower() for imp in imports)
        has_async = 'async def' in content
        
        return {
            'file': str(filepath),
            'name': filename,
            'lines_of_code': loc,
            'docstring': docstring[:200] + '...' if len(docstring) > 200 else docstring,
            'has_docstring': bool(docstring.strip()),
            'imports': imports,
            'internal_imports': [imp for imp in imports if imp.startswith('app.')],
            'external_imports': [imp for imp in imports if not imp.startswith('app.') and '.' in imp],
            'classes': classes,
            'functions': functions,
            'purpose_hints': {k: v for k, v in purpose_hints.items() if v},
            'characteristics': {
                'has_fastapi': has_fastapi,
                'has_sqlalchemy': has_sqlalchemy,
                'has_pydantic': has_pydantic,
                'has_async': has_async,
                'is_large': loc > 200
            }
        }
    except Exception as e:
        return {
            'file': str(filepath),
            'name': Path(filepath).stem,
            'error': str(e),
            'lines_of_code': 0,
            'has_docstring': False
        }

def main():
    app_root = Path('app')
    
    # Analyze root level files only
    root_files = [f for f in app_root.iterdir() if f.is_file() and f.suffix == '.py']
    
    print(f"📊 Analizando {len(root_files)} archivos Python en app/ raíz...")
    
    results = []
    for file in root_files:
        analysis = analyze_python_file(file)
        results.append(analysis)
        print(f"✓ {file.name}")
    
    # Sort by name
    results.sort(key=lambda x: x['name'])
    
    # Generate summary statistics
    total_files = len(results)
    files_with_docs = sum(1 for r in results if r.get('has_docstring', False))
    total_loc = sum(r.get('lines_of_code', 0) for r in results)
    
    # Category distribution
    categories = {}
    for result in results:
        hints = result.get('purpose_hints', {})
        if not hints:
            category = 'unknown'
        elif len(hints) == 1:
            category = list(hints.keys())[0]
        else:
            # Multiple hints, prioritize
            priority = ['router', 'service', 'middleware', 'model', 'config', 'core', 'util']
            category = next((p for p in priority if p in hints), list(hints.keys())[0])
        
        categories[category] = categories.get(category, 0) + 1
        result['suggested_category'] = category
    
    summary = {
        'analysis_date': datetime.now().isoformat(),
        'total_files': total_files,
        'total_lines_of_code': total_loc,
        'files_with_documentation': files_with_docs,
        'documentation_coverage': f"{files_with_docs/total_files*100:.1f}%" if total_files > 0 else "0%",
        'category_distribution': categories,
        'files': results
    }
    
    # Save detailed report
    with open('artifacts/reports/app_root_analysis.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📋 RESUMEN:")
    print(f"   Total archivos: {total_files}")
    print(f"   Líneas de código: {total_loc:,}")
    print(f"   Con documentación: {files_with_docs}/{total_files} ({files_with_docs/total_files*100:.1f}%)")
    print(f"\n📂 DISTRIBUCIÓN POR CATEGORÍAS:")
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count}")
    
    print(f"\n💾 Reporte guardado: artifacts/reports/app_root_analysis.json")
    
    return summary

if __name__ == '__main__':
    main()
