#!/usr/bin/env python3
"""
Script para corregir imports de modelos después de reorganización
"""
import os
import re
from pathlib import Path


def fix_model_imports_in_file(file_path: Path) -> bool:
    """Corregir imports de modelos en un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones de imports de modelos incorrectos
        model_import_fixes = [
            # from app.models.database_models import ArithmeticRequest -> from app.models import ArithmeticRequest
            (r'from app\.models\.database_models import ([A-Za-z_][A-Za-z0-9_,\s]*)', r'from app.models import \1'),
            
            # from app.database_models import -> from app.models import
            (r'from app\.database_models import ([A-Za-z_][A-Za-z0-9_,\s]*)', r'from app.models import \1'),
            
            # import app.models.database_models as -> import app.models as  
            (r'import app\.models\.database_models as ([A-Za-z_][A-Za-z0-9_]*)', r'import app.models as \1'),
            
            # Referencias a app.models.database_models. -> app.models.
            (r'app\.models\.database_models\.([A-Za-z_][A-Za-z0-9_]*)', r'app.models.\1'),
        ]
        
        changes_made = False
        for pattern, replacement in model_import_fixes:
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
    """Ejecutar corrección de imports de modelos"""
    print("🔧 Corrigiendo imports de modelos post-reorganización...")
    
    # Directorios a procesar
    directories = ['app', 'main.py']
    
    total_files = 0
    fixed_files = 0
    
    # Procesar main.py específicamente
    if os.path.exists('main.py'):
        total_files += 1
        if fix_model_imports_in_file(Path('main.py')):
            print(f"  ✅ main.py")
            fixed_files += 1
    
    # Procesar directorios
    for directory in directories:
        if directory == 'main.py':
            continue
            
        for root, dirs, files in os.walk(directory):
            # Evitar ciertos directorios
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', '.pytest_cache']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    total_files += 1
                    
                    if fix_model_imports_in_file(file_path):
                        print(f"  ✅ {file_path}")
                        fixed_files += 1
    
    print(f"\n📊 Resultados:")
    print(f"   • Archivos procesados: {total_files}")
    print(f"   • Archivos corregidos: {fixed_files}")
    
    return fixed_files


if __name__ == '__main__':
    main()
