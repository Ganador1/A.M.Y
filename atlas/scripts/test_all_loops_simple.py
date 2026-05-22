#!/usr/bin/env python3
"""
🔬 AXIOM ATLAS META 4 - Test Simplificado de Todos los Loops

Test básico de importación y ejecución de cada loop autónomo.
Fecha: 2025-10-29
"""

import time
import json
import traceback
from datetime import datetime
from pathlib import Path

# Configurar paths
import sys
sys.path.insert(0, str(Path(__file__).parent))


def test_loop(loop_name: str, test_func):
    """Ejecutar test de un loop y capturar resultado"""
    print(f"\n{'='*80}")
    print(f"🧪 Probando {loop_name}...")
    print(f"{'='*80}")
    
    try:
        start_time = time.time()
        result = test_func()
        execution_time = time.time() - start_time
        
        print(f"✅ {loop_name} completado en {execution_time:.2f}s")
        
        return {
            "status": "SUCCESS",
            "loop": loop_name,
            "execution_time": round(execution_time, 2),
            "result": result
        }
    except Exception as e:
        print(f"❌ Error en {loop_name}: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        
        return {
            "status": "ERROR",
            "loop": loop_name,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


def test_quantum_loop():
    """Test QuantumLoop"""
    from app.autonomous.pipelines.quantum_loop import QuantumLoop
    loop = QuantumLoop()
    result = loop.run_iteration(iteration=1, limit=3)
    print(f"  📊 Resultado type: {type(result)}")
    print(f"  📊 Candidatos generados: {result.get('n_candidates', 'N/A') if isinstance(result, dict) else 'N/A'}")
    return result


def test_biology_loop():
    """Test BiologyLoop"""
    from app.autonomous.pipelines.biology_loop import BiologyLoop
    loop = BiologyLoop()
    result = loop.run_iteration(top_n=3)
    print(f"  📊 Resultado type: {type(result)}")
    return result


def test_mathematics_loop():
    """Test MathematicsLoop"""
    from app.autonomous.pipelines.mathematics_loop import MathematicsLoop
    loop = MathematicsLoop()
    result = loop.run_iteration(iteration=1, limit=3)
    print(f"  📊 Resultado type: {type(result)}")
    return result


def test_chemistry_loop():
    """Test ChemistryLoop"""
    from app.autonomous.pipelines.chemistry_loop import ChemistryLoop
    loop = ChemistryLoop()
    result = loop.run_iteration(top_n=3)
    print(f"  📊 Resultado type: {type(result)}")
    return result


def test_materials_loop():
    """Test MaterialsLoop"""
    from app.autonomous.pipelines.materials_loop import MaterialsLoop
    loop = MaterialsLoop()
    result = loop.run_iteration(top_n=3)
    print(f"  📊 Resultado type: {type(result)}")
    return result


def test_neuroscience_loop():
    """Test NeuroscienceLoop"""
    from app.autonomous.pipelines.neuroscience_loop import NeuroscienceLoop
    loop = NeuroscienceLoop()
    result = loop.run_iteration()
    print(f"  📊 Resultado type: {type(result)}")
    return result


def test_medicine_loop():
    """Test MedicineLoop"""
    from app.autonomous.pipelines.medicine_loop import MedicineLoop
    loop = MedicineLoop()
    result = loop.run_iteration(top_n=3)
    print(f"  📊 Resultado type: {type(result)}")
    return result


def test_astronomy_loop():
    """Test AstronomyLoop"""
    from app.autonomous.pipelines.astronomy_loop import AstronomyLoop
    loop = AstronomyLoop()
    result = loop.run_iteration(top_n=3)
    print(f"  📊 Resultado type: {type(result)}")
    return result


def test_engineering_loop():
    """Test EngineeringLoop"""
    from app.autonomous.pipelines.engineering_loop import EngineeringLoop
    loop = EngineeringLoop()
    result = loop.run_iteration(top_n=3)
    print(f"  📊 Resultado type: {type(result)}")
    return result


def test_climate_loop():
    """Test ClimateLoop"""
    from app.autonomous.pipelines.climate_loop import ClimateLoop
    loop = ClimateLoop()
    result = loop.run_iteration(top_n=3)
    print(f"  📊 Resultado type: {type(result)}")
    return result


def main():
    """Función principal"""
    print("\n" + "="*80)
    print("🚀 AXIOM ATLAS META 4 - Test de Todos los Loops Autónomos")
    print("="*80)
    
    loops = [
        ("QuantumLoop", test_quantum_loop),
        ("BiologyLoop", test_biology_loop),
        ("MathematicsLoop", test_mathematics_loop),
        ("ChemistryLoop", test_chemistry_loop),
        ("MaterialsLoop", test_materials_loop),
        ("NeuroscienceLoop", test_neuroscience_loop),
        ("MedicineLoop", test_medicine_loop),
        ("AstronomyLoop", test_astronomy_loop),
        ("EngineeringLoop", test_engineering_loop),
        ("ClimateLoop", test_climate_loop),
    ]
    
    results = {}
    total_start = time.time()
    
    for loop_name, test_func in loops:
        results[loop_name] = test_loop(loop_name, test_func)
        time.sleep(0.5)  # Pausa entre tests
    
    total_time = time.time() - total_start
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE TESTS")
    print("="*80)
    
    successful = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
    failed = sum(1 for r in results.values() if r['status'] == 'ERROR')
    
    print(f"\n✅ Tests exitosos: {successful}/10")
    print(f"❌ Tests fallidos: {failed}/10")
    print(f"⏱️  Tiempo total: {total_time:.2f}s")
    
    if successful > 0:
        print("\n📈 Tiempo de ejecución por loop:")
        for loop_name, result in results.items():
            if result['status'] == 'SUCCESS':
                exec_time = result.get('execution_time', 0)
                print(f"  {loop_name:20} {exec_time:6.2f}s")
    
    if failed > 0:
        print("\n❌ Loops con errores:")
        for loop_name, result in results.items():
            if result['status'] == 'ERROR':
                error = result.get('error', 'Unknown')[:60]
                print(f"  {loop_name:20} {error}")
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"all_loops_test_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "total_loops": 10,
            "total_time_seconds": round(total_time, 2),
            "successful": successful,
            "failed": failed,
            "results": results
        }, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    return successful == 10


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
