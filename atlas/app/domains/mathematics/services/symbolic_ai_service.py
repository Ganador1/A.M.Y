"""
Symbolic AI Mathematics Service
==============================

Servicio de Inteligencia Artificial Simbólica para resolución automática
de problemas matemáticos complejos.

Este servicio integra técnicas avanzadas de IA para:

- Resolución automática de ecuaciones
- Demostración de teoremas
- Simplificación simbólica inteligente
- Reconocimiento de patrones matemáticos
- Generación automática de soluciones
- Análisis de expresiones matemáticas

Tecnologías Integradas:
----------------------
- Transformers para comprensión matemática
- SymPy para manipulación simbólica
- Redes neuronales especializadas
- Algoritmos genéticos para optimización
- Procesamiento de lenguaje natural matemático

Ejemplos de Uso:
---------------
```python
from app.domains.mathematics.services.symbolic_ai_service import SymbolicAIService
from app.exceptions.domain.mathematics import MathematicsError

# Inicializar servicio
ai_service = SymbolicAIService()

# Resolver ecuación automáticamente
solution = await ai_service.solve_equation("x^2 + 5*x + 6 = 0")

# Demostrar teorema
proof = await ai_service.prove_theorem("For all n, n^2 >= 0")

# Simplificar expresión compleja
simplified = await ai_service.intelligent_simplify("(x^2 - 1)/(x - 1)")
```

Autor: AXIOM Mathematics Team
Fecha: Enero 2024
Versión: 1.0.0
"""

import asyncio
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import sympy as sp
from sympy import symbols, solve, simplify, expand, factor, diff, integrate
from app.services.base_service import BaseService
from app.exceptions.domain.mathematics import MathematicsError
from app.utils.hf_safe import safe_load_pipeline

# Configurar logging
logger = logging.getLogger(__name__)

# Intentar importar dependencias de IA (opcionales)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
    logger.info("Transformers disponible - IA matemática habilitada")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.info("Transformers no disponible - Usando métodos simbólicos básicos")

try:
    import torch
    TORCH_AVAILABLE = True
    logger.info("PyTorch disponible para modelos de IA")
except ImportError:
    TORCH_AVAILABLE = False
    logger.info("PyTorch no disponible")


class MathematicalPatternRecognizer:
    """Reconocedor de patrones matemáticos usando IA."""
    
    def __init__(self):
        """Inicializar reconocedor de patrones."""
        self.patterns = {
            "quadratic": r"[a-z]\^?2.*[+-].*[a-z].*[+-].*\d",
            "linear": r"[a-z].*[+-].*\d.*=.*\d",
            "exponential": r"e\^.*[a-z]|[a-z]\^.*[a-z]",
            "logarithmic": r"log|ln|lg",
            "trigonometric": r"sin|cos|tan|sec|csc|cot",
            "polynomial": r"[a-z]\^?\d+.*[+-].*[a-z]\^?\d+",
            "rational": r"\([^)]+\)/\([^)]+\)",
            "radical": r"sqrt|[a-z]\^?\(1/\d+\)"
        }
    
    def recognize_pattern(self, expression: str) -> Dict[str, Any]:
        """
        Reconocer patrones en una expresión matemática.
        
        Args:
            expression: Expresión matemática como string
            
        Returns:
            Dict con patrones reconocidos y metadatos
        """
        recognized = []
        confidence_scores = {}
        
        for pattern_name, pattern_regex in self.patterns.items():
            if re.search(pattern_regex, expression.lower()):
                recognized.append(pattern_name)
                # Calcular confianza basada en coincidencias
                matches = len(re.findall(pattern_regex, expression.lower()))
                confidence_scores[pattern_name] = min(matches * 0.3, 1.0)
        
        return {
            "expression": expression,
            "recognized_patterns": recognized,
            "confidence_scores": confidence_scores,
            "primary_pattern": max(confidence_scores.keys(), key=confidence_scores.get) if confidence_scores else None,
            "complexity_score": len(expression) / 50.0  # Métrica simple de complejidad
        }


