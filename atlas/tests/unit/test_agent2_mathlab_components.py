"""
Tests para componentes de Agent 2 - MathLab
- EllipticCurveSampler  
- EllipticInvariants
- SequenceAnalyzer
"""

import pytest
from typing import List, Dict, Any

from app.mathlab.generation.elliptic_curve_sampler import EllipticCurveSampler, ELLIPTIC_SAMPLER
from app.mathlab.invariants.elliptic_invariants import EllipticInvariants, ELLIPTIC_INVARIANTS
from app.mathlab.sequences.sequence_analyzer import SequenceAnalyzer, SEQUENCE_ANALYZER
from app.mathlab.core.object_models import MathematicalObject


class TestEllipticCurveSampler:
    """Tests para el generador de curvas elípticas"""
    
    def test_systematic_sampling(self):
        """Test de generación sistemática de curvas elípticas"""
        sampler = EllipticCurveSampler()
        
        # Generar algunas curvas sistemáticamente
        curves = list(sampler.systematic_sampling(limit=10, max_abs=5))
        
        assert len(curves) <= 10
        assert len(curves) > 0
        
        # Verificar que son objetos MathematicalObject válidos
        for curve in curves:
            assert isinstance(curve, MathematicalObject)
            assert curve.type == "elliptic_curve"
            assert "A" in curve.payload_json
            assert "B" in curve.payload_json
            assert "discriminant" in curve.payload_json
    
    def test_discriminant_computation(self):
        """Test del cálculo del discriminante"""
        sampler = EllipticCurveSampler()
        
        # Caso conocido: y² = x³ - x (A=-1, B=0)
        # Discriminant = -16(4A³ + 27B²) = -16(4(-1) + 0) = -16(-4) = 64
        curve = sampler.generate_curve(A=-1, B=0)
        assert curve.payload_json["discriminant"] == 64
        
        # Caso singular: y² = x³ (A=0, B=0)
        # Discriminant = -16(0 + 0) = 0
        curve = sampler.generate_curve(A=0, B=0)
        assert curve.payload_json["discriminant"] == 0
    
    def test_random_sampling(self):
        """Test de generación aleatoria"""
        sampler = EllipticCurveSampler()
        
        curves = list(sampler.random_sampling(count=5, max_coeff=10))
        
        assert len(curves) == 5
        
        for curve in curves:
            assert isinstance(curve, MathematicalObject)
            A, B = curve.payload_json["A"], curve.payload_json["B"]
            assert abs(A) <= 10
            assert abs(B) <= 10
    
    def test_special_curves(self):
        """Test de curvas especiales conocidas"""
        sampler = EllipticCurveSampler()
        
        special_curves = sampler.get_special_curves()
        
        assert len(special_curves) > 0
        
        # Verificar que la primera curva especial es y² = x³ - x
        first_curve = special_curves[0]
        assert first_curve.payload_json["A"] == -1
        assert first_curve.payload_json["B"] == 0
        assert first_curve.payload_json["name"] == "y² = x³ - x"
    
    def test_conductor_based_sampling(self):
        """Test de sampling basado en conductor"""
        sampler = EllipticCurveSampler()
        
        curves = list(sampler.conductor_based_sampling(max_conductor=100, limit=5))
        
        assert len(curves) <= 5
        
        for curve in curves:
            # Verificar que el conductor estimado esté en rango
            conductor_est = abs(curve.payload_json["discriminant"]) // 16
            assert conductor_est <= 100
    
    def test_global_sampler_instance(self):
        """Test de la instancia global del sampler"""
        # Verificar que la instancia global funciona
        curves = list(ELLIPTIC_SAMPLER.systematic_sampling(limit=3))
        assert len(curves) <= 3
        assert all(isinstance(c, MathematicalObject) for c in curves)


