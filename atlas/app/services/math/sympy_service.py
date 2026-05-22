"""
SymPy Service - Symbolic Mathematics
Proporciona álgebra simbólica, cálculo, y resolución de ecuaciones
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SymPyService:
    """Servicio para operaciones de matemática simbólica usando SymPy"""
    
    def __init__(self):
        self.service_name = "SymPyService"
        logger.info(f"✅ {self.service_name} initialized")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes de operaciones simbólicas
        
        Operaciones soportadas:
        - 'solve': Resolver ecuaciones
        - 'diff': Calcular derivadas
        - 'integrate': Calcular integrales
        - 'simplify': Simplificar expresiones
        - 'expand': Expandir expresiones
        - 'factor': Factorizar expresiones
        - 'limit': Calcular límites
        """
        operation = request_data.get('operation')
        
        if operation == 'solve':
            return await self.solve_equation(request_data)
        elif operation == 'diff':
            return await self.differentiate(request_data)
        elif operation == 'integrate':
            return await self.integrate(request_data)
        elif operation == 'simplify':
            return await self.simplify(request_data)
        elif operation == 'expand':
            return await self.expand(request_data)
        elif operation == 'factor':
            return await self.factor(request_data)
        elif operation == 'limit':
            return await self.calculate_limit(request_data)
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "supported_operations": ['solve', 'diff', 'integrate', 'simplify', 'expand', 'factor', 'limit']
            }
    
    async def solve_equation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolver ecuaciones simbólicas"""
        try:
            import sympy as sp
            
            equation_str = request_data.get('equation', '')
            variable_str = request_data.get('variable', 'x')
            
            # Parsear ecuación
            x = sp.Symbol(variable_str)
            equation = sp.sympify(equation_str)
            
            # Resolver
            solutions = sp.solve(equation, x)
            
            return {
                "success": True,
                "operation": "solve",
                "equation": str(equation),
                "variable": variable_str,
                "solutions": [str(sol) for sol in solutions],
                "num_solutions": len(solutions)
            }
            
        except Exception as e:
            logger.error(f"Error solving equation: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "solve"
            }
    
    async def differentiate(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular derivadas"""
        try:
            import sympy as sp
            
            expression_str = request_data.get('expression', '')
            variable_str = request_data.get('variable', 'x')
            order = request_data.get('order', 1)
            
            x = sp.Symbol(variable_str)
            expr = sp.sympify(expression_str)
            
            # Derivada
            derivative = sp.diff(expr, x, order)
            
            return {
                "success": True,
                "operation": "differentiate",
                "expression": str(expr),
                "variable": variable_str,
                "order": order,
                "derivative": str(derivative),
                "simplified": str(sp.simplify(derivative))
            }
            
        except Exception as e:
            logger.error(f"Error differentiating: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "differentiate"
            }
    
    async def integrate(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular integrales"""
        try:
            import sympy as sp
            
            expression_str = request_data.get('expression', '')
            variable_str = request_data.get('variable', 'x')
            definite = request_data.get('definite', False)
            
            x = sp.Symbol(variable_str)
            expr = sp.sympify(expression_str)
            
            if definite:
                lower = request_data.get('lower', 0)
                upper = request_data.get('upper', 1)
                integral = sp.integrate(expr, (x, lower, upper))
                
                return {
                    "success": True,
                    "operation": "integrate",
                    "expression": str(expr),
                    "variable": variable_str,
                    "definite": True,
                    "limits": [lower, upper],
                    "result": str(integral),
                    "numerical_value": float(integral.evalf()) if integral.is_number else None
                }
            else:
                integral = sp.integrate(expr, x)
                
                return {
                    "success": True,
                    "operation": "integrate",
                    "expression": str(expr),
                    "variable": variable_str,
                    "definite": False,
                    "result": str(integral)
                }
            
        except Exception as e:
            logger.error(f"Error integrating: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "integrate"
            }
    
    async def simplify(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simplificar expresiones"""
        try:
            import sympy as sp
            
            expression_str = request_data.get('expression', '')
            expr = sp.sympify(expression_str)
            
            simplified = sp.simplify(expr)
            
            return {
                "success": True,
                "operation": "simplify",
                "original": str(expr),
                "simplified": str(simplified),
                "reduction_achieved": len(str(expr)) - len(str(simplified))
            }
            
        except Exception as e:
            logger.error(f"Error simplifying: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "simplify"
            }
    
    async def expand(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Expandir expresiones"""
        try:
            import sympy as sp
            
            expression_str = request_data.get('expression', '')
            expr = sp.sympify(expression_str)
            
            expanded = sp.expand(expr)
            
            return {
                "success": True,
                "operation": "expand",
                "original": str(expr),
                "expanded": str(expanded)
            }
            
        except Exception as e:
            logger.error(f"Error expanding: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "expand"
            }
    
    async def factor(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Factorizar expresiones"""
        try:
            import sympy as sp
            
            expression_str = request_data.get('expression', '')
            expr = sp.sympify(expression_str)
            
            factored = sp.factor(expr)
            
            return {
                "success": True,
                "operation": "factor",
                "original": str(expr),
                "factored": str(factored)
            }
            
        except Exception as e:
            logger.error(f"Error factoring: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "factor"
            }
    
    async def calculate_limit(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular límites"""
        try:
            import sympy as sp
            
            expression_str = request_data.get('expression', '')
            variable_str = request_data.get('variable', 'x')
            point = request_data.get('point', 0)
            direction = request_data.get('direction', '+')  # '+', '-', o None para bilateral
            
            x = sp.Symbol(variable_str)
            expr = sp.sympify(expression_str)
            
            if direction == '+':
                limit_result = sp.limit(expr, x, point, '+')
            elif direction == '-':
                limit_result = sp.limit(expr, x, point, '-')
            else:
                limit_result = sp.limit(expr, x, point)
            
            return {
                "success": True,
                "operation": "limit",
                "expression": str(expr),
                "variable": variable_str,
                "point": point,
                "direction": direction,
                "result": str(limit_result)
            }
            
        except Exception as e:
            logger.error(f"Error calculating limit: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "limit"
            }
