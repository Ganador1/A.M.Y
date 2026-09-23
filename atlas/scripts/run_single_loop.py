#!/usr/bin/env python3
"""
Ejecuta un solo loop para debugging.
"""

import json
import time
from datetime import datetime


def run_quantum_loop():
    """Ejecuta el QuantumLoop"""
    print("🔬 Iniciando QuantumLoop...")
    
    from app.autonomous.pipelines.quantum_loop import QuantumLoop
    
    loop = QuantumLoop()
    start = time.time()
    result = loop.run_iteration(iteration=1, limit=5)
    duration = time.time() - start
    
    print(f"✅ Completado en {duration:.2f}s")
    
    # Guardar resultado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quantum_loop_result_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"📁 Resultado guardado en: {filename}")
    return result


if __name__ == "__main__":
    run_quantum_loop()