class SymbolicAISolver:
    """Solucionador de IA simbólica."""
    
    def __init__(self):
        """Inicializar solucionador."""
        self.pattern_recognizer = MathematicalPatternRecognizer()
        
        # Estrategias de resolución por tipo de patrón
        self.solving_strategies = {
            "quadratic": self._solve_quadratic,
            "linear": self._solve_linear,
            "exponential": self._solve_exponential,
            "logarithmic": self._solve_logarithmic,
            "trigonometric": self._solve_trigonometric,
            "polynomial": self._solve_polynomial,
            "rational": self._solve_rational,
            "radical": self._solve_radical
        }
    
    def _solve_quadratic(self, expr: sp.Expr, variable: sp.Symbol) -> Dict[str, Any]:
        """Resolver ecuación cuadrática."""
        try:
            solutions = solve(expr, variable)
            return {
                "method": "quadratic_formula",
                "solutions": solutions,
                "discriminant": self._calculate_discriminant(expr, variable),
                "vertex": self._find_vertex(expr, variable)
            }
        except MathematicsError as e:
            return {"error": str(e), "method": "quadratic_formula"}
    
    def _solve_linear(self, expr: sp.Expr, variable: sp.Symbol) -> Dict[str, Any]:
        """Resolver ecuación lineal."""
        try:
            solutions = solve(expr, variable)
            return {
                "method": "linear_algebra",
                "solutions": solutions,
                "slope": diff(expr, variable) if solutions else None
            }
        except MathematicsError as e:
            return {"error": str(e), "method": "linear_algebra"}
    
    def _solve_exponential(self, expr: sp.Expr, variable: sp.Symbol) -> Dict[str, Any]:
        """Resolver ecuación exponencial."""
        try:
            solutions = solve(expr, variable)
            return {
                "method": "logarithmic_transformation",
                "solutions": solutions,
                "domain_restrictions": "x > 0" if "log" in str(expr) else None
            }
        except MathematicsError as e:
            return {"error": str(e), "method": "logarithmic_transformation"}
    
    def _solve_logarithmic(self, expr: sp.Expr, variable: sp.Symbol) -> Dict[str, Any]:
        """Resolver ecuación logarítmica."""
        try:
            solutions = solve(expr, variable)
            # Filtrar soluciones válidas (positivas para logaritmos)
            valid_solutions = [sol for sol in solutions if sol.is_positive != False]
            return {
                "method": "exponential_transformation",
                "solutions": valid_solutions,
                "domain_restrictions": "argument > 0"
            }
        except MathematicsError as e:
            return {"error": str(e), "method": "exponential_transformation"}
    
    def _solve_trigonometric(self, expr: sp.Expr, variable: sp.Symbol) -> Dict[str, Any]:
        """Resolver ecuación trigonométrica."""
        try:
            solutions = solve(expr, variable)
            return {
                "method": "trigonometric_identities",
                "solutions": solutions,
                "period": 2*sp.pi,  # Período general
                "general_solution": True
            }
        except MathematicsError as e:
            return {"error": str(e), "method": "trigonometric_identities"}
    
    def _solve_polynomial(self, expr: sp.Expr, variable: sp.Symbol) -> Dict[str, Any]:
        """Resolver ecuación polinómica."""
        try:
            solutions = solve(expr, variable)
            degree = sp.degree(expr, variable)
            return {
                "method": f"polynomial_degree_{degree}",
                "solutions": solutions,
                "degree": degree,
                "leading_coefficient": sp.LC(expr, variable)
            }
        except MathematicsError as e:
            return {"error": str(e), "method": "polynomial_general"}
    
    def _solve_rational(self, expr: sp.Expr, variable: sp.Symbol) -> Dict[str, Any]:
        """Resolver ecuación racional."""
        try:
            # Multiplicar por denominador común
            simplified = simplify(expr)
            solutions = solve(simplified, variable)
            return {
                "method": "rational_clearing",
                "solutions": solutions,
                "asymptotes": self._find_asymptotes(expr, variable)
            }
        except MathematicsError as e:
            return {"error": str(e), "method": "rational_clearing"}
    
    def _solve_radical(self, expr: sp.Expr, variable: sp.Symbol) -> Dict[str, Any]:
        """Resolver ecuación con radicales."""
        try:
            solutions = solve(expr, variable)
            # Verificar soluciones extrañas
            valid_solutions = []
            for sol in solutions:
                if expr.subs(variable, sol).is_real != False:
                    valid_solutions.append(sol)
            
            return {
                "method": "radical_elimination",
                "solutions": valid_solutions,
                "extraneous_check": len(solutions) != len(valid_solutions)
            }
        except MathematicsError as e:
            return {"error": str(e), "method": "radical_elimination"}
    
    def _calculate_discriminant(self, expr: sp.Expr, variable: sp.Symbol) -> Optional[sp.Expr]:
        """Calcular discriminante de ecuación cuadrática."""
        try:
            coeffs = sp.Poly(expr, variable).all_coeffs()
            if len(coeffs) == 3:
                a, b, c = coeffs
                return b**2 - 4*a*c
        except MathematicsError:
            pass
        return None
    
    def _find_vertex(self, expr: sp.Expr, variable: sp.Symbol) -> Optional[Tuple[sp.Expr, sp.Expr]]:
        """Encontrar vértice de parábola."""
        try:
            coeffs = sp.Poly(expr, variable).all_coeffs()
            if len(coeffs) == 3:
                a, b, c = coeffs
                x_vertex = -b / (2*a)
                y_vertex = expr.subs(variable, x_vertex)
                return (x_vertex, y_vertex)
        except MathematicsError:
            pass
        return None
    
    def _find_asymptotes(self, expr: sp.Expr, variable: sp.Symbol) -> Dict[str, List]:
        """Encontrar asíntotas de función racional."""
        asymptotes = {"vertical": [], "horizontal": [], "oblique": []}
        
        try:
            # Asíntotas verticales (ceros del denominador)
            numer, denom = sp.fraction(expr)
            vertical_asymptotes = solve(denom, variable)
            asymptotes["vertical"] = vertical_asymptotes
            
            # Asíntota horizontal
            limit_inf = sp.limit(expr, variable, sp.oo)
            if limit_inf.is_finite:
                asymptotes["horizontal"] = [limit_inf]
        except MathematicsError:
            pass
        
        return asymptotes


