#!/usr/bin/env python3
"""
🔬 AXIOM ATLAS META 4 - Test Directo de Loops (sin dependencias app)

Test que importa los loops directamente sin pasar por app/__init__.py
para evitar dependencias faltantes como slowapi.

Fecha: 2025-10-29
"""

import time
import json
import sys
import importlib.util
from datetime import datetime
from pathlib import Path


def import_loop_directly(loop_file: str, class_name: str):
    """Importar un loop directamente desde su archivo"""
    spec = importlib.util.spec_from_file_location("temp_module", loop_file)
    if spec and spec.loader:
        module = spec.loader.load_module()
        return getattr(module, class_name)
    raise ImportError(f"No se pudo cargar {loop_file}")


def test_loop_initialization(loop_name: str, loop_file: str, class_name: str):
    """Probar que un loop se puede inicializar"""
    print(f"\n{'='*80}")
    print(f"🧪 Probando {loop_name}...")
    print(f"{'='*80}")
    
    try:
        start_time = time.time()
        
        # Intentar importar y crear instancia
        LoopClass = import_loop_directly(loop_file, class_name)
        loop_instance = LoopClass()
        
        init_time = time.time() - start_time
        
        # Verificar que tiene run_iteration
        has_run_iteration = hasattr(loop_instance, 'run_iteration')
        
        print(f"✅ {loop_name} inicializado correctamente")
        print(f"  ⏱️  Tiempo de inicialización: {init_time:.2f}s")
        print(f"  📝 Método run_iteration: {'✅ Presente' if has_run_iteration else '❌ Ausente'}")
        
        if has_run_iteration:
            # Inspeccionar signature
            import inspect
            sig = inspect.signature(loop_instance.run_iteration)
            print(f"  📋 Signature: run_iteration{sig}")
        
        return {
            "status": "SUCCESS",
            "loop": loop_name,
            "init_time": round(init_time, 2),
            "has_run_iteration": has_run_iteration,
            "class_name": class_name
        }
        
    except Exception as e:
        print(f"❌ Error en {loop_name}: {str(e)}")
        
        return {
            "status": "ERROR",
            "loop": loop_name,
            "error": str(e),
            "error_type": type(e).__name__
        }


def main():
    """Función principal"""
    print("\n" + "="*80)
    print("🚀 AXIOM ATLAS META 4 - Test de Inicialización de Loops")
    print("="*80)
    print("\nEste test verifica que cada loop se puede importar e inicializar")
    print("sin ejecutar experimentos (para evitar dependencias faltantes).\n")
    
    base_path = Path("/Volumes/Ganador disk/atlas/app/autonomous/pipelines")
    
    loops = [
        ("QuantumLoop", str(base_path / "quantum_loop.py"), "QuantumLoop"),
        ("BiologyLoop", str(base_path / "biology_loop.py"), "BiologyLoop"),
        ("MathematicsLoop", str(base_path / "mathematics_loop.py"), "MathematicsLoop"),
        ("ChemistryLoop", str(base_path / "chemistry_loop.py"), "ChemistryLoop"),
        ("MaterialsLoop", str(base_path / "materials_loop.py"), "MaterialsLoop"),
        ("NeuroscienceLoop", str(base_path / "neuroscience_loop.py"), "NeuroscienceLoop"),
        ("MedicineLoop", str(base_path / "medicine_loop.py"), "MedicineLoop"),
        ("AstronomyLoop", str(base_path / "astronomy_loop.py"), "AstronomyLoop"),
        ("EngineeringLoop", str(base_path / "engineering_loop.py"), "EngineeringLoop"),
        ("ClimateLoop", str(base_path / "climate_loop.py"), "ClimateLoop"),
    ]
    
    results = {}
    total_start = time.time()
    
    for loop_name, loop_file, class_name in loops:
        results[loop_name] = test_loop_initialization(loop_name, loop_file, class_name)
    
    total_time = time.time() - total_start
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE TESTS")
    print("="*80)
    
    successful = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
    failed = sum(1 for r in results.values() if r['status'] == 'ERROR')
    
    print(f"\n✅ Loops que se pueden inicializar: {successful}/10")
    print(f"❌ Loops con errores de inicialización: {failed}/10")
    print(f"⏱️  Tiempo total: {total_time:.2f}s")
    
    if successful > 0:
        print("\n📈 Detalles de loops exitosos:")
        for loop_name, result in results.items():
            if result['status'] == 'SUCCESS':
                init_time = result.get('init_time', 0)
                has_run = result.get('has_run_iteration', False)
                print(f"  {loop_name:20} {init_time:6.2f}s  run_iteration: {'✅' if has_run else '❌'}")
    
    if failed > 0:
        print("\n❌ Loops con errores:")
        for loop_name, result in results.items():
            if result['status'] == 'ERROR':
                error_type = result.get('error_type', 'Unknown')
                error = result.get('error', 'Unknown')[:50]
                print(f"  {loop_name:20} {error_type}: {error}")
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"loops_initialization_test_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_loops": 10,
            "total_time_seconds": round(total_time, 2),
            "successful": successful,
            "failed": failed,
            "results": results
        }, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    # Análisis adicional
    if successful == 10:
        print("\n" + "="*80)
        print("🎉 ¡ÉXITO TOTAL! Todos los 10 loops se pueden inicializar")
        print("="*80)
        print("\n📋 Próximos pasos sugeridos:")
        print("  1. Instalar dependencias faltantes (slowapi, etc.)")
        print("  2. Ejecutar experimentos reales con cada loop")
        print("  3. Validar resultados científicos")
    
    return successful == 10


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
