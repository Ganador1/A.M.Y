#!/usr/bin/env python3
"""
Script para ejecutar la reorganización física de archivos en app/
"""
import json
import os
import shutil
from pathlib import Path

def execute_reorganization():
    """Ejecutar reorganización de archivos"""
    print("🔄 Ejecutando reorganización de app/...")
    
    # Cargar propuesta
    with open('artifacts/reports/app_reorganization_proposal.json', 'r') as f:
        proposal = json.load(f)
    
    classification = proposal['classification']
    
    # Crear directorios
    app_root = Path('app')
    categories = set(data['category'] for data in classification.values())
    
    print(f"📁 Creando {len(categories)} directorios de categorías...")
    for category in categories:
        category_dir = app_root / category
        category_dir.mkdir(exist_ok=True)
        
        # Crear __init__.py en cada directorio
        init_file = category_dir / '__init__.py'
        if not init_file.exists():
            init_file.write_text('"""' + f'\n{category.replace("_", " ").title()} modules\n' + '"""\n')
    
    # Mover archivos
    moved_files = []
    failed_moves = []
    
    for filename, data in classification.items():
        if filename == '__init__':  # Skip main __init__.py
            continue
            
        source_path = app_root / f'{filename}.py'
        category = data['category']
        target_dir = app_root / category
        target_path = target_dir / f'{filename}.py'
        
        if source_path.exists():
            try:
                shutil.move(str(source_path), str(target_path))
                moved_files.append({
                    'filename': filename,
                    'from': str(source_path),
                    'to': str(target_path),
                    'category': category,
                    'is_orphan': data['is_orphan']
                })
                print(f"✓ {filename}.py → app/{category}/")
            except Exception as e:
                failed_moves.append({
                    'filename': filename,
                    'error': str(e)
                })
                print(f"❌ Error moviendo {filename}.py: {e}")
        else:
            print(f"⚠️  Archivo no encontrado: {source_path}")
    
    # Generar reporte de movimientos
    move_report = {
        'reorganization_date': '2025-09-21',
        'total_files_moved': len(moved_files),
        'failed_moves': len(failed_moves),
        'moved_files': moved_files,
        'failed_moves_detail': failed_moves,
        'categories_created': sorted(list(categories))
    }
    
    with open('artifacts/reports/app_reorganization_execution.json', 'w') as f:
        json.dump(move_report, f, indent=2)
    
    print(f"\n📊 RESULTADO:")
    print(f"   Archivos movidos: {len(moved_files)}")
    print(f"   Movimientos fallidos: {len(failed_moves)}")
    print(f"   Categorías creadas: {len(categories)}")
    
    if failed_moves:
        print(f"\n❌ ERRORES:")
        for failed in failed_moves:
            print(f"   {failed['filename']}: {failed['error']}")
    
    print(f"\n💾 Reporte de ejecución: artifacts/reports/app_reorganization_execution.json")
    
    return move_report

if __name__ == '__main__':
    execute_reorganization()