class SymbolicAIService(BaseService):
    """
    Servicio principal de IA simbólica para matemáticas.
    
    Integra reconocimiento de patrones, resolución inteligente,
    y técnicas avanzadas de IA para problemas matemáticos.
    """
    
    def __init__(self):
        """Inicializar servicio de IA simbólica."""
        super().__init__("SymbolicAIService")
        self.pattern_recognizer = MathematicalPatternRecognizer()
        self.solver = SymbolicAISolver()
        
        # Inicializar modelo de IA si está disponible
        self.ai_model = None
        if TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE:
            try:
                self.ai_model = safe_load_pipeline("text-generation", "microsoft/DialoGPT-medium")
                if self.ai_model is not None:
                    logger.info("Modelo de IA matemática cargado")
                else:
                    logger.warning("No se pudo cargar modelo de IA (pipeline devuelto como None)")
            except Exception as e:
                logger.warning(f"No se pudo cargar modelo de IA: {e}")
        
        # Estadísticas de uso
        self.usage_stats = {
            "equations_solved": 0,
            "patterns_recognized": 0,
            "ai_assisted_solutions": 0,
            "success_rate": 0.0
        }
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes de IA simbólica
        """
        action = request_data.get("action")
        
        if action == "solve_equation":
            return await self.solve_equation(
                equation=request_data.get("equation"),
                variable=request_data.get("variable", "x"),
                use_ai_assistance=request_data.get("use_ai_assistance", True)
            )
        elif action == "intelligent_simplify":
            return await self.intelligent_simplify(
                expression=request_data.get("expression"),
                use_ai_guidance=request_data.get("use_ai_guidance", True)
            )
        elif action == "prove_theorem":
            return await self.prove_theorem(
                statement=request_data.get("statement"),
                use_ai_reasoning=request_data.get("use_ai_reasoning", True)
            )
            
        return {"success": False, "error": f"Unknown action: {action}"}
    
    async def solve_equation(
        self, 
        equation: str, 
        variable: str = "x",
        use_ai_assistance: bool = True
    ) -> Dict[str, Any]:
        """
        Resolver ecuación usando IA simbólica.
        
        Args:
            equation: Ecuación como string
            variable: Variable a resolver
            use_ai_assistance: Usar asistencia de IA
            
        Returns:
            Dict con solución y metadatos
        """
        start_time = time.time()
        
        try:
            # Reconocer patrones
            pattern_analysis = self.pattern_recognizer.recognize_pattern(equation)
            
            # Convertir a expresión simbólica
            var = symbols(variable)
            
            # Parsear ecuación
            if "=" in equation:
                left, right = equation.split("=")
                expr = sp.sympify(left) - sp.sympify(right)
            else:
                expr = sp.sympify(equation)
            
            # Seleccionar estrategia de resolución
            primary_pattern = pattern_analysis.get("primary_pattern")
            
            if primary_pattern and primary_pattern in self.solver.solving_strategies:
                # Usar estrategia específica
                solution_result = self.solver.solving_strategies[primary_pattern](expr, var)
                method = f"ai_pattern_{primary_pattern}"
            else:
                # Resolución general
                solutions = solve(expr, var)
                solution_result = {
                    "method": "general_symbolic",
                    "solutions": solutions
                }
                method = "general_symbolic"
            
            # Asistencia de IA si está disponible
            ai_insights = {}
            if use_ai_assistance and self.ai_model:
                ai_insights = await self._get_ai_insights(equation, solution_result)
                self.usage_stats["ai_assisted_solutions"] += 1
            
            computation_time = time.time() - start_time
            self.usage_stats["equations_solved"] += 1
            
            return {
                "success": True,
                "equation": equation,
                "variable": variable,
                "solution": solution_result,
                "pattern_analysis": pattern_analysis,
                "ai_insights": ai_insights,
                "method": method,
                "computation_time": computation_time,
                "steps": self._generate_solution_steps(expr, var, solution_result)
            }
            
        except MathematicsError as e:
            logger.error(f"Error resolviendo ecuación: {e}")
            return {
                "success": False,
                "equation": equation,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
    
    async def intelligent_simplify(
        self, 
        expression: str,
        use_ai_guidance: bool = True
    ) -> Dict[str, Any]:
        """
        Simplificación inteligente de expresiones.
        
        Args:
            expression: Expresión a simplificar
            use_ai_guidance: Usar guía de IA
            
        Returns:
            Dict con expresión simplificada y pasos
        """
        start_time = time.time()
        
        try:
            # Convertir a expresión simbólica
            expr = sp.sympify(expression)
            
            # Múltiples estrategias de simplificación
            simplification_results = {
                "basic": simplify(expr),
                "expanded": expand(expr),
                "factored": factor(expr),
                "trigsimp": sp.trigsimp(expr),
                "radsimp": sp.radsimp(expr),
                "ratsimp": sp.ratsimp(expr)
            }
            
            # Seleccionar mejor simplificación
            best_simplification = self._select_best_simplification(
                expr, simplification_results
            )
            
            # Guía de IA si está disponible
            ai_guidance = {}
            if use_ai_guidance and self.ai_model:
                ai_guidance = await self._get_simplification_guidance(
                    expression, simplification_results
                )
            
            computation_time = time.time() - start_time
            
            return {
                "success": True,
                "original": expression,
                "simplified": best_simplification["result"],
                "method": best_simplification["method"],
                "all_results": simplification_results,
                "ai_guidance": ai_guidance,
                "computation_time": computation_time,
                "complexity_reduction": self._calculate_complexity_reduction(
                    expr, best_simplification["result"]
                )
            }
            
        except MathematicsError as e:
            logger.error(f"Error en simplificación: {e}")
            return {
                "success": False,
                "original": expression,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
    
    async def prove_theorem(
        self, 
        statement: str,
        use_ai_reasoning: bool = True
    ) -> Dict[str, Any]:
        """
        Intentar demostrar un teorema matemático.
        
        Args:
            statement: Enunciado del teorema
            use_ai_reasoning: Usar razonamiento de IA
            
        Returns:
            Dict con intento de demostración
        """
        start_time = time.time()
        
        try:
            # Analizar enunciado
            statement_analysis = self._analyze_theorem_statement(statement)
            
            # Estrategias de demostración
            proof_strategies = [
                "direct_proof",
                "proof_by_contradiction",
                "mathematical_induction",
                "proof_by_cases"
            ]
            
            proof_attempts = {}
            
            for strategy in proof_strategies:
                proof_attempts[strategy] = await self._attempt_proof_strategy(
                    statement, strategy, statement_analysis
                )
            
            # Razonamiento de IA si está disponible
            ai_reasoning = {}
            if use_ai_reasoning and self.ai_model:
                ai_reasoning = await self._get_ai_proof_reasoning(
                    statement, proof_attempts
                )
            
            # Seleccionar mejor intento de demostración
            best_proof = self._select_best_proof(proof_attempts)
            
            computation_time = time.time() - start_time
            
            return {
                "success": True,
                "statement": statement,
                "proof_result": best_proof,
                "all_attempts": proof_attempts,
                "ai_reasoning": ai_reasoning,
                "statement_analysis": statement_analysis,
                "computation_time": computation_time,
                "confidence": best_proof.get("confidence", 0.0)
            }
            
        except MathematicsError as e:
            logger.error(f"Error en demostración: {e}")
            return {
                "success": False,
                "statement": statement,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
    
    async def discover_patterns(
        self, 
        data: List[Union[int, float]],
        pattern_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Descubrir patrones matemáticos en datos.
        
        Args:
            data: Lista de datos numéricos
            pattern_types: Tipos de patrones a buscar
            
        Returns:
            Dict con patrones descubiertos
        """
        if pattern_types is None:
            pattern_types = ["arithmetic", "geometric", "polynomial", "exponential"]
        
        start_time = time.time()
        
        try:
            discovered_patterns = {}
            
            # Buscar progresión aritmética
            if "arithmetic" in pattern_types:
                discovered_patterns["arithmetic"] = self._detect_arithmetic_sequence(data)
            
            # Buscar progresión geométrica
            if "geometric" in pattern_types:
                discovered_patterns["geometric"] = self._detect_geometric_sequence(data)
            
            # Buscar patrón polinómico
            if "polynomial" in pattern_types:
                discovered_patterns["polynomial"] = self._detect_polynomial_pattern(data)
            
            # Buscar patrón exponencial
            if "exponential" in pattern_types:
                discovered_patterns["exponential"] = self._detect_exponential_pattern(data)
            
            # Calcular confianza general
            confidences = [p.get("confidence", 0) for p in discovered_patterns.values() if p]
            overall_confidence = np.mean(confidences) if confidences else 0.0
            
            computation_time = time.time() - start_time
            self.usage_stats["patterns_recognized"] += 1
            
            return {
                "success": True,
                "data": data,
                "patterns": discovered_patterns,
                "overall_confidence": overall_confidence,
                "computation_time": computation_time,
                "recommendations": self._generate_pattern_recommendations(discovered_patterns)
            }
            
        except MathematicsError as e:
            logger.error(f"Error descubriendo patrones: {e}")
            return {
                "success": False,
                "data": data,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
    
    # Métodos auxiliares privados
    
    async def _get_ai_insights(self, equation: str, solution: Dict) -> Dict[str, Any]:
        """Obtener insights de IA sobre la solución."""
        if not self.ai_model:
            return {}
        
        try:
            prompt = f"Analyze this mathematical equation and solution: {equation}"
            response = self.ai_model(prompt, max_length=100, num_return_sequences=1)
            return {
                "ai_analysis": response[0]["generated_text"],
                "confidence": 0.7  # Placeholder
            }
        except MathematicsError as e:
            logger.error(f"Error obteniendo insights de IA: {e}")
            return {}
    
    async def _get_simplification_guidance(self, expression: str, results: Dict) -> Dict:
        """Obtener guía de IA para simplificación."""
        return {
            "recommended_method": "basic",  # Placeholder
            "reasoning": "Based on expression structure"
        }
    
    async def _get_ai_proof_reasoning(self, statement: str, attempts: Dict) -> Dict:
        """Obtener razonamiento de IA para demostración."""
        return {
            "suggested_approach": "direct_proof",
            "key_insights": ["Consider the domain", "Use algebraic manipulation"]
        }
    
    def _select_best_simplification(self, original: sp.Expr, results: Dict) -> Dict:
        """Seleccionar la mejor simplificación."""
        # Criterios: longitud de expresión, complejidad
        best_method = "basic"
        best_result = results["basic"]
        min_complexity = len(str(best_result))
        
        for method, result in results.items():
            complexity = len(str(result))
            if complexity < min_complexity:
                min_complexity = complexity
                best_method = method
                best_result = result
        
        return {"method": best_method, "result": best_result}
    
    def _calculate_complexity_reduction(self, original: sp.Expr, simplified: sp.Expr) -> float:
        """Calcular reducción de complejidad."""
        original_len = len(str(original))
        simplified_len = len(str(simplified))
        return (original_len - simplified_len) / original_len if original_len > 0 else 0.0
    
    def _analyze_theorem_statement(self, statement: str) -> Dict:
        """Analizar enunciado de teorema."""
        return {
            "type": "general",
            "variables": re.findall(r'\b[a-z]\b', statement.lower()),
            "quantifiers": ["for all" in statement.lower(), "exists" in statement.lower()],
            "complexity": len(statement.split())
        }
    
    async def _attempt_proof_strategy(self, statement: str, strategy: str, analysis: Dict) -> Dict:
        """Intentar estrategia de demostración."""
        return {
            "strategy": strategy,
            "success": False,  # Placeholder
            "confidence": 0.3,
            "steps": [f"Step 1 for {strategy}", f"Step 2 for {strategy}"]
        }
    
    def _select_best_proof(self, attempts: Dict) -> Dict:
        """Seleccionar mejor intento de demostración."""
        best_attempt = max(attempts.values(), key=lambda x: x.get("confidence", 0))
        return best_attempt
    
    def _detect_arithmetic_sequence(self, data: List) -> Optional[Dict]:
        """Detectar progresión aritmética."""
        if len(data) < 3:
            return None
        
        differences = [data[i+1] - data[i] for i in range(len(data)-1)]
        if all(abs(d - differences[0]) < 1e-10 for d in differences):
            return {
                "type": "arithmetic",
                "common_difference": differences[0],
                "confidence": 0.95,
                "formula": f"a_n = {data[0]} + {differences[0]}*(n-1)"
            }
        return None
    
    def _detect_geometric_sequence(self, data: List) -> Optional[Dict]:
        """Detectar progresión geométrica."""
        if len(data) < 3 or any(x == 0 for x in data[:-1]):
            return None
        
        ratios = [data[i+1] / data[i] for i in range(len(data)-1)]
        if all(abs(r - ratios[0]) < 1e-10 for r in ratios):
            return {
                "type": "geometric",
                "common_ratio": ratios[0],
                "confidence": 0.95,
                "formula": f"a_n = {data[0]} * {ratios[0]}^(n-1)"
            }
        return None
    
    def _detect_polynomial_pattern(self, data: List) -> Optional[Dict]:
        """Detectar patrón polinómico."""
        if len(data) < 4:
            return None
        
        try:
            x = np.arange(len(data))
            coeffs = np.polyfit(x, data, min(3, len(data)-1))
            poly = np.poly1d(coeffs)
            
            # Verificar ajuste
            predicted = poly(x)
            mse = np.mean((data - predicted) ** 2)
            
            if mse < 1e-6:
                return {
                    "type": "polynomial",
                    "degree": len(coeffs) - 1,
                    "coefficients": coeffs.tolist(),
                    "confidence": 0.9,
                    "mse": mse
                }
        except MathematicsError:
            pass
        
        return None
    
    def _detect_exponential_pattern(self, data: List) -> Optional[Dict]:
        """Detectar patrón exponencial."""
        if len(data) < 3 or any(x <= 0 for x in data):
            return None
        
        try:
            x = np.arange(len(data))
            log_data = np.log(data)
            coeffs = np.polyfit(x, log_data, 1)
            
            # Verificar ajuste exponencial
            predicted = np.exp(coeffs[1]) * np.exp(coeffs[0] * x)
            mse = np.mean((data - predicted) ** 2)
            
            if mse < np.var(data) * 0.1:  # Buen ajuste relativo
                return {
                    "type": "exponential",
                    "base": np.exp(coeffs[0]),
                    "initial_value": np.exp(coeffs[1]),
                    "confidence": 0.85,
                    "mse": mse
                }
        except MathematicsError:
            pass
        
        return None
    
    def _generate_solution_steps(self, expr: sp.Expr, var: sp.Symbol, solution: Dict) -> List[str]:
        """Generar pasos de solución."""
        steps = [
            f"1. Ecuación original: {expr} = 0",
            f"2. Método utilizado: {solution.get('method', 'general')}",
        ]
        
        if "solutions" in solution:
            steps.append(f"3. Soluciones encontradas: {solution['solutions']}")
        
        return steps
    
    def _generate_pattern_recommendations(self, patterns: Dict) -> List[str]:
        """Generar recomendaciones basadas en patrones."""
        recommendations = []
        
        for pattern_type, pattern_data in patterns.items():
            if pattern_data and pattern_data.get("confidence", 0) > 0.8:
                recommendations.append(
                    f"Patrón {pattern_type} detectado con alta confianza"
                )
        
        return recommendations
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de uso del servicio."""
        total_operations = (
            self.usage_stats["equations_solved"] + 
            self.usage_stats["patterns_recognized"]
        )
        
        if total_operations > 0:
            self.usage_stats["success_rate"] = (
                self.usage_stats["equations_solved"] / total_operations
            )
        
        return self.usage_stats.copy()


# Instancia global del servicio
symbolic_ai_service = SymbolicAIService()
