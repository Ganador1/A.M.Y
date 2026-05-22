"""
Intelligent Counterexample Fuzzer for Mathematical Propositions

Este servicio proporciona búsqueda avanzada de contraejemplos usando:
1. Fuzzing aleatorio con distribuciones adaptativas
2. Búsqueda en límites (boundary value analysis)
3. Integración con Z3 para búsqueda simbólica
4. Generación inteligente de valores basada en tipos
"""

import random
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
import numpy as np
from pydantic import BaseModel, Field
from app.exceptions.domain.biology import BiologyError
from app.types.counterexample_fuzzer_types import (
    AnalyzeExpressionResult,
)

# Importar servicios existentes
try:
    from .normalizer import ExpressionNormalizer, ExprNode, Variable, Constant, BinaryOp, Comparison
    from .theorem_proving.z3_smt_service import Z3SMTService
except ImportError:
    # Fallback para imports relativos
    from app.services.normalizer import ExpressionNormalizer, ExprNode, Variable, Constant, BinaryOp, Comparison
    from app.services.theorem_proving.z3_smt_service import Z3SMTService

logger = logging.getLogger(__name__)


class FuzzingStrategy(BaseModel):
    """Estrategia de fuzzing para diferentes tipos de variables"""
    name: str = Field(..., description="Nombre de la estrategia")
    weight: float = Field(1.0, description="Peso relativo para sampling")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class VariableDistribution(BaseModel):
    """Distribución para generar valores de una variable"""
    variable_name: str
    variable_type: str  # "Real", "Int", "Bool"
    strategies: List[FuzzingStrategy] = Field(default_factory=list)
    current_strategy_index: int = 0


class FuzzingResult(BaseModel):
    """Resultado de una ejecución de fuzzing"""
    success: bool = Field(..., description="Si se encontró contraejemplo")
    counterexample: Optional[Dict[str, Any]] = Field(None, description="Valores que refutan la proposición")
    iterations: int = Field(0, description="Número de iteraciones ejecutadas")
    strategy_used: str = Field("unknown", description="Estrategia que encontró el contraejemplo")
    variable_values: Dict[str, Any] = Field(default_factory=dict)


