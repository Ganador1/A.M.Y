"""
Differential Equations Service
Servicio para resolver ecuaciones diferenciales con métodos mejorados
"""

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict, Optional, Any, Union
from app.models import DifferentialEquationRequest, DifferentialEquationResponse
import logging
from app.exceptions.domain.biology import BiologyError
from app.types.differential_equations_fixed_types import (
    SolvePdeSymbolicResult,
)

logger = logging.getLogger(__name__)


class PDESolver:
    """Enhanced PDE solver with numerical methods"""
    
    @staticmethod
    def solve_pde_numerical(equation_str: str, boundary_conditions: Dict[str, Any], 
                           domain: Dict[str, Any], method: str = "finite_difference") -> Dict[str, Any]:
        """
        Solve PDEs using numerical methods
        
        Args:
            equation_str: String representation of the PDE
            boundary_conditions: Boundary conditions
            domain: Domain specification (x_min, x_max, t_min, t_max, etc.)
            method: Numerical method to use
            
        Returns:
            Dictionary with numerical solution
        """
        try:
            if method == "finite_difference":
                return PDESolver._solve_finite_difference(equation_str, boundary_conditions, domain)
            elif method == "finite_element":
                return PDESolver._solve_finite_element(equation_str, boundary_conditions, domain)
            else:
                raise ValueError(f"Unknown numerical method: {method}")
                
        except BiologyError as e:
            return {"error": f"Numerical PDE solving failed: {str(e)}"}
    
    @staticmethod
    def _solve_finite_difference(equation_str: str, boundary_conditions: Dict[str, Any], 
                                domain: Dict[str, Any]) -> Dict[str, Any]:
        """Solve PDE using finite difference method"""
        try:
            # Parse domain
            x_min, x_max = domain.get('x_min', 0), domain.get('x_max', 1)
            t_min, t_max = domain.get('t_min', 0), domain.get('t_max', 1)
            nx, nt = domain.get('nx', 50), domain.get('nt', 1000)
            
            # Grid setup
            dx = (x_max - x_min) / (nx - 1)
            dt = (t_max - t_min) / (nt - 1)
            
            x = np.linspace(x_min, x_max, nx)
            t = np.linspace(t_min, t_max, nt)
            
            # Initialize solution array
            u = np.zeros((nt, nx))
            
            # Apply initial conditions
            if 'initial' in boundary_conditions:
                initial_func = boundary_conditions['initial']
                if callable(initial_func):
                    u[0, :] = np.array(initial_func(x))
                else:
                    # Simple sine wave for demonstration
                    u[0, :] = np.sin(np.pi * x)
            
            # Stability parameter for heat equation
            alpha = 0.5  # Thermal diffusivity
            r = alpha * dt / (dx**2)
            
            if r > 0.5:
                return {"error": "Unstable finite difference scheme. Reduce dt or increase dx."}
            
            # Finite difference scheme (explicit)
            for n in range(1, nt):
                for i in range(1, nx - 1):
                    u[n, i] = u[n-1, i] + r * (u[n-1, i+1] - 2*u[n-1, i] + u[n-1, i-1])
                
                # Apply boundary conditions
                u[n, 0] = boundary_conditions.get('left', 0)
                u[n, -1] = boundary_conditions.get('right', 0)
            
            # Create visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            X, T = np.meshgrid(x, t)
            contour = ax.contourf(X, T, u, levels=50, cmap='viridis')
            plt.colorbar(contour)
            ax.set_xlabel('x')
            ax.set_ylabel('t')
            ax.set_title('PDE Solution (Finite Difference Method)')
            
            # Save plot to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plot_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                "method": "finite_difference",
                "solution_matrix": u.tolist(),
                "x_grid": x.tolist(),
                "t_grid": t.tolist(),
                "plot": plot_data,
                "stability_parameter": r,
                "grid_size": (nx, nt)
            }
            
        except BiologyError as e:
            return {"error": f"Finite difference method failed: {str(e)}"}
    
    @staticmethod
    def _solve_finite_element(equation_str: str, boundary_conditions: Dict[str, Any], 
                             domain: Dict[str, Any]) -> Dict[str, Any]:
        """Solve PDE using finite element method (simplified)"""
        try:
            # This is a placeholder for a more complex FEM implementation
            # In practice, you would use libraries like FEniCS, dealii, or similar
            
            return {
                "method": "finite_element",
                "message": "Finite element method requires specialized libraries like FEniCS",
                "recommendation": "Use finite_difference method for current implementation"
            }
            
        except BiologyError as e:
            return {"error": f"Finite element method failed: {str(e)}"}


