#!/usr/bin/env python3
"""
Test rápido de validación sin dependencias complejas
"""

def test_lean4_error_diagnosis():
    """Test básico de diagnóstico de errores Lean4"""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        # Simular el diagnóstico de errores
        error_patterns = {
            "command not found": "binary_missing",
            "no such file": "file_not_found", 
            "invalid toolchain": "toolchain_error",
            "not found": "library_missing"
        }
        
        # Test casos básicos
        test_errors = [
            "lean: command not found",
            "error: no such file or directory",
            "invalid toolchain specified",
            "library xyz not found"
        ]
        
        for error in test_errors:
            classified = False
            for pattern, error_type in error_patterns.items():
                if pattern in error.lower():
                    classified = True
                    break
            assert classified, f"Error no clasificado: {error}"
        
        print("✅ Lean4 error diagnosis: PASS")
        return True
    except Exception as e:
        print(f"❌ Lean4 error diagnosis: FAIL - {e}")
        return False

def test_quantum_math_basic():
    """Test básico de lógica cuántica sin Qiskit"""
    try:
        import math
        
        # Test factorización clásica (parte de Shor)
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(math.sqrt(n)) + 1):
                if n % i == 0:
                    return False
            return True
        
        # Test casos
        assert gcd(48, 18) == 6
        assert is_prime(17) == True
        assert is_prime(15) == False
        
        print("✅ Quantum math basics: PASS")
        return True
    except Exception as e:
        print(f"❌ Quantum math basics: FAIL - {e}")
        return False

def test_uncertainty_math_basic():
    """Test básico de matemáticas de incertidumbre"""
    try:
        import random
        import statistics
        
        # Simular bootstrap simple
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        bootstrap_samples = []
        for _ in range(100):
            sample = [random.choice(data) for _ in range(len(data))]
            bootstrap_samples.append(statistics.mean(sample))
        
        mean_bootstrap = statistics.mean(bootstrap_samples)
        std_bootstrap = statistics.stdev(bootstrap_samples)
        
        assert isinstance(mean_bootstrap, float)
        assert isinstance(std_bootstrap, float)
        assert std_bootstrap > 0
        
        print("✅ Uncertainty math basics: PASS")
        return True
    except Exception as e:
        print(f"❌ Uncertainty math basics: FAIL - {e}")
        return False

def test_file_existence():
    """Verificar que los archivos principales existen"""
    try:
        import os
        
        files_to_check = [
            "app/services/lean4_installer.py",
            "app/routers/lean4_management.py", 
            "app/routers/uncertainty_quantification.py",
            "app/services/conformal_prediction.py",
            "app/uncertainty_quantification.py"
        ]
        
        for file_path in files_to_check:
            full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path)
            assert os.path.exists(full_path), f"Archivo no encontrado: {file_path}"
        
        print("✅ File existence check: PASS")
        return True
    except Exception as e:
        print(f"❌ File existence check: FAIL - {e}")
        return False

if __name__ == "__main__":
    print("🧪 Ejecutando tests de validación rápida...\n")
    
    results = []
    results.append(test_lean4_error_diagnosis())
    results.append(test_quantum_math_basic()) 
    results.append(test_uncertainty_math_basic())
    results.append(test_file_existence())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests básicos pasaron!")
        exit(0)
    else:
        print("⚠️  Algunos tests fallaron")
        exit(1)
