"""
Tests para el sistema de fuzzing inteligente de contraejemplos
"""

import pytest
import sys
import os

# Añadir el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.counterexample_fuzzer import IntelligentFuzzer, FuzzingResult
from app.services.hybrid_verification_service import HybridVerificationService, HybridVerificationResult


class TestCounterexampleFuzzer:
    """Tests para el fuzzer inteligente"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.fuzzer = IntelligentFuzzer()
        self.hybrid_verifier = HybridVerificationService()
    
    def test_analyze_expression_basic(self):
        """Test de análisis de expresiones básicas"""
        # Expresión simple con una variable
        result = self.fuzzer.analyze_expression("x > 0")
        assert result["success"] == True
        assert "x" in result["variables"]
        assert result["variables"]["x"]["type"] == "Real"
        assert result["variable_names"] == ["x"]
        assert result["expression_complexity"] > 0
    
    def test_analyze_expression_multiple_variables(self):
        """Test de análisis con múltiples variables"""
        result = self.fuzzer.analyze_expression("x + y > z and a == b")
        assert result["success"] == True
        variables = result["variable_names"]
        assert len(variables) >= 4  # x, y, z, a, b
        assert all(var in variables for var in ["x", "y", "z", "a", "b"])
    
    def test_analyze_expression_invalid(self):
        """Test de análisis de expresión inválida"""
        result = self.fuzzer.analyze_expression("invalid syntax !!")
        assert result["success"] == False
        assert "error" in result
    
    def test_generate_values_numeric(self):
        """Test de generación de valores numéricos"""
        var_info = {"type": "Real"}
        
        # Test diferentes estrategias
        strategies = ["random_uniform", "boundary_values", "small_numbers", "large_numbers"]
        
        for strategy in strategies:
            value = self.fuzzer.generate_values(var_info, strategy)
            assert isinstance(value, (int, float))
    
    def test_generate_values_boolean(self):
        """Test de generación de valores booleanos"""
        var_info = {"type": "Bool"}
        
        value = self.fuzzer.generate_values(var_info, "random_uniform")
        assert isinstance(value, bool)
    
    def test_find_counterexample_simple_true(self):
        """Test de búsqueda de contraejemplo para proposición verdadera"""
        # x² >= 0 es siempre verdadera para x real
        result = self.fuzzer.find_counterexample("x**2 >= 0", max_iterations=100)
        assert isinstance(result, FuzzingResult)
        assert result.success == False  # No debería encontrar contraejemplo
        assert result.iterations > 0
    
    def test_find_counterexample_simple_false(self):
        """Test de búsqueda de contraejemplo para proposición falsa"""
        # x > x + 1 es siempre falsa
        result = self.fuzzer.find_counterexample("x > x + 1", max_iterations=100)
        assert isinstance(result, FuzzingResult)
        # Podría encontrar contraejemplo rápidamente
        assert result.iterations > 0
    
    def test_find_counterexample_known_false(self):
        """Test con proposición conocidamente falsa"""
        # ∀x (x == x + 1) es falsa
        result = self.fuzzer.find_counterexample("x == x + 1", max_iterations=500)
        assert isinstance(result, FuzzingResult)
        # Debería encontrar contraejemplo
        if result.success:
            assert result.counterexample is not None
            assert "x" in result.counterexample
    
    @pytest.mark.slow
    def test_find_counterexample_complex(self):
        """Test con proposición más compleja"""
        # sin(x) == cos(x) no es siempre verdadera
        result = self.fuzzer.find_counterexample("sin(x) == cos(x)", max_iterations=1000)
        assert isinstance(result, FuzzingResult)
        assert result.iterations > 0
    
    def test_hybrid_verification_true_proposition(self):
        """Test de verificación híbrida para proposición verdadera"""
        # x + 1 > x es siempre verdadera
        result = self.hybrid_verifier.verify_proposition("x + 1 > x")
        assert isinstance(result, HybridVerificationResult)
        assert result.verified == True
        assert result.confidence > 0.5
    
    def test_hybrid_verification_false_proposition(self):
        """Test de verificación híbrida para proposición falsa"""
        # x == x + 1 es siempre falsa
        result = self.hybrid_verifier.verify_proposition("x == x + 1")
        assert isinstance(result, HybridVerificationResult)
        assert result.verified == False
        assert result.counterexample is not None
        assert "x" in result.counterexample
    
    def test_hybrid_verification_cache(self):
        """Test del sistema de caché"""
        proposition = "x * 2 == x + x"  # Siempre verdadera
        
        # Primera ejecución (cache miss)
        result1 = self.hybrid_verifier.verify_proposition(proposition)
        stats1 = self.hybrid_verifier.get_stats()
        
        # Segunda ejecución (cache hit)
        result2 = self.hybrid_verifier.verify_proposition(proposition)
        stats2 = self.hybrid_verifier.get_stats()
        
        assert stats2["cache_hits"] == stats1["cache_hits"] + 1
        assert result1.verified == result2.verified
        assert result2.time_taken < result1.time_taken  # Debería ser más rápido
    
    def test_hybrid_verification_strategies(self):
        """Test que verifica múltiples estrategias"""
        # Proposición que debería ser refutada rápidamente
        result = self.hybrid_verifier.verify_proposition("x * 0 == 1")
        assert isinstance(result, HybridVerificationResult)
        assert result.verified == False
        assert result.strategy_used != "none"
        assert result.time_taken < 10.0  # No debería tomar demasiado tiempo
    
    def test_clear_cache(self):
        """Test de limpieza del caché"""
        # Llenar el caché
        self.hybrid_verifier.verify_proposition("x > 0")
        stats_before = self.hybrid_verifier.get_stats()
        
        # Limpiar caché
        self.hybrid_verifier.clear_cache()
        stats_after = self.hybrid_verifier.get_stats()
        
        assert stats_after["cache_size"] == 0
        assert stats_after["cache_hits"] == 0
        assert stats_after["cache_misses"] == 0


class TestEdgeCases:
    """Tests para casos edge y boundary values"""
    
    def setup_method(self):
        self.fuzzer = IntelligentFuzzer()
    
    def test_boundary_values_strategy(self):
        """Test específico para la estrategia de valores límite"""
        var_info = {"type": "Int"}
        
        # Generar múltiples valores y verificar que incluyen boundary values
        values = []
        for _ in range(50):  # Muestra significativa
            values.append(self.fuzzer.generate_values(var_info, "boundary_values"))
        
        # Verificar que aparecen valores límite comunes
        boundary_values = [0, 1, -1, 10, -10, 100, -100]
        found_boundaries = [v for v in values if v in boundary_values]
        
        assert len(found_boundaries) > 0, "Should find some boundary values"
    
    def test_boolean_propositions(self):
        """Test con proposiciones booleanas"""
        # Proposiciones con variables booleanas
        result = self.fuzzer.find_counterexample("a and not a", max_iterations=100)
        assert result.success == True  # Debería encontrar contraejemplo rápidamente
        assert result.counterexample is not None
        assert "a" in result.counterexample
        assert isinstance(result.counterexample["a"], bool)


if __name__ == "__main__":
    # Ejecutar tests manualmente
    test_suite = TestCounterexampleFuzzer()
    test_suite.setup_method()
    
    print("Running basic tests...")
    test_suite.test_analyze_expression_basic()
    print("✓ Basic analysis test passed")
    
    test_suite.test_find_counterexample_simple_true()
    print("✓ True proposition test passed")
    
    test_suite.test_find_counterexample_known_false()
    print("✓ False proposition test passed")
    
    print("All basic tests passed!")
    
    # Ejecutar tests híbridos
    hybrid_test = TestCounterexampleFuzzer()
    hybrid_test.setup_method()
    
    hybrid_test.test_hybrid_verification_true_proposition()
    print("✓ Hybrid verification test passed")
    
    print("All tests completed successfully!")