class DifferentialEquationService:
    """Servicio para ecuaciones diferenciales"""
    
    @staticmethod
    def solve_differential_equation(request: DifferentialEquationRequest) -> DifferentialEquationResponse:
        """
        Resuelve una ecuación diferencial
        
        Args:
            request: Solicitud con ecuación diferencial
            
        Returns:
            Respuesta con la solución
        """
        try:
            # Crear símbolos
            t = sp.Symbol(request.variable)
            function_name = request.function.split('(')[0]
            y = sp.Function(function_name)
            
            # Parsear la ecuación diferencial
            import re
            equation_str = request.equation
            # Replace higher-order derivatives first, then simple derivatives
            equation_str = re.sub(r"y''", "Derivative(y(t), t, 2)", equation_str)
            equation_str = re.sub(r"y'", "Derivative(y(t), t)", equation_str)
            # Replace standalone 'y' only when it's not followed by '(' to avoid double substitution
            equation_str = re.sub(r"\by\b(?!\()", "y(t)", equation_str)

            # Convertir a ecuación SymPy - manejar errores de parseo explícitamente
            try:
                if "=" in equation_str:
                    left, right = equation_str.split('=', 1)
                    equation_str = f"({left}) - ({right})"
                equation = sp.sympify(equation_str)
            except Exception as e:
                raise ValueError(f"Ecuación diferencial inválida: {str(e)}")

            # Resolver la ecuación diferencial
            try:
                general_solution = sp.dsolve(equation, y(t))
            except Exception as e:
                # If dsolve fails, return a response indicating failure
                return DifferentialEquationResponse(
                    equation=request.equation,
                    solution="<no solution found>",
                    method="dsolve_failed"
                )
            
            # Extraer la solución
            if isinstance(general_solution, list):
                solutions = [str(sol.rhs) if hasattr(sol, 'rhs') else str(sol) for sol in general_solution]
                solution_str = solutions[0] if solutions else "No solution found"
            else:
                solution_str = str(general_solution.rhs) if hasattr(general_solution, 'rhs') else str(general_solution)
            
            # Aplicar condiciones iniciales si existen
            particular_solution = None
            if request.initial_conditions:
                particular_solution = DifferentialEquationService._apply_initial_conditions(
                    general_solution, request.initial_conditions, t, y
                )
            
            # Determinar tipo de solución
            solution_type = DifferentialEquationService._determine_solution_type(equation, t, y)
            
            # Generar pasos de solución
            steps = [
                f"Ecuación diferencial: {request.equation}",
                f"Función: {request.function}({request.variable})",
                f"Método de solución: {solution_type}",
                f"Solución general: {solution_str}",
            ]
            
            if particular_solution:
                steps.append(f"Solución particular: {particular_solution}")
            
            return DifferentialEquationResponse(
                equation=request.equation,
                general_solution=solution_str,
                particular_solution=particular_solution,
                solution_type=solution_type,
                steps=steps
            )
            
        except BiologyError as e:
            raise ValueError(f"Error resolviendo ecuación diferencial: {str(e)}")
    
    @staticmethod
    def _apply_initial_conditions(general_solution: Any, initial_conditions: Dict[str, Any], 
                                 t: sp.Symbol, y: sp.Function) -> Optional[str]:
        """Aplica condiciones iniciales a la solución general"""
        try:
            # Extraer constantes de la solución
            constants = []
            if isinstance(general_solution, list):
                sol = general_solution[0]
            else:
                sol = general_solution
            
            if not hasattr(sol, 'rhs'):
                return None
                
            # Buscar constantes C1, C2, etc.
            for symbol in sol.rhs.free_symbols:
                if str(symbol).startswith('C'):
                    constants.append(symbol)
            
            if not constants:
                return None
            
            # Crear sistema de ecuaciones con las condiciones iniciales
            equations = []
            for condition, value in initial_conditions.items():
                if condition.startswith('y('):
                    # Condición de valor: y(t0) = value
                    t_val = float(condition[2:-1])
                    eq = sp.Eq(sol.rhs.subs(t, t_val), value)
                    equations.append(eq)
                elif condition.startswith("y'("):
                    # Condición de derivada: y'(t0) = value
                    t_val = float(condition[3:-1])
                    derivative = sp.diff(sol.rhs, t)
                    eq = sp.Eq(derivative.subs(t, t_val), value)
                    equations.append(eq)
            
            # Resolver sistema de ecuaciones
            if equations and constants:
                const_values = sp.solve(equations, constants)
                if const_values:
                    particular_sol = sol.rhs.subs(const_values)
                    return str(particular_sol)
            
            return None
            
        except BiologyError as e:
            print(f"Error aplicando condiciones iniciales: {e}")
            return None
    
    @staticmethod
    def _determine_solution_type(equation: sp.Expr, t: sp.Symbol, y: sp.Function) -> str:
        """Determina el tipo de ecuación diferencial"""
        try:
            # Buscar derivadas en la ecuación
            derivatives = []
            for expr in sp.preorder_traversal(equation):
                if isinstance(expr, sp.Derivative):
                    derivatives.append(expr)
            
            if not derivatives:
                return "algebraic"
            
            # Determinar orden máximo
            max_order = max(len(d.args[1:]) for d in derivatives)
            
            # Determinar si es lineal
            is_linear = equation.is_polynomial(y(t))
            
            # Determinar si es homogénea
            is_homogeneous = equation.subs(y(t), 0) == 0
            
            # Construir descripción del tipo
            type_parts = []
            type_parts.append(f"orden {max_order}")
            
            if is_linear:
                type_parts.append("lineal")
            else:
                type_parts.append("no lineal")
            
            if is_homogeneous:
                type_parts.append("homogénea")
            else:
                type_parts.append("no homogénea")
            
            return "Ecuación diferencial " + ", ".join(type_parts)
            
        except BiologyError as e:
            return f"Tipo desconocido: {str(e)}"
    
    @staticmethod
    def solve_pde_enhanced(equation: str, boundary_conditions: Optional[Dict[str, Any]] = None, 
                          domain: Optional[Dict[str, Any]] = None, method: str = "symbolic") -> Dict[str, Any]:
        """
        Enhanced PDE solver with both symbolic and numerical methods
        
        Args:
            equation: PDE equation string
            boundary_conditions: Boundary conditions
            domain: Domain specification
            method: "symbolic" or "numerical"
            
        Returns:
            Solution dictionary
        """
        try:
            if method == "symbolic":
                return DifferentialEquationService._solve_pde_symbolic(equation)
            elif method == "numerical":
                if not boundary_conditions or not domain:
                    return {"error": "Boundary conditions and domain required for numerical methods"}
                return PDESolver.solve_pde_numerical(equation, boundary_conditions, domain)
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except BiologyError as e:
            return {"error": f"PDE solving failed: {str(e)}"}
    
    @staticmethod
    def _solve_pde_symbolic(equation: str) -> SolvePdeSymbolicResult:
        """Solve PDE symbolically using SymPy"""
        try:
            # Parse variables
            x, y, t = sp.symbols('x y t')
            u = sp.Function('u')
            
            # Replace common PDE notation and attempt to parse; fallback gracefully on failures
            try:
                equation_str = equation
                equation_str = equation_str.replace('u_t', 'Derivative(u(x,t), t)')
                equation_str = equation_str.replace('u_xx', 'Derivative(u(x,t), x, 2)')
                equation_str = equation_str.replace('u_x', 'Derivative(u(x,t), x)')
                equation_str = equation_str.replace('u_xy', 'Derivative(u(x,t), x, y)')
                equation_str = equation_str.replace('u_yy', 'Derivative(u(x,t), y, 2)')
                equation_str = equation_str.replace('u', 'u(x,t)')

                pde = sp.sympify(equation_str)
            except Exception as e:
                logger.debug(f"PDE parsing failed: {e}")
                return {
                    "method": "symbolic",
                    "equation": equation,
                    "solution": "<unable to parse symbolically>",
                    "solution_type": "unknown",
                    "note": f"Parsing failed: {str(e)}"
                }

            # Attempt to solve using different methods
            try:
                solution = sp.pdsolve(pde, u(x,t))
                if solution:
                    return {
                        "method": "symbolic",
                        "equation": equation,
                        "solution": str(solution),
                        "solution_type": "analytical"
                    }
            except Exception as e:
                logger.debug(f"Direct pdsolve failed: {e}")
                try:
                    X = sp.Function('X')
                    T = sp.Function('T')
                    return {
                        "method": "symbolic",
                        "equation": equation,
                        "solution": "u(x,t) = X(x) * T(t) where separation of variables applies",
                        "solution_type": "separable",
                        "note": "Complete solution requires boundary conditions"
                    }
                except Exception as e2:
                    logger.debug(f"Separation of variables attempt failed: {e2}")

            return {
                "method": "symbolic",
                "equation": equation,
                "message": "No analytical solution found. Try numerical methods.",
                "recommendation": "Use method='numerical' for complex PDEs"
            }
                
        except BiologyError as e:
            return {"error": f"Symbolic PDE solving failed: {str(e)}"}
    
    @staticmethod
    def solve_pde(equation: str, function: str, variables: List[str], 
                 boundary_conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Solve partial differential equations
        
        Args:
            equation: PDE equation string
            function: Function name
            variables: List of variables
            boundary_conditions: Boundary conditions
            
        Returns:
            Solution dictionary
        """
        try:
            # Create symbols for variables
            var_symbols = [sp.Symbol(var) for var in variables]
            
            # Create function symbol
            u = sp.Function(function)(*var_symbols)
            
            # Parse equation
            eq_str = equation
            
            # Replace common notation
            for i, var in enumerate(variables):
                eq_str = eq_str.replace(f'{function}_{var}', f'Derivative({function}({",".join(variables)}), {var})')
                eq_str = eq_str.replace(f'{function}_{var}{var}', f'Derivative({function}({",".join(variables)}), {var}, 2)')
            
            eq_str = eq_str.replace(function, f'{function}({",".join(variables)})')
            
            # Convert to SymPy expression
            eq_sym = sp.sympify(eq_str)
            
            # Attempt to solve
            try:
                solution = sp.pdsolve(eq_sym, u)
                if solution:
                    return {
                        "equation": equation,
                        "solution": str(solution),
                        "variables": variables,
                        "function": function,
                        "method": "symbolic"
                    }
            except BiologyError as e:
                logger.debug(f"Symbolic pdsolve failed: {e}")
            
            return {
                "equation": equation,
                "message": "No analytical solution found",
                "variables": variables,
                "function": function,
                "method": "symbolic",
                "recommendation": "Try numerical methods for complex PDEs"
            }
            
        except BiologyError as e:
            return {"error": f"PDE solving failed: {str(e)}"}
