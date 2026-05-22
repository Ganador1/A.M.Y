#!/usr/bin/env python3
"""
Script para corregir todos los imports de logging_config a bootstrap_logging
"""
import os
import re
from pathlib import Path


def fix_imports_in_file(file_path: Path) -> bool:
    """Corregir imports en un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones de imports a corregir
        patterns = [
            # from app.logging_config import logger
            (r'from app\.logging_config import logger', 'from app.core.bootstrap_logging import logger'),
            # from app.core.logging_config import logger  
            (r'from app\.core\.logging_config import logger', 'from app.core.bootstrap_logging import logger'),
            # from app.core.logging_config import (varias cosas)
            (r'from app\.core\.logging_config import ([^,\n]+)', r'from app.core.bootstrap_logging import \1'),
            # import app.logging_config
            (r'import app\.logging_config', 'import app.core.bootstrap_logging'),
            # app.logging_config.logger -> app.core.bootstrap_logging.logger
            (r'app\.logging_config\.logger', 'app.core.bootstrap_logging.logger'),
        ]
        
        changes_made = False
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes_made = True
        
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False
    
    return False


def main():
    """Ejecutar corrección de imports"""
    print("🔧 Corrigiendo imports de logging_config a bootstrap_logging...")
    
    # Directorios a procesar
    directories = ['app']
    
    total_files = 0
    fixed_files = 0
    
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            # Evitar ciertos directorios
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    total_files += 1
                    
                    if fix_imports_in_file(file_path):
                        print(f"  ✅ {file_path}")
                        fixed_files += 1
    
    print(f"\n📊 Resultados:")
    print(f"   • Archivos procesados: {total_files}")
    print(f"   • Archivos corregidos: {fixed_files}")
    
    if fixed_files > 0:
        print(f"\n🎯 Probando import básico...")
        try:
            # Test básico
            import importlib
            importlib.invalidate_caches()
            
            # Probar imports críticos
            import app.core.bootstrap_logging
            print("   ✅ bootstrap_logging funciona")
            
            import app.core.cache
            print("   ✅ cache funciona")
            
        except Exception as e:
            print(f"   ❌ Error en test: {e}")
    
    return fixed_files


if __name__ == '__main__':
    main()
