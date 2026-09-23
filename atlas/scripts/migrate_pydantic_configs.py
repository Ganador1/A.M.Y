#!/usr/bin/env python3
"""
Script para migrar automáticamente class Config a ConfigDict en archivos Python.
Migra de Pydantic v1 style Config a Pydantic v2 ConfigDict.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def find_files_with_config_classes(root_dir: str) -> List[Path]:
    """Encuentra archivos Python con 'class Config:' que necesitan migración."""
    
    files_to_migrate = []
    root_path = Path(root_dir)
    
    # Buscar archivos .py recursivamente
    for py_file in root_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            if 'class Config:' in content and 'BaseModel' in content:
                files_to_migrate.append(py_file)
        except (UnicodeDecodeError, PermissionError):
            continue
    
    return files_to_migrate


def migrate_file(file_path: Path) -> Tuple[bool, str]:
    """Migra un archivo individual de class Config a ConfigDict."""
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Verificar si ya tiene ConfigDict importado
        needs_import = 'ConfigDict' not in content
        
        # Agregar import de ConfigDict si es necesario
        if needs_import and 'from pydantic import' in content:
            # Buscar línea de import de pydantic y agregar ConfigDict
            content = re.sub(
                r'(from pydantic import [^\\n]*)(BaseModel[^\\n]*)',
                r'\\1\\2, ConfigDict',
                content
            )
            
            # Si no se pudo agregar a la línea existente, crear nueva línea
            if 'ConfigDict' not in content:
                content = re.sub(
                    r'(from pydantic import [^\\n]*\\n)',
                    r'\\1from pydantic import ConfigDict\\n',
                    content
                )
        
        # Patrón para encontrar class Config dentro de BaseModel
        config_pattern = r'(class\s+\w+\s*\([^)]*BaseModel[^)]*\):[^{]*?)(\s+class Config:\s*\n((?:\s{8,}[^\n]*\n)*))(\s+\w+:)'
        
        def replace_config(match):
            class_def = match.group(1)
            config_content = match.group(3).strip()
            next_field = match.group(4)
            
            # Extraer contenido del Config
            config_lines = config_content.split('\n')
            config_dict_content = []
            
            for line in config_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    config_dict_content.append(f'        {line}')
            
            # Crear el model_config
            if config_dict_content:
                model_config = f'''    model_config = ConfigDict(
{chr(10).join(config_dict_content)}
    )
    
'''
            else:
                model_config = '    model_config = ConfigDict()\n    \n'
            
            return f'{class_def}{model_config}{next_field}'
        
        # Aplicar la migración
        content = re.sub(config_pattern, replace_config, content, flags=re.MULTILINE)
        
        # Solo escribir si hubo cambios
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True, "Migrado exitosamente"
        else:
            return False, "No necesitaba migración"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Función principal para ejecutar la migración."""
    
    app_dir = "app"
    if not os.path.exists(app_dir):
        print("❌ Directorio 'app' no encontrado")
        return
    
    print("🔍 Buscando archivos con class Config...")
    files_to_migrate = find_files_with_config_classes(app_dir)
    
    if not files_to_migrate:
        print("✅ No se encontraron archivos que necesiten migración")
        return
    
    print(f"📁 Encontrados {len(files_to_migrate)} archivos para migrar:")
    for file_path in files_to_migrate:
        print(f"  - {file_path}")
    
    print("\n🚀 Iniciando migración...")
    migrated_count = 0
    
    for file_path in files_to_migrate:
        print(f"📝 Procesando: {file_path}")
        success, message = migrate_file(file_path)
        
        if success:
            print(f"  ✅ {message}")
            migrated_count += 1
        else:
            print(f"  ⚠️  {message}")
    
    print(f"\n🎉 Migración completada!")
    print(f"  - Archivos migrados: {migrated_count}")
    print(f"  - Total procesados: {len(files_to_migrate)}")
    

if __name__ == "__main__":
    main()