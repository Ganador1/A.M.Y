#!/usr/bin/env python3
"""
Script para corregir imports rotos post-reorganización
"""
import os
import re
from pathlib import Path
import json

def fix_imports_in_reorganized_modules():
    """Corregir imports en módulos reorganizados"""
    print("🔧 Corrigiendo imports en módulos reorganizados...")
    
    # Cargar información de reorganización
    with open('artifacts/reports/app_reorganization_execution.json', 'r') as f:
        reorganization = json.load(f)
    
    # Mapeo de imports que necesitan corrección
    import_fixes = {
        'from app.logging_config': 'from app.core.logging_config',
        'import app.logging_config': 'import app.core.logging_config',
        'from app.config': 'from app.core.config',
        'import app.config': 'import app.core.config',
        'from app.database': 'from app.core.database',
        'import app.database': 'import app.core.database',
        'from app.cache': 'from app.core.cache',
        'import app.cache': 'import app.core.cache',
        'from app.auth': 'from app.security.auth',
        'import app.auth': 'import app.security.auth',
        'from app.security import': 'from app.security.security import',
        'from app.health': 'from app.monitoring.health',
        'import app.health': 'import app.monitoring.health',
        'from app.metrics': 'from app.monitoring.metrics',
        'import app.metrics': 'import app.monitoring.metrics',
        'from app.monitoring import': 'from app.monitoring.monitoring import',
        'from app.gpu_manager': 'from app.distributed.gpu_manager',
        'import app.gpu_manager': 'import app.distributed.gpu_manager',
        'from app.performance_profiler': 'from app.monitoring.performance_profiler',
        'import app.performance_profiler': 'import app.monitoring.performance_profiler',
        'from app.intelligent_optimizer': 'from app.algorithms.intelligent_optimizer',
        'import app.intelligent_optimizer': 'import app.algorithms.intelligent_optimizer'
    }
    
    fixed_files = []
    
    # Corregir cada archivo movido
    for move_info in reorganization['moved_files']:
        file_path = Path(move_info['to'])
        
        if not file_path.exists():
            continue
        
        try:
            # Leer contenido
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes_made = []
            
            # Aplicar correcciones
            for old_import, new_import in import_fixes.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    changes_made.append(f"{old_import} → {new_import}")
            
            # Escribir archivo si hubo cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files.append({
                    'file': str(file_path),
                    'changes': changes_made
                })
                
                print(f"✓ {move_info['filename']}: {len(changes_made)} imports corregidos")
            
        except Exception as e:
            print(f"❌ Error procesando {file_path}: {e}")
    
    return fixed_files

def fix_main_py_imports():
    """Corregir imports en main.py"""
    print(f"\n🔧 Corrigiendo imports en main.py...")
    
    main_file = Path('main.py')
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        # Correcciones específicas para main.py
        main_fixes = {
            'from app.config import settings': 'from app.core.config import settings',
            'from app.logging_config import logger': 'from app.core.logging_config import logger',
            'from app.health import health_checker': 'from app.monitoring.health import health_checker',
            'from app.metrics import metrics': 'from app.monitoring.metrics import metrics',
            'from app.gpu_manager import gpu_manager': 'from app.distributed.gpu_manager import gpu_manager',
            'from app.performance_profiler import profiler': 'from app.monitoring.performance_profiler import profiler',
            'from app.performance_profiler import get_performance_report': 'from app.monitoring.performance_profiler import get_performance_report',
            'from app.intelligent_optimizer import optimizer': 'from app.algorithms.intelligent_optimizer import optimizer'
        }
        
        for old_import, new_import in main_fixes.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes.append(f"{old_import} → {new_import}")
        
        # Escribir si hubo cambios
        if content != original_content:
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ main.py: {len(changes)} imports corregidos")
            for change in changes:
                print(f"   - {change}")
        else:
            print("ℹ️  main.py: No requiere correcciones")
            
        return changes
        
    except Exception as e:
        print(f"❌ Error procesando main.py: {e}")
        return []

def fix_router_imports():
    """Corregir imports específicos en routers que referencian módulos movidos"""
    print(f"\n🔧 Corrigiendo imports en routers...")
    
    routers_dir = Path('app/routers')
    fixed_routers = []
    
    # Mapeo específico para routers
    router_fixes = {
        'from app.config': 'from app.core.config',
        'from app.logging_config': 'from app.core.logging_config',
        'from app.database': 'from app.core.database',
        'from app.cache': 'from app.core.cache',
        'from app.auth': 'from app.security.auth',
        'from app.metrics': 'from app.monitoring.metrics',
        'from app.health': 'from app.monitoring.health',
        'from app.gpu_manager': 'from app.distributed.gpu_manager'
    }
    
    for router_file in routers_dir.glob('*.py'):
        try:
            with open(router_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes = []
            
            for old_import, new_import in router_fixes.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    changes.append(old_import)
            
            if content != original_content:
                with open(router_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_routers.append({
                    'file': str(router_file),
                    'changes': len(changes)
                })
                
                print(f"✓ {router_file.name}: {len(changes)} imports corregidos")
        
        except Exception as e:
            print(f"❌ Error procesando {router_file}: {e}")
    
    return fixed_routers

def main():
    """Función principal de corrección de imports"""
    print("🚀 Iniciando corrección masiva de imports...")
    
    # Corregir imports en módulos reorganizados
    fixed_modules = fix_imports_in_reorganized_modules()
    
    # Corregir main.py
    main_changes = fix_main_py_imports()
    
    # Corregir routers
    fixed_routers = fix_router_imports()
    
    # Generar reporte
    fixes_report = {
        'fix_date': '2025-09-21',
        'modules_fixed': len(fixed_modules),
        'main_py_changes': len(main_changes),
        'routers_fixed': len(fixed_routers),
        'fixed_modules_detail': fixed_modules,
        'main_py_changes_detail': main_changes,
        'fixed_routers_detail': fixed_routers
    }
    
    with open('artifacts/reports/import_fixes_report.json', 'w') as f:
        json.dump(fixes_report, f, indent=2)
    
    print(f"\n📊 RESUMEN DE CORRECCIONES:")
    print(f"   Módulos reorganizados corregidos: {len(fixed_modules)}")
    print(f"   Cambios en main.py: {len(main_changes)}")
    print(f"   Routers corregidos: {len(fixed_routers)}")
    
    print(f"\n💾 Reporte de correcciones: artifacts/reports/import_fixes_report.json")
    
    return fixes_report

if __name__ == '__main__':
    main()
