"""
Analizador de secuencias matemáticas con integración OEIS
- Detección de patrones recursivos
- Clasificación de secuencias conocidas
- Generación de términos siguientes
- Búsqueda en OEIS (simulada sin API externa)
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

from app.mathlab.core.object_models import MathematicalObject


class SequenceAnalyzer:
    """Analizador avanzado de secuencias matemáticas"""
    
    def __init__(self):
        # Cache para análisis computacionalmente pesados
        self._pattern_cache = {}
        self._oeis_cache = {}
        
        # Base de datos local de secuencias famosas
        self._famous_sequences = self._build_famous_sequences_db()
    
    def analyze_sequence(self, sequence: List[int], max_depth: int = 5) -> Dict[str, Any]:
        """
        Análisis completo de una secuencia
        
        Args:
            sequence: Lista de enteros representando la secuencia
            max_depth: Profundidad máxima para análisis recursivo
            
        Returns:
            Dict con análisis completo
        """
        if len(sequence) < 2:
            return {"error": "Sequence too short for analysis", "min_length": 2}
        
        # Identificar en cache
        cache_key = tuple(sequence[:10])  # Primeros 10 términos para cache
        if cache_key in self._pattern_cache:
            return self._pattern_cache[cache_key]
        
        analysis = {}
        
        # Análisis básico
        analysis.update(self._basic_analysis(sequence))
        
        # Detección de patrones
        analysis.update(self._detect_patterns(sequence, max_depth))
        
        # Clasificación de tipos de secuencia
        analysis.update(self._classify_sequence_type(sequence))
        
        # Predicción de términos siguientes
        analysis.update(self._predict_next_terms(sequence))
        
        # Búsqueda en base de datos OEIS local
        analysis.update(self._search_oeis_local(sequence))
        
        # Propiedades avanzadas
        analysis.update(self._advanced_properties(sequence))
        
        # Cache result
        self._pattern_cache[cache_key] = analysis
        
        return analysis
    
    def _basic_analysis(self, sequence: List[int]) -> Dict[str, Any]:
        """Análisis estadístico básico"""
        return {
            "length": len(sequence),
            "min_value": min(sequence),
            "max_value": max(sequence),
            "sum": sum(sequence),
            "mean": sum(sequence) / len(sequence),
            "is_increasing": all(sequence[i] <= sequence[i+1] for i in range(len(sequence)-1)),
            "is_decreasing": all(sequence[i] >= sequence[i+1] for i in range(len(sequence)-1)),
            "is_strictly_increasing": all(sequence[i] < sequence[i+1] for i in range(len(sequence)-1)),
            "is_strictly_decreasing": all(sequence[i] > sequence[i+1] for i in range(len(sequence)-1)),
            "has_negatives": any(x < 0 for x in sequence),
            "has_zeros": 0 in sequence,
            "unique_values": len(set(sequence)),
            "is_constant": len(set(sequence)) == 1,
        }
    
    def _detect_patterns(self, sequence: List[int], max_depth: int) -> Dict[str, Any]:
        """Detección de patrones recursivos y aritméticos/geométricos"""
        patterns = {}
        
        # Diferencias sucesivas
        differences = self._compute_differences(sequence, max_depth)
        patterns["differences"] = differences
        
        # Análisis aritmético
        if differences and len(differences[0]) > 0:
            first_diffs = differences[0]
            if len(set(first_diffs)) == 1:  # Diferencias constantes
                patterns["arithmetic_progression"] = {
                    "is_arithmetic": True,
                    "common_difference": first_diffs[0],
                    "first_term": sequence[0]
                }
            else:
                patterns["arithmetic_progression"] = {"is_arithmetic": False}
        
        # Análisis geométrico
        patterns.update(self._detect_geometric_progression(sequence))
        
        # Patrones de recurrencia lineal
        patterns.update(self._detect_linear_recurrence(sequence))
        
        # Periodicidad
        patterns.update(self._detect_periodicity(sequence))
        
        # Patrones polinomiales
        patterns.update(self._detect_polynomial_pattern(sequence, differences))
        
        return patterns
    
    def _compute_differences(self, sequence: List[int], max_depth: int) -> List[List[int]]:
        """Computa diferencias sucesivas hasta max_depth o hasta constante"""
        differences = []
        current = sequence[:]
        
        for _ in range(max_depth):
            if len(current) < 2:
                break
            
            diff = [current[i+1] - current[i] for i in range(len(current)-1)]
            differences.append(diff)
            
            # Si las diferencias son constantes, no necesitamos más profundidad
            if len(set(diff)) <= 1:
                break
            
            current = diff
        
        return differences
    
    def _detect_geometric_progression(self, sequence: List[int]) -> Dict[str, Any]:
        """Detecta si es progresión geométrica"""
        if len(sequence) < 2:
            return {"geometric_progression": {"is_geometric": False}}
        
        # Evitar división por cero
        if 0 in sequence[:-1]:  # Cero no puede estar en posiciones intermedias
            return {"geometric_progression": {"is_geometric": False, "reason": "contains_zero"}}
        
        try:
            ratios = [sequence[i+1] / sequence[i] for i in range(len(sequence)-1) if sequence[i] != 0]
            
            if not ratios:
                return {"geometric_progression": {"is_geometric": False, "reason": "division_by_zero"}}
            
            # Verificar si todas las razones son iguales (con tolerancia para decimales)
            first_ratio = ratios[0]
            is_geometric = all(abs(ratio - first_ratio) < 1e-10 for ratio in ratios)
            
            if is_geometric:
                return {
                    "geometric_progression": {
                        "is_geometric": True,
                        "common_ratio": first_ratio,
                        "first_term": sequence[0]
                    }
                }
            else:
                return {
                    "geometric_progression": {
                        "is_geometric": False,
                        "ratios": ratios[:5],  # Primeras 5 razones para análisis
                        "ratio_variance": max(ratios) - min(ratios) if ratios else 0
                    }
                }
        
        except ZeroDivisionError:
            return {"geometric_progression": {"is_geometric": False, "reason": "zero_division"}}
    
    def _detect_linear_recurrence(self, sequence: List[int]) -> Dict[str, Any]:
        """Detecta patrones de recurrencia lineal (Fibonacci, Tribonacci, etc.)"""
        if len(sequence) < 3:
            return {"linear_recurrence": {"detected": False, "reason": "too_short"}}
        
        recurrence_patterns = {}
        
        # Fibonacci-like: a_n = a_{n-1} + a_{n-2}
        if len(sequence) >= 3:
            fibonacci_like = all(
                sequence[i] == sequence[i-1] + sequence[i-2] 
                for i in range(2, len(sequence))
            )
            if fibonacci_like:
                recurrence_patterns["fibonacci_like"] = True
                recurrence_patterns["recurrence_relation"] = "a_n = a_{n-1} + a_{n-2}"
        
        # Tribonacci-like: a_n = a_{n-1} + a_{n-2} + a_{n-3}
        if len(sequence) >= 4:
            tribonacci_like = all(
                sequence[i] == sequence[i-1] + sequence[i-2] + sequence[i-3]
                for i in range(3, len(sequence))
            )
            if tribonacci_like:
                recurrence_patterns["tribonacci_like"] = True
                recurrence_patterns["recurrence_relation"] = "a_n = a_{n-1} + a_{n-2} + a_{n-3}"
        
        # Lucas-like: a_n = 2*a_{n-1} - a_{n-2}
        if len(sequence) >= 3:
            lucas_like = all(
                sequence[i] == 2*sequence[i-1] - sequence[i-2]
                for i in range(2, len(sequence))
            )
            if lucas_like:
                recurrence_patterns["lucas_like"] = True
                recurrence_patterns["recurrence_relation"] = "a_n = 2*a_{n-1} - a_{n-2}"
        
        # General linear recurrence of order 2: a_n = c1*a_{n-1} + c2*a_{n-2}
        if len(sequence) >= 4 and not any(recurrence_patterns.values()):
            coeffs = self._find_linear_recurrence_coeffs(sequence, order=2)
            if coeffs:
                recurrence_patterns["general_order_2"] = True
                recurrence_patterns["coefficients"] = coeffs
                recurrence_patterns["recurrence_relation"] = f"a_n = {coeffs[0]}*a_{{n-1}} + {coeffs[1]}*a_{{n-2}}"
        
        return {"linear_recurrence": recurrence_patterns if recurrence_patterns else {"detected": False}}
    
    def _find_linear_recurrence_coeffs(self, sequence: List[int], order: int) -> Optional[List[float]]:
        """Encuentra coeficientes de recurrencia lineal usando mínimos cuadrados"""
        if len(sequence) <= order:
            return None
        
        # Intentar resolver sistema A*x = b donde x son los coeficientes
        n = len(sequence) - order
        if n < order:
            return None
        
        try:
            # Construir matriz A y vector b
            A = []
            b = []
            
            for i in range(order, len(sequence)):
                row = [sequence[i-j-1] for j in range(order)]
                A.append(row)
                b.append(sequence[i])
            
            # Resolver usando eliminación gaussiana simple
            coeffs = self._solve_linear_system(A, b)
            
            # Verificar que los coeficientes funcionan
            if coeffs and self._verify_recurrence(sequence, coeffs, order):
                return coeffs
            
        except (ValueError, ZeroDivisionError, OverflowError):
            pass
        
        return None
    
    def _solve_linear_system(self, A: List[List[float]], b: List[float]) -> Optional[List[float]]:
        """Resuelve sistema lineal Ax=b usando método simple"""
        n = len(A)
        if n != len(b):
            return None
        
        # Solo para sistemas 2x2 por simplicidad
        if n == 2:
            det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
            if abs(det) < 1e-10:
                return None
            
            x1 = (b[0] * A[1][1] - b[1] * A[0][1]) / det
            x2 = (A[0][0] * b[1] - A[1][0] * b[0]) / det
            
            return [x1, x2]
        
        return None
    
    def _verify_recurrence(self, sequence: List[int], coeffs: List[float], order: int) -> bool:
        """Verifica que los coeficientes generan la secuencia correcta"""
        tolerance = 1e-10
        
        for i in range(order, len(sequence)):
            predicted = sum(coeffs[j] * sequence[i-j-1] for j in range(order))
            if abs(predicted - sequence[i]) > tolerance:
                return False
        
        return True
    
    def _detect_periodicity(self, sequence: List[int]) -> Dict[str, Any]:
        """Detecta periodicidad en la secuencia"""
        if len(sequence) < 2:
            return {"periodicity": {"is_periodic": False}}
        
        max_period = min(len(sequence) // 2, 20)  # Limitar búsqueda
        
        for period in range(1, max_period + 1):
            is_periodic = True
            for i in range(period, len(sequence)):
                if sequence[i] != sequence[i % period]:
                    is_periodic = False
                    break
            
            if is_periodic:
                return {
                    "periodicity": {
                        "is_periodic": True,
                        "period": period,
                        "repeating_pattern": sequence[:period]
                    }
                }
        
        return {"periodicity": {"is_periodic": False}}
    
    def _detect_polynomial_pattern(self, sequence: List[int], differences: List[List[int]]) -> Dict[str, Any]:
        """Detecta si la secuencia sigue un patrón polinomial"""
        polynomial_info = {}
        
        # Una secuencia es polinomial de grado n si las diferencias n-ésimas son constantes
        for degree, diff_level in enumerate(differences):
            if len(set(diff_level)) == 1:  # Diferencias constantes
                polynomial_info["is_polynomial"] = True
                polynomial_info["degree"] = degree + 1
                polynomial_info["constant_difference"] = diff_level[0]
                polynomial_info["difference_level"] = degree
                
                # Para polinomios de grado bajo, intentar encontrar la fórmula
                if degree == 0:  # Grado 1: lineal
                    polynomial_info["formula"] = f"{diff_level[0]}*n + {sequence[0] - diff_level[0]}"
                elif degree == 1:  # Grado 2: cuadrático
                    # a_n = an² + bn + c
                    # Usando diferencias finitas
                    d1 = diff_level[0]
                    a = d1 // 2
                    b = differences[0][0] - a
                    c = sequence[0] - a - b
                    polynomial_info["formula"] = f"{a}*n² + {b}*n + {c}"
                
                break
        else:
            polynomial_info["is_polynomial"] = False
        
        return {"polynomial_pattern": polynomial_info}
    
    def _classify_sequence_type(self, sequence: List[int]) -> Dict[str, Any]:
        """Clasifica el tipo general de secuencia"""
        classification = {}
        
        # Verificar tipos especiales conocidos
        
        # Buscar en base de datos de secuencias famosas
        for name, patterns in self._famous_sequences.items():
            for pattern in patterns:
                if len(sequence) >= len(pattern) and tuple(sequence[:len(pattern)]) == tuple(pattern):
                    classification["famous_sequence"] = name
                    classification["confidence"] = "exact_match"
                    break
            if "famous_sequence" in classification:
                break
        
        # Clasificaciones por propiedades
        if all(x >= 0 for x in sequence):
            classification["non_negative"] = True
        
        if all(isinstance(x, int) and x == int(x) for x in sequence):
            classification["integer_sequence"] = True
        
        # Clasificación por crecimiento
        if len(sequence) >= 2:
            growth_rate = self._analyze_growth_rate(sequence)
            classification.update(growth_rate)
        
        return {"sequence_classification": classification}
    
    def _analyze_growth_rate(self, sequence: List[int]) -> Dict[str, Any]:
        """Analiza la tasa de crecimiento de la secuencia"""
        if len(sequence) < 3:
            return {"growth_analysis": "insufficient_data"}
        
        # Calcular ratios sucesivos para análisis de crecimiento
        ratios = []
        for i in range(1, len(sequence)):
            if sequence[i-1] != 0:
                ratios.append(abs(sequence[i]) / abs(sequence[i-1]))
        
        if not ratios:
            return {"growth_analysis": "contains_zeros"}
        
        avg_ratio = sum(ratios) / len(ratios)
        
        growth_type = ""
        if avg_ratio < 1.1:
            growth_type = "slow"
        elif avg_ratio < 2.0:
            growth_type = "moderate"
        elif avg_ratio < 10.0:
            growth_type = "fast"
        else:
            growth_type = "very_fast"
        
        return {
            "growth_analysis": {
                "average_ratio": avg_ratio,
                "growth_type": growth_type,
                "min_ratio": min(ratios),
                "max_ratio": max(ratios),
                "ratio_stability": max(ratios) - min(ratios)
            }
        }
    
    def _predict_next_terms(self, sequence: List[int], num_terms: int = 3) -> Dict[str, Any]:
        """Predice los siguientes términos basado en patrones detectados"""
        predictions = {}
        
        # Predicción basada en diferencias
        if len(sequence) >= 2:
            diffs = [sequence[i+1] - sequence[i] for i in range(len(sequence)-1)]
            
            if len(set(diffs)) == 1:  # Progresión aritmética
                diff = diffs[0]
                next_terms = [sequence[-1] + (i+1)*diff for i in range(num_terms)]
                predictions["arithmetic_prediction"] = {
                    "next_terms": next_terms,
                    "confidence": "high",
                    "method": "constant_difference"
                }
        
        # Predicción geométrica
        if len(sequence) >= 2 and all(x != 0 for x in sequence[-2:]):
            ratio = sequence[-1] / sequence[-2]
            next_terms = [sequence[-1] * (ratio ** (i+1)) for i in range(num_terms)]
            # Convertir a enteros si la secuencia original era entera
            if all(isinstance(x, int) for x in sequence):
                next_terms = [int(round(x)) for x in next_terms]
            
            predictions["geometric_prediction"] = {
                "next_terms": next_terms,
                "confidence": "medium",
                "method": "constant_ratio"
            }
        
        # Predicción Fibonacci-like
        if len(sequence) >= 2:
            fib_next = [sequence[-1] + sequence[-2]]
            for i in range(1, num_terms):
                fib_next.append(fib_next[-1] + sequence[-1] if i == 1 else fib_next[-1] + fib_next[-2])
            
            predictions["fibonacci_prediction"] = {
                "next_terms": fib_next,
                "confidence": "low",
                "method": "fibonacci_pattern"
            }
        
        return {"predictions": predictions}
    
    def _search_oeis_local(self, sequence: List[int]) -> Dict[str, Any]:
        """Búsqueda local en base de datos OEIS simulada"""
        # Esta sería la búsqueda en OEIS real, aquí simulamos con base local
        seq_key = tuple(sequence[:6])  # Primeros 6 términos para búsqueda
        
        if seq_key in self._oeis_cache:
            return self._oeis_cache[seq_key]
        
        # Buscar coincidencias parciales
        oeis_results = []
        for name, info in self._famous_sequences.items():
            for pattern in info.get("patterns", []):
                if len(pattern) >= 3 and len(sequence) >= 3:
                    # Comparar primeros términos
                    match_length = min(len(pattern), len(sequence))
                    if pattern[:match_length] == sequence[:match_length]:
                        oeis_results.append({
                            "name": name,
                            "oeis_id": info.get("oeis_id", f"A{hash(name) % 100000:06d}"),
                            "match_length": match_length,
                            "description": info.get("description", ""),
                            "formula": info.get("formula", "")
                        })
        
        oeis_info = {
            "local_search_results": oeis_results,
            "total_matches": len(oeis_results),
            "best_match": oeis_results[0] if oeis_results else None
        }
        
        self._oeis_cache[seq_key] = {"oeis_search": oeis_info}
        return {"oeis_search": oeis_info}
    
    def _advanced_properties(self, sequence: List[int]) -> Dict[str, Any]:
        """Propiedades avanzadas de la secuencia"""
        properties = {}
        
        # Análisis de primalidad (para secuencias de números primos)
        if all(x > 0 for x in sequence):
            prime_analysis = self._analyze_primality(sequence)
            properties.update(prime_analysis)
        
        # Análisis de divisibilidad
        divisibility_analysis = self._analyze_divisibility(sequence)
        properties.update(divisibility_analysis)
        
        # Propiedades modulares
        modular_analysis = self._analyze_modular_properties(sequence)
        properties.update(modular_analysis)
        
        return {"advanced_properties": properties}
    
    def _analyze_primality(self, sequence: List[int]) -> Dict[str, Any]:
        """Analiza propiedades relacionadas con números primos"""
        if not all(x > 0 for x in sequence):
            return {}
        
        def is_prime(n):
            if n < 2:
                return False
            if n == 2:
                return True
            if n % 2 == 0:
                return False
            for i in range(3, int(n**0.5) + 1, 2):
                if n % i == 0:
                    return False
            return True
        
        primes_in_seq = [x for x in sequence if is_prime(x)]
        
        return {
            "prime_analysis": {
                "contains_primes": len(primes_in_seq) > 0,
                "all_primes": len(primes_in_seq) == len(sequence),
                "prime_count": len(primes_in_seq),
                "prime_ratio": len(primes_in_seq) / len(sequence),
                "primes_found": primes_in_seq[:10]  # Primeros 10 primos
            }
        }
    
    def _analyze_divisibility(self, sequence: List[int]) -> Dict[str, Any]:
        """Analiza patrones de divisibilidad"""
        divisibility = {}
        
        # Verificar divisibilidad por números pequeños
        for divisor in [2, 3, 5, 7, 11]:
            divisible_count = len([x for x in sequence if x != 0 and x % divisor == 0])
            divisibility[f"divisible_by_{divisor}"] = {
                "count": divisible_count,
                "ratio": divisible_count / len(sequence),
                "all_divisible": divisible_count == len(sequence)
            }
        
        return {"divisibility_analysis": divisibility}
    
    def _analyze_modular_properties(self, sequence: List[int]) -> Dict[str, Any]:
        """Analiza propiedades modulares de la secuencia"""
        modular_properties = {}
        
        # Residuos módulo números pequeños
        for modulus in [2, 3, 4, 5, 7, 10]:
            residues = [x % modulus for x in sequence]
            unique_residues = list(set(residues))
            
            modular_properties[f"mod_{modulus}"] = {
                "residues": residues,
                "unique_residues": sorted(unique_residues),
                "residue_count": len(unique_residues),
                "all_residues_present": len(unique_residues) == modulus
            }
        
        return {"modular_analysis": modular_properties}
    
    def _build_famous_sequences_db(self) -> Dict[str, Dict]:
        """Construye base de datos local de secuencias famosas"""
        return {
            "fibonacci": {
                "patterns": [[1, 1, 2, 3, 5, 8, 13, 21], [0, 1, 1, 2, 3, 5, 8, 13]],
                "oeis_id": "A000045",
                "description": "Fibonacci numbers: F(n) = F(n-1) + F(n-2)",
                "formula": "F(n) = F(n-1) + F(n-2) with F(0)=0, F(1)=1"
            },
            "lucas": {
                "patterns": [[2, 1, 3, 4, 7, 11, 18, 29]],
                "oeis_id": "A000032", 
                "description": "Lucas numbers: L(n) = L(n-1) + L(n-2) with L(0)=2, L(1)=1",
                "formula": "L(n) = L(n-1) + L(n-2)"
            },
            "triangular": {
                "patterns": [[1, 3, 6, 10, 15, 21, 28, 36], [0, 1, 3, 6, 10, 15, 21]],
                "oeis_id": "A000217",
                "description": "Triangular numbers: n(n+1)/2",
                "formula": "T(n) = n(n+1)/2"
            },
            "squares": {
                "patterns": [[1, 4, 9, 16, 25, 36, 49, 64], [0, 1, 4, 9, 16, 25, 36]],
                "oeis_id": "A000290",
                "description": "Perfect squares: n^2",
                "formula": "a(n) = n^2"
            },
            "cubes": {
                "patterns": [[1, 8, 27, 64, 125, 216, 343], [0, 1, 8, 27, 64, 125]],
                "oeis_id": "A000578",
                "description": "Perfect cubes: n^3",
                "formula": "a(n) = n^3"
            },
            "primes": {
                "patterns": [[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]],
                "oeis_id": "A000040",
                "description": "Prime numbers",
                "formula": "n-th prime number"
            },
            "factorials": {
                "patterns": [[1, 1, 2, 6, 24, 120, 720], [1, 2, 6, 24, 120, 720]],
                "oeis_id": "A000142",
                "description": "Factorial numbers: n!",
                "formula": "a(n) = n!"
            },
            "catalan": {
                "patterns": [[1, 1, 2, 5, 14, 42, 132, 429]],
                "oeis_id": "A000108",
                "description": "Catalan numbers",
                "formula": "C(n) = (2n)!/(n+1)!n!"
            },
            "tribonacci": {
                "patterns": [[1, 1, 2, 4, 7, 13, 24, 44]],
                "oeis_id": "A000073",
                "description": "Tribonacci numbers: a(n) = a(n-1) + a(n-2) + a(n-3)",
                "formula": "T(n) = T(n-1) + T(n-2) + T(n-3)"
            },
            "powers_of_2": {
                "patterns": [[1, 2, 4, 8, 16, 32, 64, 128], [2, 4, 8, 16, 32, 64]],
                "oeis_id": "A000079",
                "description": "Powers of 2: 2^n",
                "formula": "a(n) = 2^n"
            }
        }
    
    def generate_sequence_object(self, sequence: List[int], metadata: Optional[Dict] = None) -> MathematicalObject:
        """
        Genera un MathematicalObject para la secuencia analizada
        
        Args:
            sequence: La secuencia de números
            metadata: Metadatos adicionales opcionales
            
        Returns:
            MathematicalObject de tipo 'sequence'
        """
        analysis = self.analyze_sequence(sequence)
        
        payload = {
            "sequence": sequence,
            "length": len(sequence),
            "analysis": analysis
        }
        
        if metadata:
            payload.update(metadata)
        
        from app.mathlab.core.hashing import semantic_hash
        import uuid
        
        # Generar ID único
        object_id = str(uuid.uuid4())
        
        # Computar hash semántico del payload
        hash_value = semantic_hash(payload, "sequence", "v1")
        
        return MathematicalObject(
            id=object_id,
            type="sequence",
            semantic_hash=hash_value,
            spec_version="v1",
            payload_json=payload
        )


# Instancia global del analizador
SEQUENCE_ANALYZER = SequenceAnalyzer()
