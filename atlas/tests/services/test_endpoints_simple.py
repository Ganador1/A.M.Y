#!/usr/bin/env python3
"""
Test de endpoints simples sin base de datos completa
"""

def test_import_core_services():
    """Test básico de importación de servicios principales"""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        # Test importaciones básicas
        from app.services.lean4_installer import Lean4InstallerService
        from app.services.conformal_prediction import ConformalPredictionService
        from app.uncertainty_quantification import MonteCarloDropoutQuantifier, EnsembleQuantifier
        
        # Verificar que las clases se pueden instanciar
        lean4_service = Lean4InstallerService()
        conformal_service = ConformalPredictionService()
        mc_quantifier = MonteCarloDropoutQuantifier()
        ensemble_quantifier = EnsembleQuantifier()
        
        assert lean4_service is not None
        assert conformal_service is not None
        assert mc_quantifier is not None
        assert ensemble_quantifier is not None
        
        print("✅ Core services import: PASS")
        return True
    except Exception as e:
        print(f"❌ Core services import: FAIL - {e}")
        return False

def test_lean4_basic_functionality():
    """Test básico de funcionalidad Lean4"""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        from app.services.lean4_installer import Lean4InstallerService
        
        installer = Lean4InstallerService()
        
        # Test detección de OS
        os_info = installer._detect_os()
        assert isinstance(os_info, dict)
        assert "system" in os_info
        assert "architecture" in os_info
        
        print("✅ Lean4 basic functionality: PASS")
        return True
    except Exception as e:
        print(f"❌ Lean4 basic functionality: FAIL - {e}")
        return False

def test_conformal_prediction_basic():
    """Test básico de conformal prediction"""
    try:
        import sys
        import os
        import numpy as np
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        from app.services.conformal_prediction import ConformalPredictionService
        
        service = ConformalPredictionService()
        
        # Datos de prueba simples
        X_cal = np.random.rand(50, 2)
        y_cal = np.random.rand(50)
        X_test = np.random.rand(10, 2)
        
        # Test split conformal prediction
        result = service.split_conformal_prediction(X_cal, y_cal, X_test, alpha=0.1)
        
        assert "predictions" in result
        assert "prediction_intervals" in result
        assert "coverage_probability" in result
        
        print("✅ Conformal prediction basic: PASS")
        return True
    except Exception as e:
        print(f"❌ Conformal prediction basic: FAIL - {e}")
        return False

def test_uncertainty_quantification_basic():
    """Test básico de uncertainty quantification"""
    try:
        import sys
        import os
        import numpy as np
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        from app.uncertainty_quantification import MonteCarloDropoutQuantifier
        
        quantifier = MonteCarloDropoutQuantifier()
        
        # Datos de prueba simples
        X = np.random.rand(100, 10)
        y = np.random.rand(100)
        
        # Test quantify_uncertainty
        result = quantifier.quantify_uncertainty(X, y, n_samples=10)
        
        assert "mean_prediction" in result
        assert "epistemic_uncertainty" in result
        assert "confidence_intervals" in result
        
        print("✅ Uncertainty quantification basic: PASS")
        return True
    except Exception as e:
        print(f"❌ Uncertainty quantification basic: FAIL - {e}")
        return False

def test_quantum_basic_math():
    """Test matemáticas básicas para quantum"""
    try:
        import sys
        import os
        import math
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        # Test funciones auxiliares de Shor
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
        
        # Test función de período clásica
        def find_period_classical(a, N):
            """Encuentra período r tal que a^r ≡ 1 (mod N)"""
            for r in range(1, N):
                if pow(a, r, N) == 1:
                    return r
            return None
        
        # Tests
        assert gcd(15, 21) == 3
        assert is_prime(17) == True
        assert is_prime(15) == False
        assert find_period_classical(2, 15) == 4  # 2^4 ≡ 1 (mod 15)
        
        print("✅ Quantum basic math: PASS")
        return True
    except Exception as e:
        print(f"❌ Quantum basic math: FAIL - {e}")
        return False

if __name__ == "__main__":
    print("🧪 Ejecutando tests de endpoints simples...\n")
    
    results = []
    results.append(test_import_core_services())
    results.append(test_lean4_basic_functionality())
    results.append(test_conformal_prediction_basic())
    results.append(test_uncertainty_quantification_basic())
    results.append(test_quantum_basic_math())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests de endpoints pasaron!")
        exit(0)
    else:
        print("⚠️  Algunos tests fallaron")
        exit(1)