class TestEllipticInvariants:
    """Tests para el cómputo de invariantes de curvas elípticas"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.invariants_computer = EllipticInvariants()
        
        # Crear curva de prueba y² = x³ - x
        self.test_curve = MathematicalObject(
            id="test-curve-1",
            type="elliptic_curve",
            semantic_hash="test-hash",
            spec_version="v1",
            payload_json={"A": -1, "B": 0, "discriminant": 64}
        )
    
    def test_basic_invariants(self):
        """Test de invariantes básicos"""
        invariants = self.invariants_computer.compute(self.test_curve)
        
        assert invariants["A_coefficient"] == -1
        assert invariants["B_coefficient"] == 0
        assert invariants["discriminant"] == 64
        assert invariants["is_singular"] == False
        assert invariants["has_real_component"] == False  # discriminant > 0
        assert invariants["equation_string"] == "y^2 = x^3 + -1*x + 0"
    
    def test_j_invariant_computation(self):
        """Test del cálculo del j-invariant"""
        invariants = self.invariants_computer.compute(self.test_curve)
        
        # Para y² = x³ - x: j = 1728 * (4*(-1)³) / 64 = 1728 * (-4) / 64 = -108
        expected_j = 1728 * 4 * (-1)**3 / 64  # = -108
        
        assert invariants["j_invariant"] == expected_j
        assert invariants["j_invariant_type"] == "general"
        assert invariants["j_invariant_rational"] == True
    
    def test_torsion_structure_analysis(self):
        """Test del análisis de estructura de torsión"""
        invariants = self.invariants_computer.compute(self.test_curve)
        
        # Para y² = x³ - x, se conoce que tiene torsión Z/2Z × Z/2Z
        assert invariants["torsion_order_estimate"] == 4
        assert invariants["torsion_structure_estimate"] == "Z2_Z2"
        assert invariants["mazur_bound"] == 16
        assert 4 in invariants["possible_orders"]
    
    def test_rank_estimation(self):
        """Test de estimación de rank"""
        invariants = self.invariants_computer.compute(self.test_curve)
        
        # Para y² = x³ - x, el rank conocido es 2
        assert invariants["rank_estimate"] == 2
        assert invariants["rank_confidence"] == "known"
        assert invariants["rank_method"] == "literature"
        assert invariants["rank_lower_bound"] == 0
    
    def test_conductor_estimation(self):
        """Test de estimación del conductor"""
        invariants = self.invariants_computer.compute(self.test_curve)
        
        # Para y² = x³ - x, el conductor conocido es 32
        assert invariants["conductor_known"] == 32
        assert invariants["conductor_confidence"] == "literature"
        assert invariants["conductor_complexity"] == "low"
    
    def test_modular_properties(self):
        """Test de propiedades modulares"""
        invariants = self.invariants_computer.compute(self.test_curve)
        
        assert invariants["has_complex_multiplication"] == False
        assert invariants["is_modular"] == True
        assert invariants["modular_level_estimate"] == 32  # Igual al conductor
        assert "modular_degree_estimate" in invariants
    
    def test_singular_curve(self):
        """Test con curva singular"""
        singular_curve = MathematicalObject(
            id="singular-test",
            type="elliptic_curve", 
            semantic_hash="singular-hash",
            spec_version="v1",
            payload_json={"A": 0, "B": 0, "discriminant": 0}
        )
        
        invariants = self.invariants_computer.compute(singular_curve)
        
        assert invariants["is_singular"] == True
        assert invariants["j_invariant"] is None
        assert invariants["j_invariant_type"] == "undefined"
    
    def test_complex_multiplication_cases(self):
        """Test de casos con complex multiplication"""
        # Crear curva con j-invariant = 0 (CM por sqrt(-3))
        # Necesitamos resolver j = 1728 * 4A³ / Δ = 0
        # Esto requiere A = 0, entonces necesitamos discriminant != 0
        
        # Usar curva especial con j = 1728 (CM por i)
        # j = 1728 cuando 4A³ = discriminant
        A = 1
        discriminant = 4 * A**3  # = 4
        B = 1  # Elegir B tal que discriminant sea correcto
        
        cm_curve = MathematicalObject(
            id="cm-test",
            type="elliptic_curve",
            semantic_hash="cm-hash", 
            spec_version="v1",
            payload_json={"A": A, "B": B, "discriminant": discriminant}
        )
        
        invariants = self.invariants_computer.compute(cm_curve)
        
        expected_j = 1728 * 4 * A**3 / discriminant
        assert invariants["j_invariant"] == expected_j
    
    def test_isogeny_properties(self):
        """Test de propiedades de isogenias"""
        isogeny_props = self.invariants_computer.compute_isogeny_properties(self.test_curve)
        
        assert "has_2_isogeny" in isogeny_props
        assert "possible_3_isogeny" in isogeny_props
        assert "possible_5_isogeny" in isogeny_props
        
        # Para y² = x³ - x con torsión 2x2, debe tener 2-isogenias
        assert isogeny_props["has_2_isogeny"] == True
    
    def test_global_invariants_instance(self):
        """Test de la instancia global de invariantes"""
        invariants = ELLIPTIC_INVARIANTS.compute(self.test_curve)
        assert "j_invariant" in invariants
        assert "rank_estimate" in invariants


class TestSequenceAnalyzer:
    """Tests para el analizador de secuencias"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.analyzer = SequenceAnalyzer()
    
    def test_fibonacci_detection(self):
        """Test de detección de secuencia de Fibonacci"""
        fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34]
        
        analysis = self.analyzer.analyze_sequence(fibonacci)
        
        # Verificar análisis básico
        assert analysis["length"] == 9
        assert analysis["is_strictly_increasing"] == False  # Por el 1,1 inicial
        
        # Verificar detección de patrón Fibonacci
        assert analysis["linear_recurrence"]["fibonacci_like"] == True
        assert analysis["linear_recurrence"]["recurrence_relation"] == "a_n = a_{n-1} + a_{n-2}"
        
        # Verificar búsqueda OEIS
        oeis_results = analysis["oeis_search"]["local_search_results"]
        fibonacci_matches = [r for r in oeis_results if "fibonacci" in r["name"].lower()]
        assert len(fibonacci_matches) > 0
    
    def test_arithmetic_progression_detection(self):
        """Test de detección de progresión aritmética"""
        arithmetic = [2, 5, 8, 11, 14, 17, 20]  # d = 3
        
        analysis = self.analyzer.analyze_sequence(arithmetic)
        
        assert analysis["arithmetic_progression"]["is_arithmetic"] == True
        assert analysis["arithmetic_progression"]["common_difference"] == 3
        assert analysis["arithmetic_progression"]["first_term"] == 2
        
        # Verificar predicción
        predictions = analysis["predictions"]["arithmetic_prediction"]
        assert predictions["next_terms"] == [23, 26, 29]  # 20+3, 20+6, 20+9
        assert predictions["confidence"] == "high"
    
    def test_geometric_progression_detection(self):
        """Test de detección de progresión geométrica"""
        geometric = [2, 6, 18, 54, 162]  # r = 3
        
        analysis = self.analyzer.analyze_sequence(geometric)
        
        assert analysis["geometric_progression"]["is_geometric"] == True
        assert analysis["geometric_progression"]["common_ratio"] == 3.0
        assert analysis["geometric_progression"]["first_term"] == 2
        
        # Verificar predicción geométrica
        predictions = analysis["predictions"]["geometric_prediction"]
        assert predictions["next_terms"] == [486, 1458, 4374]  # 162*3, 162*9, 162*27
    
    def test_squares_sequence(self):
        """Test con secuencia de cuadrados perfectos"""
        squares = [1, 4, 9, 16, 25, 36, 49]
        
        analysis = self.analyzer.analyze_sequence(squares)
        
        # Verificar detección polinomial
        polynomial = analysis["polynomial_pattern"]
        assert polynomial["is_polynomial"] == True
        assert polynomial["degree"] == 2  # Cuadrático
        
        # Verificar clasificación como secuencia famosa
        oeis_results = analysis["oeis_search"]["local_search_results"]
        squares_matches = [r for r in oeis_results if "squares" in r["name"].lower()]
        assert len(squares_matches) > 0
    
    def test_prime_sequence_analysis(self):
        """Test con secuencia de números primos"""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        
        analysis = self.analyzer.analyze_sequence(primes)
        
        # Verificar análisis de primalidad
        prime_analysis = analysis["advanced_properties"]["prime_analysis"]
        assert prime_analysis["all_primes"] == True
        assert prime_analysis["prime_count"] == 9
        assert prime_analysis["prime_ratio"] == 1.0
        
        # Verificar que no es aritmética ni geométrica
        assert analysis["arithmetic_progression"]["is_arithmetic"] == False
        assert analysis["geometric_progression"]["is_geometric"] == False
    
    def test_constant_sequence(self):
        """Test con secuencia constante"""
        constant = [7, 7, 7, 7, 7]
        
        analysis = self.analyzer.analyze_sequence(constant)
        
        assert analysis["is_constant"] == True
        assert analysis["unique_values"] == 1
        assert analysis["arithmetic_progression"]["is_arithmetic"] == True
        assert analysis["arithmetic_progression"]["common_difference"] == 0
    
    def test_periodic_sequence(self):
        """Test con secuencia periódica"""
        periodic = [1, 2, 3, 1, 2, 3, 1, 2, 3]
        
        analysis = self.analyzer.analyze_sequence(periodic)
        
        periodicity = analysis["periodicity"]
        assert periodicity["is_periodic"] == True
        assert periodicity["period"] == 3
        assert periodicity["repeating_pattern"] == [1, 2, 3]
    
    def test_tribonacci_detection(self):
        """Test de detección de secuencia de Tribonacci"""
        tribonacci = [1, 1, 2, 4, 7, 13, 24, 44, 81]
        
        analysis = self.analyzer.analyze_sequence(tribonacci)
        
        assert analysis["linear_recurrence"]["tribonacci_like"] == True
        assert analysis["linear_recurrence"]["recurrence_relation"] == "a_n = a_{n-1} + a_{n-2} + a_{n-3}"
        
        # Verificar búsqueda OEIS
        oeis_results = analysis["oeis_search"]["local_search_results"] 
        tribonacci_matches = [r for r in oeis_results if "tribonacci" in r["name"].lower()]
        assert len(tribonacci_matches) > 0
    
    def test_factorial_sequence(self):
        """Test con secuencia de factoriales"""
        factorials = [1, 1, 2, 6, 24, 120, 720]
        
        analysis = self.analyzer.analyze_sequence(factorials)
        
        # Verificar crecimiento muy rápido
        growth = analysis["sequence_classification"]["growth_analysis"]
        assert growth["growth_type"] == "very_fast"
        assert growth["average_ratio"] > 3.0
        
        # Verificar detección en OEIS local
        oeis_results = analysis["oeis_search"]["local_search_results"]
        factorial_matches = [r for r in oeis_results if "factorial" in r["name"].lower()]
        assert len(factorial_matches) > 0
    
    def test_divisibility_analysis(self):
        """Test de análisis de divisibilidad"""
        multiples_of_3 = [3, 6, 9, 12, 15, 18, 21]
        
        analysis = self.analyzer.analyze_sequence(multiples_of_3)
        
        divisibility = analysis["advanced_properties"]["divisibility_analysis"]
        assert divisibility["divisible_by_3"]["all_divisible"] == True
        assert divisibility["divisible_by_3"]["ratio"] == 1.0
        assert divisibility["divisible_by_2"]["ratio"] == 0.0  # Ninguno es par
    
    def test_modular_analysis(self):
        """Test de análisis modular"""
        sequence = [1, 4, 7, 10, 13, 16]  # 1 mod 3, 1 mod 3, ...
        
        analysis = self.analyzer.analyze_sequence(sequence)
        
        modular = analysis["advanced_properties"]["modular_analysis"]
        
        # Todos deben ser ≡ 1 (mod 3)
        assert modular["mod_3"]["unique_residues"] == [1]
        assert modular["mod_3"]["residue_count"] == 1
    
    def test_object_generation(self):
        """Test de generación de MathematicalObject"""
        fibonacci = [1, 1, 2, 3, 5, 8, 13]
        
        math_object = self.analyzer.generate_sequence_object(
            fibonacci,
            metadata={"source": "test", "description": "Fibonacci for testing"}
        )
        
        assert isinstance(math_object, MathematicalObject)
        assert math_object.type == "sequence"
        assert math_object.payload_json["sequence"] == fibonacci
        assert math_object.payload_json["length"] == 7
        assert "analysis" in math_object.payload_json
        
        # Verificar que el análisis está incluido
        analysis = math_object.payload_json["analysis"]
        assert "fibonacci_like" in str(analysis)
    
    def test_short_sequence_handling(self):
        """Test con secuencia muy corta"""
        short = [5]
        
        analysis = self.analyzer.analyze_sequence(short)
        assert "error" in analysis
        assert analysis["min_length"] == 2
    
    def test_global_analyzer_instance(self):
        """Test de la instancia global del analizador"""
        fibonacci = [1, 1, 2, 3, 5, 8]
        
        analysis = SEQUENCE_ANALYZER.analyze_sequence(fibonacci)
        assert analysis["linear_recurrence"]["fibonacci_like"] == True


