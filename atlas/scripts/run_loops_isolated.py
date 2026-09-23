#!/usr/bin/env python3
"""
Script minimalista para ejecutar loops uno por uno SIN importar app completo.
Esto evita la carga de 150+ dependencias innecesarias.
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

def run_loop_isolated(loop_name: str, script_content: str) -> dict:
    """
    Ejecuta un loop en un proceso aislado.
    """
    print(f"\n{'=' * 80}")
    print(f"🔬 Ejecutando: {loop_name}")
    print(f"{'=' * 80}\n")
    
    # Crear script temporal
    script_path = f"_temp_{loop_name.lower()}_runner.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    start_time = time.time()
    
    try:
        # Ejecutar en proceso separado con timeout
        result = subprocess.run(
            ['.venv_new/bin/python3', script_path],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos máximo por loop
            check=False
        )
        
        duration = time.time() - start_time
        
        # Parsear salida
        try:
            output_data = json.loads(result.stdout)
            success = True
            error = None
        except json.JSONDecodeError:
            output_data = {"stdout": result.stdout, "stderr": result.stderr}
            success = result.returncode == 0
            error = result.stderr if result.stderr else None
        
        print(f"✅ {loop_name} completado en {duration:.2f}s")
        
        return {
            "loop_name": loop_name,
            "success": success,
            "duration": duration,
            "result": output_data,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏱️ {loop_name} excedió el tiempo límite (300s)")
        return {
            "loop_name": loop_name,
            "success": False,
            "duration": 300.0,
            "result": None,
            "error": "Timeout after 300 seconds",
            "timestamp": datetime.now().isoformat()
        }
    except (OSError, RuntimeError, ValueError) as e:
        print(f"❌ {loop_name} falló: {e}")
        return {
            "loop_name": loop_name,
            "success": False,
            "duration": time.time() - start_time,
            "result": None,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    finally:
        # Limpiar script temporal
        Path(script_path).unlink(missing_ok=True)


# Scripts individuales para cada loop
QUANTUM_SCRIPT = """
import json
from app.autonomous.pipelines.quantum_loop import QuantumLoop

loop = QuantumLoop()
try:
    result = loop.run_iteration(iteration=1, limit=5)
except TypeError:
    try:
        result = loop.run_iteration(limit=5)
    except TypeError:
        try:
            # Fallback a llamada posicional (algunos loops requieren 'iteration' posicional)
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
"""

MATHEMATICS_SCRIPT = """
import json
from app.autonomous.pipelines.mathematics_loop import MathematicsLoop

loop = MathematicsLoop()
try:
    result = loop.run_iteration(iteration=1, limit=5)
except TypeError:
    try:
        result = loop.run_iteration(limit=5)
    except TypeError:
        try:
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
"""

BIOLOGY_SCRIPT = """
import json
from app.autonomous.pipelines.biology_loop import BiologyLoop

loop = BiologyLoop()
try:
    result = loop.run_iteration(top_n=5)
except TypeError:
    try:
        result = loop.run_iteration(top_n=3)
    except TypeError:
        try:
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
"""

CHEMISTRY_SCRIPT = """
import json
from app.autonomous.pipelines.chemistry_loop import ChemistryLoop

loop = ChemistryLoop()
try:
    result = loop.run_iteration(iteration=1, limit=5)
except TypeError:
    try:
        result = loop.run_iteration(limit=5)
    except TypeError:
        try:
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
"""

MATERIALS_SCRIPT = """
import json
from app.autonomous.pipelines.materials_loop import MaterialsLoop

loop = MaterialsLoop()
try:
    result = loop.run_iteration(iteration=1, limit=5)
except TypeError:
    try:
        result = loop.run_iteration(limit=5)
    except TypeError:
        try:
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
"""

NEUROSCIENCE_SCRIPT = """
import json
from app.autonomous.pipelines.neuroscience_loop import NeuroscienceLoop

loop = NeuroscienceLoop()
try:
    result = loop.run_iteration(iteration=1, limit=5)
except TypeError:
    try:
        result = loop.run_iteration(limit=5)
    except TypeError:
        try:
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
"""

MEDICINE_SCRIPT = """
import json
from app.autonomous.pipelines.medicine_loop import MedicineLoop

loop = MedicineLoop()
try:
    result = loop.run_iteration(iteration=1, limit=5)
except TypeError:
    try:
        result = loop.run_iteration(limit=5)
    except TypeError:
        try:
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
"""

ASTRONOMY_SCRIPT = """
import json
from app.autonomous.pipelines.astronomy_loop import AstronomyLoop

loop = AstronomyLoop()
try:
    result = loop.run_iteration(iteration=1, limit=5)
except TypeError:
    try:
        result = loop.run_iteration(limit=5)
    except TypeError:
        try:
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
"""

ENGINEERING_SCRIPT = """
import json
from app.autonomous.pipelines.engineering_loop import EngineeringLoop

loop = EngineeringLoop()
try:
    result = loop.run_iteration(iteration=1, limit=5)
except TypeError:
    try:
        result = loop.run_iteration(limit=5)
    except TypeError:
        try:
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
"""

CLIMATE_SCRIPT = """
import json
from app.autonomous.pipelines.climate_loop import ClimateLoop

loop = ClimateLoop()
try:
    result = loop.run_iteration(iteration=1, limit=5)
except TypeError:
    try:
        result = loop.run_iteration(limit=5)
    except TypeError:
        try:
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
"""


def main():
    """
    Ejecuta todos los loops usando procesos aislados.
    """
    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "🚀 AXIOM ATLAS - EXPERIMENTOS AISLADOS" + " " * 24 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    loops = [
        ("QuantumLoop", QUANTUM_SCRIPT),
        ("MathematicsLoop", MATHEMATICS_SCRIPT),
        ("BiologyLoop", BIOLOGY_SCRIPT),
        ("ChemistryLoop", CHEMISTRY_SCRIPT),
        ("MaterialsLoop", MATERIALS_SCRIPT),
        ("NeuroscienceLoop", NEUROSCIENCE_SCRIPT),
        ("MedicineLoop", MEDICINE_SCRIPT),
        ("AstronomyLoop", ASTRONOMY_SCRIPT),
        ("EngineeringLoop", ENGINEERING_SCRIPT),
        ("ClimateLoop", CLIMATE_SCRIPT),
    ]
    
    results = []
    successful = 0
    
    for loop_name, script in loops:
        result = run_loop_isolated(loop_name, script)
        results.append(result)
        if result["success"]:
            successful += 1
        
        # Pausa entre loops
        time.sleep(2)
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"isolated_loops_results_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "successful": successful,
            "total": len(loops),
            "results": results
        }, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print(f"📊 RESUMEN: {successful}/{len(loops)} loops exitosos")
    print(f"📁 Resultados: {output_file}")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
