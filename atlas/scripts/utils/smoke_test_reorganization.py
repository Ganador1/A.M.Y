#!/usr/bin/env python3
"""
Smoke test para verificar que la reorganización no rompió imports críticos
"""
import importlib
import sys
import json
from pathlib import Path

def test_reorganized_imports():
    """Test de importación de módulos reorganizados"""
    print("🔥 Ejecutando smoke test de imports post-reorganización...")
    
    # Cargar lista de módulos movidos
    with open('artifacts/reports/app_reorganization_execution.json', 'r') as f:
        reorganization = json.load(f)
    
    success_imports = []
    failed_imports = []
    
    # Probar importar cada módulo en su nueva ubicación
    for move_info in reorganization['moved_files']:
        module_name = move_info['filename']
        new_path = move_info['to']
        category = move_info['category']
        
        # Convertir path a import path
        import_path = new_path.replace('/', '.').replace('.py', '')
        
        try:
            # Intentar importar el módulo
            module = importlib.import_module(import_path)
            success_imports.append({
                'module': module_name,
                'import_path': import_path,
                'category': category,
                'is_orphan': move_info['is_orphan']
            })
            print(f"✓ {import_path}")
            
        except Exception as e:
            failed_imports.append({
                'module': module_name,
                'import_path': import_path,
                'category': category,
                'error': str(e),
                'is_orphan': move_info['is_orphan']
            })
            print(f"❌ {import_path}: {e}")
    
    # Test específico de módulos críticos conectados
    critical_connected_modules = []
    for success in success_imports:
        if not success['is_orphan']:
            critical_connected_modules.append(success)
    
    print(f"\n📊 RESULTADOS DEL SMOKE TEST:")
    print(f"   Módulos procesados: {len(reorganization['moved_files'])}")
    print(f"   Imports exitosos: {len(success_imports)}")
    print(f"   Imports fallidos: {len(failed_imports)}")
    print(f"   Módulos conectados OK: {len(critical_connected_modules)}")
    print(f"   Tasa de éxito: {len(success_imports)/len(reorganization['moved_files'])*100:.1f}%")
    
    if failed_imports:
        print(f"\n❌ IMPORTS FALLIDOS:")
        for failed in failed_imports[:10]:  # Mostrar primeros 10
            print(f"   - {failed['import_path']}: {failed['error'][:80]}...")
    
    # Generar reporte
    smoke_test_report = {
        'test_date': '2025-09-21',
        'total_modules_tested': len(reorganization['moved_files']),
        'successful_imports': len(success_imports),
        'failed_imports': len(failed_imports),
        'success_rate': len(success_imports)/len(reorganization['moved_files'])*100,
        'critical_connected_modules_ok': len(critical_connected_modules),
        'successful_imports_detail': success_imports,
        'failed_imports_detail': failed_imports
    }
    
    with open('artifacts/reports/reorganization_smoke_test.json', 'w') as f:
        json.dump(smoke_test_report, f, indent=2)
    
    print(f"\n💾 Reporte smoke test: artifacts/reports/reorganization_smoke_test.json")
    
    return smoke_test_report

def test_main_app_import():
    """Test crítico de importación de main.py"""
    print(f"\n🚀 Probando importación de main.py...")
    
    try:
        # Verificar que main.py pueda importar sus dependencias
        with open('main.py', 'r') as f:
            main_content = f.read()
        
        # Buscar imports de app.* en main.py
        app_imports = []
        for line in main_content.split('\n'):
            line = line.strip()
            if line.startswith('from app.') or (line.startswith('import app.') and not line.startswith('import app,')):
                app_imports.append(line)
        
        print(f"   Imports de app.* encontrados en main.py: {len(app_imports)}")
        
        # Probar cada import
        import_results = []
        for import_line in app_imports:
            try:
                # Ejecutar el import
                exec(import_line)
                import_results.append({'import': import_line, 'status': 'OK'})
                print(f"   ✓ {import_line}")
            except Exception as e:
                import_results.append({'import': import_line, 'status': 'FAILED', 'error': str(e)})
                print(f"   ❌ {import_line}: {e}")
        
        return import_results
        
    except Exception as e:
        print(f"   ❌ Error leyendo main.py: {e}")
        return []

if __name__ == '__main__':
    # Ejecutar smoke tests
    reorganization_results = test_reorganized_imports()
    main_import_results = test_main_app_import()
    
    # Resumen final
    print(f"\n🎯 RESUMEN FINAL:")
    success_rate = reorganization_results['success_rate']
    if success_rate >= 95:
        print(f"   ✅ Reorganización EXITOSA ({success_rate:.1f}% de imports OK)")
    elif success_rate >= 80:
        print(f"   ⚠️  Reorganización PARCIAL ({success_rate:.1f}% de imports OK)")
    else:
        print(f"   ❌ Reorganización PROBLEMÁTICA ({success_rate:.1f}% de imports OK)")
    
    failed_count = reorganization_results['failed_imports']
    if failed_count > 0:
        print(f"   ⚠️  {failed_count} módulos requieren corrección de imports")
    
    main_ok = sum(1 for r in main_import_results if r['status'] == 'OK')
    main_total = len(main_import_results)
    if main_total > 0:
        print(f"   📋 main.py: {main_ok}/{main_total} imports OK")
