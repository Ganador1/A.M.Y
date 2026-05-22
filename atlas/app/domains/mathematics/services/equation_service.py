"""
Equation solving service
Servicio para resolver ecuaciones matemáticas usando SymPy
"""

import sympy as sp
from typing import List, Dict, Any
from app.services.base_service import BaseService
from app.domains.mathematics.models import EquationRequest, EquationResponse
from app.exceptions.domain.mathematics import MathematicsError
from app.domains.mathematics.utils import safe_sympify


class EquationService(BaseService):
    """Servicio para resolver ecuaciones matemáticas"""
    
    def __init__(self):
        super().__init__("EquationService")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes de ecuaciones
        """
        try:
            if "equation" in request_data:
                request = EquationRequest(
                    equation=request_data["equation"],
                    variable=request_data.get("variable", "x")
                )
                response = self.solve_equation(request)
                return {
                    "success": True,
                    "solutions": response.solutions,
                    "solution_type": response.solution_type
                }
            else:
                return {"success": False, "error": "Missing 'equation'"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def solve_equation(request: EquationRequest) -> EquationResponse:
        """
        Resuelve una ecuación matemática
        
        Args:
            request: Solicitud con ecuación y variable
            
        Returns:
            Respuesta con las soluciones
        """
        try:
            # Crear símbolo para la variable
            var = sp.Symbol(request.variable)
            
            # Parsear la ecuación
            equation_str = request.equation.replace('=', '-(') + ')'
            equation = safe_sympify(equation_str)
            
            # Resolver la ecuación
            solutions = sp.solve(equation, var)
            
            # Formatear las soluciones
            formatted_solutions = []
            for sol in solutions:
                if sol.is_real:
                    if sol.is_rational:
                        formatted_solutions.append(float(sol))
                    else:
                        formatted_solutions.append(str(sol))
                else:
                    formatted_solutions.append(str(sol))
            
            # Determinar el tipo de solución
            if not solutions:
                solution_type = "No tiene solución"
            elif len(solutions) == 1:
                solution_type = "Solución única"
            else:
                solution_type = f"Múltiples soluciones ({len(solutions)})"
            
            # Generar pasos (simplificado)
            steps = [
                f"Ecuación original: {request.equation}",
                f"Reescribir como: {equation} = 0",
                f"Resolver para {request.variable}",
                f"Solución(es): {formatted_solutions}"
            ]
            
            return EquationResponse(
                success=True,
                equation=request.equation,
                variable=request.variable,
                solutions=formatted_solutions,
                solution_type=solution_type,
                steps=steps
            )
            
        except MathematicsError as e:
            raise ValueError(f"Error al resolver la ecuación: {str(e)}")
    
    @staticmethod
    def solve_system(equations: List[str], variables: List[str]) -> dict:
        """
        Resuelve un sistema de ecuaciones
        
        Args:
            equations: Lista de ecuaciones
            variables: Lista de variables
            
        Returns:
            Diccionario con las soluciones
        """
        try:
            # Crear símbolos para las variables
            symbols = [sp.Symbol(var) for var in variables]
            
            # Parsear las ecuaciones
            parsed_equations = []
            for eq in equations:
                eq_str = eq.replace('=', '-(') + ')'
                parsed_equations.append(safe_sympify(eq_str))
            
            # Resolver el sistema
            solutions = sp.solve(parsed_equations, symbols)
            
            # Formatear las soluciones
            if isinstance(solutions, dict):
                formatted_solutions = {}
                for var, sol in solutions.items():
                    if sol.is_real:
                        formatted_solutions[str(var)] = float(sol)
                    else:
                        formatted_solutions[str(var)] = str(sol)
            else:
                formatted_solutions = [str(sol) for sol in solutions]
            
            return {
                "equations": equations,
                "variables": variables,
                "solutions": formatted_solutions,
                "solution_type": "Sistema resuelto"
            }
            
        except MathematicsError as e:
            raise ValueError(f"Error al resolver el sistema: {str(e)}")
    
    @staticmethod
    def get_equation_examples() -> List[dict]:
        """
        Devuelve ejemplos de ecuaciones
        
        Returns:
            Lista de ejemplos
        """
        return [
            {
                "equation": "x^2 + 2*x - 3 = 0",
                "description": "Ecuación cuadrática",
                "variable": "x"
            },
            {
                "equation": "2*x + 5 = 13",
                "description": "Ecuación lineal",
                "variable": "x"
            },
            {
                "equation": "x^3 - 6*x^2 + 11*x - 6 = 0",
                "description": "Ecuación cúbica",
                "variable": "x"
            },
            {
                "equation": "sin(x) = 0.5",
                "description": "Ecuación trigonométrica",
                "variable": "x"
            },
            {
                "equation": "e^x = 10",
                "description": "Ecuación exponencial",
                "variable": "x"
            },
            {
                "equation": "log(x) = 2",
                "description": "Ecuación logarítmica",
                "variable": "x"
            }
        ]