class TestIntegration:
    """Tests de integración entre componentes"""
    
    def test_elliptic_curve_to_invariants_pipeline(self):
        """Test del pipeline completo: generar curva → computar invariantes"""
        # Generar curva elíptica
        curve = ELLIPTIC_SAMPLER.generate_curve(A=-1, B=0)
        
        # Computar invariantes
        invariants = ELLIPTIC_INVARIANTS.compute(curve)
        
        # Verificar pipeline completo
        assert curve.type == "elliptic_curve"
        assert "j_invariant" in invariants
        assert invariants["A_coefficient"] == -1
        assert invariants["B_coefficient"] == 0
    
    def test_sequence_analysis_pipeline(self):
        """Test del pipeline: secuencia → análisis → objeto matemático"""
        squares = [1, 4, 9, 16, 25]
        
        # Analizar secuencia
        math_object = SEQUENCE_ANALYZER.generate_sequence_object(squares)
        
        # Verificar objeto generado
        assert math_object.type == "sequence"
        assert math_object.payload_json["sequence"] == squares
        
        # Verificar que el análisis detectó propiedades
        analysis = math_object.payload_json["analysis"]
        assert analysis["polynomial_pattern"]["is_polynomial"] == True
    
    def test_mathematical_objects_hashing(self):
        """Test de que los objetos matemáticos tienen hashing correcto"""
        # Crear dos curvas idénticas
        curve1 = ELLIPTIC_SAMPLER.generate_curve(A=1, B=2)
        curve2 = ELLIPTIC_SAMPLER.generate_curve(A=1, B=2)
        
        # Deben tener el mismo hash semántico (mismo contenido)
        assert curve1.semantic_hash == curve2.semantic_hash
        # Pero diferentes IDs
        assert curve1.id != curve2.id
        
        # Crear curva diferente
        curve3 = ELLIPTIC_SAMPLER.generate_curve(A=1, B=3)
        assert curve1.semantic_hash != curve3.semantic_hash


if __name__ == "__main__":
    # Ejecutar tests básicos si se llama directamente
    import sys
    
    print("🧪 Ejecutando tests básicos de Agent 2...")
    
    # Test rápido de cada componente
    try:
        # Test EllipticCurveSampler
        curves = list(ELLIPTIC_SAMPLER.systematic_sampling(limit=3))
        print(f"✅ EllipticCurveSampler: generadas {len(curves)} curvas")
        
        # Test EllipticInvariants
        test_curve = curves[0]
        invariants = ELLIPTIC_INVARIANTS.compute(test_curve)
        print(f"✅ EllipticInvariants: computados {len(invariants)} invariantes")
        
        # Test SequenceAnalyzer
        fibonacci = [1, 1, 2, 3, 5, 8, 13]
        analysis = SEQUENCE_ANALYZER.analyze_sequence(fibonacci)
        print(f"✅ SequenceAnalyzer: análisis completado")
        
        print("🎉 Todos los tests básicos pasaron!")
        
    except Exception as e:
        print(f"❌ Error en tests: {e}")
        sys.exit(1)
