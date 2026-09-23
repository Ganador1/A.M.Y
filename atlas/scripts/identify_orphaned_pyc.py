#!/usr/bin/env python3
"""
Script para identificar archivos .pyc huérfanos en el directorio app/
Un archivo .pyc es huérfano si no existe su archivo .py correspondiente.
"""
import os
from pathlib import Path

def find_orphaned_pyc_files(app_dir: str):
    """Encuentra archivos .pyc que no tienen .py correspondientes"""
    orphaned_files = []
    app_path = Path(app_dir)
    
    # Encontrar todos los archivos .pyc
    for pyc_file in app_path.rglob("*.pyc"):
        # Construir la ruta del archivo .py esperado
        relative_path = pyc_file.relative_to(app_path)
        
        # Si está en __pycache__, necesitamos reconstruir el path original
        if "__pycache__" in pyc_file.parts:
            # Ejemplo: app/__pycache__/cache.cpython-313.pyc -> app/cache.py
            pycache_dir = pyc_file.parent
            parent_dir = pycache_dir.parent
            
            # Extraer el nombre base del archivo .pyc
            filename = pyc_file.stem  # Ejemplo: cache.cpython-313
            base_name = filename.split('.')[0]  # Ejemplo: cache
            
            expected_py_file = parent_dir / f"{base_name}.py"
        else:
            # Para archivos .pyc fuera de __pycache__ (raro pero posible)
            expected_py_file = pyc_file.with_suffix('.py')
        
        # Verificar si el archivo .py existe
        if not expected_py_file.exists():
            orphaned_files.append({
                'pyc_file': str(pyc_file),
                'expected_py_file': str(expected_py_file),
                'size': pyc_file.stat().st_size,
                'relative_path': str(relative_path)
            })
    
    return orphaned_files

if __name__ == "__main__":
    app_directory = "./app"
    orphaned = find_orphaned_pyc_files(app_directory)
    
    print(f"🔍 Encontrados {len(orphaned)} archivos .pyc huérfanos:")
    print()
    
    total_size = 0
    for item in orphaned:
        total_size += item['size']
        print(f"  • {item['relative_path']}")
        print(f"    Esperaba encontrar: {item['expected_py_file'].replace('./', '')}")
        print()
    
    print(f"📊 Tamaño total de archivos huérfanos: {total_size:,} bytes ({total_size / 1024:.1f} KB)")
    
    if orphaned:
        print("\n🧹 Para limpiar estos archivos, puedes ejecutar:")
        print("python clean_orphaned_pyc.py --delete")