class IntelligentFuzzer:
    """Fuzzer inteligente para búsqueda de contraejemplos matemáticos"""
    
    def __init__(self):
        self.normalizer = ExpressionNormalizer()
        self.z3_service = Z3SMTService()
        self.strategies = self._initialize_strategies()
        
    def _initialize_strategies(self) -> Dict[str, FuzzingStrategy]:
        """Inicializar estrategias de fuzzing predefinidas"""
        return {
            "random_uniform": FuzzingStrategy(
                name="random_uniform",
                weight=0.3,
                parameters={"min": -100, "max": 100}
            ),
            "boundary_values": FuzzingStrategy(
                name="boundary_values", 
                weight=0.4,
                parameters={"values": [0, 1, -1, 10, -10, 100, -100]}
            ),
            "small_numbers": FuzzingStrategy(
                name="small_numbers",
                weight=0.2,
                parameters={"min": -10, "max": 10}
            ),
            "large_numbers": FuzzingStrategy(
                name="large_numbers", 
                weight=0.1,
                parameters={"min": -1000, "max": 1000}
            )
        }
    
    def analyze_expression(self, proposition: str) -> AnalyzeExpressionResult:
        """Analizar una expresión matemática para extraer variables y tipos"""
        try:
            # Parsear la expresión usando el normalizador existente
            ast = self.normalizer.from_python(proposition)
            
            # Extraer información de variables
            variables_info = self._extract_variables_info(ast)
            
            return {
                "success": True,
                "ast": ast,
                "variables": variables_info,
                "variable_names": list(variables_info.keys()),
                "expression_complexity": self._calculate_complexity(ast)
            }
            
        except BiologyError as e:
            logger.error(f"Error analyzing expression: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_variables_info(self, ast: ExprNode) -> Dict[str, Dict[str, Any]]:
        """Extraer información de variables del AST"""
        variables_info = {}
        
        def traverse(node):
            if isinstance(node, Variable):
                variables_info[node.name] = {
                    "type": node.sort,
                    "occurrences": variables_info.get(node.name, {}).get("occurrences", 0) + 1
                }
            elif hasattr(node, '__dict__'):
                for attr_name, attr_value in node.__dict__.items():
                    if isinstance(attr_value, ExprNode):
                        traverse(attr_value)
                    elif isinstance(attr_value, list):
                        for item in attr_value:
                            if isinstance(item, ExprNode):
                                traverse(item)
        
        traverse(ast)
        return variables_info
    
    def _calculate_complexity(self, ast: ExprNode) -> int:
        """Calcular complejidad aproximada del AST"""
        complexity = 0
        
        def count_nodes(node):
            nonlocal complexity
            complexity += 1
            if hasattr(node, '__dict__'):
                for attr_value in node.__dict__.values():
                    if isinstance(attr_value, ExprNode):
                        count_nodes(attr_value)
                    elif isinstance(attr_value, list):
                        for item in attr_value:
                            if isinstance(item, ExprNode):
                                count_nodes(item)
        
        count_nodes(ast)
        return complexity
    
    def generate_values(self, variable_info: Dict[str, Any], strategy_name: str) -> Any:
        """Generar valores según la estrategia y tipo de variable"""
        strategy = self.strategies.get(strategy_name)
        if not strategy:
            strategy = self.strategies["random_uniform"]
        
        var_type = variable_info.get("type", "Real")
        
        if var_type == "Bool":
            return random.choice([True, False])
            
        elif var_type == "Int":
            if strategy.name == "boundary_values":
                return random.choice(strategy.parameters.get("values", [0, 1, -1]))
            else:
                min_val = strategy.parameters.get("min", -100)
                max_val = strategy.parameters.get("max", 100)
                return random.randint(min_val, max_val)
                
        elif var_type == "Real":
            if strategy.name == "boundary_values":
                return random.choice(strategy.parameters.get("values", [0.0, 1.0, -1.0]))
            else:
                min_val = strategy.parameters.get("min", -100.0)
                max_val = strategy.parameters.get("max", 100.0)
                return random.uniform(min_val, max_val)
    
    def evaluate_expression(self, ast: ExprNode, variable_values: Dict[str, Any]) -> bool:
        """Evaluar la expresión AST con los valores dados"""
        try:
            from sympy import sympify
            # Convert AST-derived Python expression back to a SymPy expression for safe evaluation
            expr = sympify(python_expr)
            # Evaluate with given variable values
            result = expr.evalf(subs=variable_values)
            
            return bool(result)
            
        except Exception as e:
            logger.warning(f"Error evaluating expression safely: {e}")
            return False
    
    def _ast_to_python(self, ast: ExprNode, variable_values: Dict[str, Any]) -> str:
        """Convertir AST a expresión Python evaluable"""
        if isinstance(ast, Variable):
            return ast.name
        elif isinstance(ast, Constant):
            return str(ast.value)
        elif isinstance(ast, BinaryOp):
            left = self._ast_to_python(ast.left, variable_values)
            right = self._ast_to_python(ast.right, variable_values)
            
            op_map = {
                "+": "+", "-": "-", "*": "*", "/": "/", "**": "**",
                "and": "and", "or": "or", "=>": ""  # Implementar lógica adecuada
            }
            
            if ast.op in op_map:
                return f"({left} {op_map[ast.op]} {right})"
            else:
                return f"({left} {ast.op} {right})"
                
        elif isinstance(ast, Comparison):
            left = self._ast_to_python(ast.left, variable_values)
            right = self._ast_to_python(ast.right, variable_values)
            return f"({left} {ast.op} {right})"
            
        # Implementar otros tipos de nodos según sea necesario
        return "False"  # Fallback seguro
    
    def find_counterexample(
        self, 
        proposition: str, 
        max_iterations: int = 1000,
        timeout: int = 30
    ) -> FuzzingResult:
        """
        Buscar contraejemplo para una proposición matemática
        
        Args:
            proposition: Expresión matemática a refutar
            max_iterations: Máximo número de intentos de fuzzing
            timeout: Tiempo máximo en segundos
            
        Returns:
            FuzzingResult con el resultado de la búsqueda
        """
        logger.info(f"Starting counterexample search for: {proposition}")
        
        # Paso 1: Analizar la expresión
        analysis = self.analyze_expression(proposition)
        if not analysis["success"]:
            return FuzzingResult(success=False, iterations=0)
        
        variables_info = analysis["variables"]
        variable_names = list(variables_info.keys())
        
        if not variable_names:
            logger.info("No variables found in expression")
            return FuzzingResult(success=False, iterations=0)
        
        # Paso 2: Intentar estrategias en orden de efectividad
        strategies_to_try = ["boundary_values", "random_uniform", "small_numbers", "large_numbers"]
        
        for strategy_name in strategies_to_try:
            logger.info(f"Trying strategy: {strategy_name}")
            
            for iteration in range(max_iterations // len(strategies_to_try)):
                # Generar valores para todas las variables
                values = {}
                for var_name in variable_names:
                    values[var_name] = self.generate_values(variables_info[var_name], strategy_name)
                
                # Evaluar la expresión
                is_true = self.evaluate_expression(analysis["ast"], values)
                
                if not is_true:
                    # ¡Contraejemplo encontrado!
                    logger.info(f"Counterexample found with strategy {strategy_name}: {values}")
                    return FuzzingResult(
                        success=True,
                        counterexample=values,
                        iterations=iteration + 1,
                        strategy_used=strategy_name,
                        variable_values=values
                    )
        
        # Paso 3: Si el fuzzing falla, intentar con Z3
        try:
            z3_result = self.z3_service.find_counterexamples(proposition, {"x": "Real"})
            if z3_result:
                logger.info(f"Z3 found counterexample: {z3_result[0]}")
                return FuzzingResult(
                    success=True,
                    counterexample=z3_result[0],
                    iterations=max_iterations,
                    strategy_used="z3_symbolic",
                    variable_values=z3_result[0]
                )
        except BiologyError as e:
            logger.warning(f"Z3 counterexample search failed: {e}")
        
        return FuzzingResult(success=False, iterations=max_iterations)


# Singleton para uso global
fuzzer_singleton = IntelligentFuzzer()