#!/usr/bin/env python3
"""
Ejecuta solo los 5 loops restantes que no completaron.
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

def run_loop_isolated(loop_name: str, script_content: str) -> dict:
    """Ejecuta un loop en un proceso aislado."""
    print(f"\n{'=' * 80}")
    print(f"🔬 Ejecutando: {loop_name}")
    print(f"{'=' * 80}\n")
    
    script_path = f"_temp_{loop_name.lower()}_runner.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ['.venv_new/bin/python3', script_path],
            capture_output=True,
            text=True,
            timeout=300,
            check=False
        )
        
        duration = time.time() - start_time
        
        try:
            output_data = json.loads(result.stdout)
            success = True
            error = None
        except json.JSONDecodeError:
            output_data = {"stdout": result.stdout[:1000], "stderr": result.stderr[:1000]}
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
        print(f"⏱️ {loop_name} excedió 300s")
        return {
            "loop_name": loop_name,
            "success": False,
            "duration": 300.0,
            "result": None,
            "error": "Timeout",
            "timestamp": datetime.now().isoformat()
        }
    finally:
        Path(script_path).unlink(missing_ok=True)


# Solo los loops restantes
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
        result = loop.run_iteration()
print(json.dumps(result, default=str))
"""


def main():
    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 10 + "🚀 Completando Loops Restantes (6-10)" + " " * 29 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    loops = [
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
        time.sleep(2)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"remaining_loops_results_{timestamp}.json"
    
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
