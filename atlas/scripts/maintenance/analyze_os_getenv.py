#!/usr/bin/env python3
"""
Script para identificar todos los accesos directos a os.getenv() en el proyecto
y ayudar con la migración a pydantic-settings
"""

import re
import os
from pathlib import Path
from collections import defaultdict

def find_os_getenv_usage():
    """Encuentra todos los usos de os.getenv() en el proyecto"""
    project_root = Path(".")
    app_dir = project_root / "app"
    
    # Patrones para encontrar os.getenv
    patterns = [
        r'os\.getenv\(["\']([^"\']+)["\']',  # os.getenv('VAR')
        r'os\.getenv\([""]([^""]+)[""]',      # os.getenv("VAR")
        r'os\.environ\.get\(["\']([^"\']+)["\']',  # os.environ.get('VAR')
        r'os\.environ\[["\']([^"\']+)["\']\]',     # os.environ['VAR']
    ]
    
    results = defaultdict(list)
    total_count = 0
    
    # Buscar en archivos Python
    for py_file in app_dir.rglob("*.py"):
        if py_file.name == "__pycache__":
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_matches = []
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    file_matches.append(match)
                    total_count += 1
            
            if file_matches:
                relative_path = py_file.relative_to(project_root)
                results[str(relative_path)] = file_matches
                
        except Exception as e:
            print(f"Error leyendo {py_file}: {e}")
    
    return results, total_count

def categorize_variables(variables):
    """Categoriza las variables por tipo de configuración"""
    categories = {
        'security': [],
        'database': [],
        'api_keys': [],
        'server': [],
        'llm': [],
        'cache': [],
        'logging': [],
        'gpu': [],
        'distributed': [],
        'other': []
    }
    
    for var in variables:
        var_lower = var.lower()
        if any(keyword in var_lower for keyword in ['secret', 'key', 'token', 'auth', 'password']):
            categories['security'].append(var)
        elif any(keyword in var_lower for keyword in ['database', 'db', 'postgres', 'mysql']):
            categories['database'].append(var)
        elif any(keyword in var_lower for keyword in ['api_key', 'openai', 'huggingface', 'bearer']):
            categories['api_keys'].append(var)
        elif any(keyword in var_lower for keyword in ['host', 'port', 'url', 'base_url']):
            categories['server'].append(var)
        elif any(keyword in var_lower for keyword in ['llm', 'ollama', 'model', 'hf_', 'mlx']):
            categories['llm'].append(var)
        elif any(keyword in var_lower for keyword in ['redis', 'cache', 'ttl']):
            categories['cache'].append(var)
        elif any(keyword in var_lower for keyword in ['log', 'debug']):
            categories['logging'].append(var)
        elif any(keyword in var_lower for keyword in ['gpu', 'cuda', 'mps']):
            categories['gpu'].append(var)
        elif any(keyword in var_lower for keyword in ['distributed', 'world_size', 'rank']):
            categories['distributed'].append(var)
        else:
            categories['other'].append(var)
    
    return categories

if __name__ == "__main__":
    print("🔍 Analizando accesos directos a os.getenv() en el proyecto...")
    print("=" * 60)
    
    results, total_count = find_os_getenv_usage()
    
    print(f"📊 Total de accesos encontrados: {total_count}")
    print(f"📁 Archivos afectados: {len(results)}")
    print()
    
    # Mostrar por archivo
    for file_path, variables in results.items():
        print(f"📄 {file_path}")
        for var in set(variables):  # Eliminar duplicados
            print(f"   - {var}")
        print()
    
    # Categorizar todas las variables únicas
    all_variables = set()
    for variables in results.values():
        all_variables.update(variables)
    
    categories = categorize_variables(all_variables)
    
    print("📋 CATEGORIZACIÓN DE VARIABLES:")
    print("=" * 40)
    for category, vars_list in categories.items():
        if vars_list:
            print(f"\n🔹 {category.upper()} ({len(vars_list)} variables):")
            for var in sorted(set(vars_list)):
                print(f"   - {var}")
    
    print(f"\n✅ Análisis completado. Total: {total_count} accesos en {len(results)} archivos")
