#!/usr/bin/env python3
"""
Verificación de Dependencias - AXIOM ATLAS v3.3
================================================
Verifica que todas las dependencias críticas estén instaladas y funcionales.
"""

import sys
from typing import List, Tuple

def check_module(module_name: str, import_name: str = None) -> Tuple[bool, str]:
    """Verifica si un módulo está disponible"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        return (True, "✅ OK")
    except ImportError as e:
        return (False, f"❌ NO DISPONIBLE - {str(e)[:50]}")

def main():
    print()
    print("═" * 80)
    print("🔬 AXIOM ATLAS v3.3 - Verificación de Dependencias")
    print("═" * 80)
    print()
    
    # Dependencias críticas organizadas por categoría
    dependencies = {
        "🧪 Química Computacional": [
            ("RDKit", "rdkit"),
            ("PySCF (Química Cuántica)", "pyscf"),
            ("Pymatgen (Materiales)", "pymatgen"),
        ],
        "🧬 Biología y Bioinformática": [
            ("Biopython", "Bio"),
            ("COBRApy (Metabolismo)", "cobra"),
        ],
        "🧠 Neurociencia": [
            ("Brian2", "brian2"),
            ("NEURON", "neuron"),
        ],
        "⚛️  Computación Cuántica": [
            ("Qiskit", "qiskit"),
            ("Qiskit Aer", "qiskit_aer"),
            ("Qiskit Algorithms", "qiskit_algorithms"),
            ("Cirq", "cirq"),
        ],
        "🔥 Deep Learning": [
            ("PyTorch", "torch"),
            ("TorchVision", "torchvision"),
        ],
        "🤖 Agentes IA": [
            ("LangChain", "langchain"),
            ("LangChain Community", "langchain_community"),
        ],
        "🌟 Astronomía": [
            ("Astropy", "astropy"),
        ],
        "🧮 Matemáticas y ML": [
            ("DeepXDE", "deepxde"),
            ("SymPy", "sympy"),
            ("SciPy", "scipy"),
            ("NumPy", "numpy"),
        ],
        "💾 Infraestructura": [
            ("Redis", "redis"),
            ("SQLAlchemy", "sqlalchemy"),
            ("Pydantic", "pydantic"),
        ]
    }
    
    total_checked = 0
    total_available = 0
    
    for category, modules in dependencies.items():
        print(f"{category}")
        print("-" * 80)
        
        for name, import_name in modules:
            available, status = check_module(name, import_name)
            print(f"  {name:30} {status}")
            
            total_checked += 1
            if available:
                total_available += 1
        
        print()
    
    # Verificación especial de Redis
    print("🔴 Redis Server")
    print("-" * 80)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=2)
        r.ping()
        print("  Redis Server:                  ✅ CORRIENDO (localhost:6379)")
        print("  Conectividad:                  ✅ OK")
        
        # Test de escritura/lectura
        test_key = "axiom:verification:test"
        r.set(test_key, "OK", ex=10)
        value = r.get(test_key)
        r.delete(test_key)
        print("  Test R/W:                      ✅ OK")
        
    except redis.ConnectionError:
        print("  Redis Server:                  ❌ NO ESTÁ CORRIENDO")
        print("  Solución:                      brew services start redis")
    except Exception as e:
        print(f"  Redis:                         ❌ ERROR - {str(e)[:40]}")
    
    print()
    
    # Verificación de PyTorch con MPS
    print("🔥 PyTorch - Aceleración de Hardware")
    print("-" * 80)
    try:
        import torch
        print(f"  PyTorch Version:               ✅ {torch.__version__}")
        
        if torch.backends.mps.is_available():
            print("  MPS (Apple Silicon):           ✅ DISPONIBLE")
            if torch.backends.mps.is_built():
                print("  MPS Built:                     ✅ COMPILADO")
        else:
            print("  MPS (Apple Silicon):           ⚠️  NO DISPONIBLE (usando CPU)")
        
        print(f"  CPU Threads:                   {torch.get_num_threads()}")
        
    except ImportError:
        print("  PyTorch:                       ❌ NO INSTALADO")
    except Exception as e:
        print(f"  PyTorch:                       ⚠️  {str(e)[:40]}")
    
    print()
    
    # Resumen final
    print("═" * 80)
    print("📊 RESUMEN")
    print("═" * 80)
    print()
    
    coverage = (total_available / total_checked) * 100
    
    print(f"  Módulos verificados:           {total_checked}")
    print(f"  Módulos disponibles:           {total_available}")
    print(f"  Cobertura:                     {coverage:.1f}%")
    print()
    
    if coverage >= 90:
        status = "🎉 EXCELENTE - Sistema completamente funcional"
        color = "\033[0;32m"  # Verde
    elif coverage >= 75:
        status = "✅ BUENO - La mayoría de funcionalidades disponibles"
        color = "\033[1;33m"  # Amarillo
    elif coverage >= 50:
        status = "⚠️  ACEPTABLE - Funcionalidad básica disponible"
        color = "\033[1;33m"  # Amarillo
    else:
        status = "❌ INSUFICIENTE - Instalar dependencias faltantes"
        color = "\033[0;31m"  # Rojo
    
    reset = "\033[0m"
    
    print(f"  {color}Estado: {status}{reset}")
    print()
    
    if coverage < 100:
        print("💡 Sugerencias:")
        print()
        
        if coverage < 90:
            print("  Para instalar dependencias faltantes:")
            print("    bash install_chemistry_dependencies.sh")
            print()
        
        # Verificar Redis
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
            r.ping()
        except:
            print("  Para activar Redis:")
            print("    bash setup_redis.sh")
            print()
    
    print("═" * 80)
    print()
    
    return 0 if coverage >= 75 else 1


if __name__ == "__main__":
    sys.exit(main())
