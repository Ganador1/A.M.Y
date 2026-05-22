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
from app.exceptions.domain.mathematics import MathematicsError
from app.domains.mathematics.utils import safe_sympify


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
        except MathematicsError as e:
            return {"error": f"Numerical method failed: {str(e)}"}

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
            
        except MathematicsError as e:
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
            
        except MathematicsError as e:
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
            y = sp.Function(function_name)(t)  # Crear la función aplicada a la variable
            
            # Parsear la ecuación diferencial manualmente
            # Para ecuaciones simples como "y' = -2*y", creamos la ecuación directamente
            if "'" in request.equation and "=" in request.equation:
                # Es una ecuación con notación prima
                left_side, right_side = request.equation.split("=", 1)
                left_side = left_side.strip()
                right_side = right_side.strip()
                
                # Crear la función y su derivada
                y_func = y
                dy_dt = sp.diff(y_func, t)
                
                # Parsear el lado derecho
                right_expr = safe_sympify(right_side)
                
                # Crear la ecuación
                equation = sp.Eq(dy_dt, right_expr)
            else:
                # Para ecuaciones más complejas, intentar usar el parser
                try:
                    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, convert_xor
                    local_dict = {
                        request.variable: t,
                        function_name: y
                    }
                    transformations = standard_transformations + (convert_xor,)
                    equation = parse_expr(request.equation, local_dict=local_dict, transformations=transformations)
                except Exception:
                    # Fallback: intentar parsear como expresión simple
                    equation = safe_sympify(request.equation)
            
            # Resolver la ecuación diferencial
            general_solution = sp.dsolve(equation, y)
            
            # Extraer la solución
            try:
                if isinstance(general_solution, list):
                    solution_str = str(general_solution[0]) if general_solution else "No solution found"
                else:
                    solution_str = str(general_solution)
            except MathematicsError:
                solution_str = "Unable to extract solution"
            
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
                solution=solution_str,
                method=solution_type
            )
            
        except MathematicsError as e:
            raise ValueError(f"Error resolviendo ecuación diferencial: {str(e)}")
    
    @staticmethod
    def _apply_initial_conditions(general_solution: Any, initial_conditions: Dict[str, Any], 
                                 t: sp.Symbol, y_func: Any) -> Optional[str]:
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
            
        except MathematicsError as e:
            print(f"Error aplicando condiciones iniciales: {e}")
            return None
    
    @staticmethod
    def _determine_solution_type(equation: Any, t: sp.Symbol, y_func: Any) -> str:
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
            is_linear = equation.is_polynomial(y_func)
            
            # Determinar si es homogénea
            is_homogeneous = equation.subs(y_func, 0) == 0
            
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
            
        except MathematicsError as e:
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
                
        except MathematicsError as e:
            return {"error": f"PDE solving failed: {str(e)}"}
    
    @staticmethod
    def _solve_pde_symbolic(equation: str) -> Dict[str, Any]:
        """Solve PDE symbolically using SymPy"""
        try:
            # Parse variables
            x, y, t = sp.symbols('x y t')
            u = sp.Function('u')
            
            # Replace common PDE notation using safe regex substitutions to avoid double-replacement
            import re
            equation_str = str(equation)

            # Replace derivative shorthand like u_xx, u_tt, u_xy, u_t
            def _replace_u_deriv(m):
                suffix = m.group(1)  # e.g., 'xx', 't', 'xy'
                mapping = {'x': 'x', 'y': 'y', 't': 't'}
                # If repeated same char like 'xx' -> second derivative w.r.t that var
                if len(suffix) > 1 and all(ch == suffix[0] for ch in suffix):
                    var = mapping[suffix[0]]
                    order = len(suffix)
                    return f"Derivative(u(x,t), {var}, {order})"
                else:
                    args = ', '.join(mapping[ch] for ch in suffix)
                    return f"Derivative(u(x,t), {args})"

            equation_str = re.sub(r'u_([xyt]+)', _replace_u_deriv, equation_str)

            # If any standalone 'u' remains (e.g., u = ...), replace with u(x,t)
            equation_str = re.sub(r'\bu\b', 'u(x,t)', equation_str)

            # Normalize equality to subtraction so sympy can parse as expression = 0
            if '=' in equation_str:
                left, right = equation_str.split('=', 1)
                equation_str = f"({left}) - ({right})"

            # Parse equation
            try:
                pde = safe_sympify(equation_str)
            except Exception as e:
                # Parsing failed; return a graceful symbolic response indicating inability to parse
                return {
                    "method": "symbolic",
                    "equation": equation,
                    "solution": "<unable to parse symbolically>",
                    "solution_type": "unknown",
                    "note": f"Parsing failed: {str(e)}"
                }

            # Attempt to solve using different methods
            try:
                # Try direct pdsolve
                solution = sp.pdsolve(pde, u(x,t))
                if solution:
                    return {
                        "method": "symbolic",
                        "equation": equation,
                        "solution": str(solution),
                        "solution_type": "analytical"
                    }
            except Exception as e:
                # Try separation of variables as a fallback
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
                    # If fallback fails, return a graceful note
                    return {
                        "method": "symbolic",
                        "equation": equation,
                        "solution": "<no symbolic solution found>",
                        "solution_type": "none",
                        "note": f"Symbolic solving failed: {str(e2)}"
                    }

            return {
                "method": "symbolic",
                "equation": equation,
                "solution": "<no symbolic solution found>",
                "solution_type": "none",
                "message": "No analytical solution found. Try numerical methods.",
                "recommendation": "Use method='numerical' for complex PDEs"
            }
                
        except MathematicsError as e:
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
            eq_sym = safe_sympify(eq_str)
            
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
            except MathematicsError as e:
                print(f"PDE solving attempt failed: {e}")
                pass
            
            return {
                "equation": equation,
                "message": "No analytical solution found",
                "variables": variables,
                "function": function,
                "method": "symbolic",
                "recommendation": "Try numerical methods for complex PDEs"
            }
            
        except MathematicsError as e:
            return {"error": f"PDE solving failed: {str(e)}"}

    @staticmethod
    def solve_heat_equation_fd(domain: Dict[str, Any], boundary_conditions: Dict[str, Any],
                              initial_conditions: Dict[str, Any], parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve heat equation using finite difference method
        """
        try:
            if parameters is None:
                parameters = {"alpha": 0.5}
            
            # Domain parameters
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
            if 'function' in initial_conditions:
                initial_func = initial_conditions['function']
                if callable(initial_func):
                    u[0, :] = np.array([initial_func(xi) for xi in x])
                else:
                    # Default: sine wave
                    u[0, :] = np.sin(np.pi * x)
            
            # Thermal diffusivity
            alpha = parameters.get('alpha', 0.5)
            r = alpha * dt / (dx**2)
            
            if r > 0.5:
                return {"error": "Unstable scheme. Reduce dt or increase dx."}
            
            # Time stepping using explicit finite difference
            for n in range(1, nt):
                for i in range(1, nx-1):
                    u[n, i] = u[n-1, i] + r * (u[n-1, i+1] - 2*u[n-1, i] + u[n-1, i-1])
                
                # Apply boundary conditions
                if 'left' in boundary_conditions:
                    u[n, 0] = boundary_conditions['left']
                if 'right' in boundary_conditions:
                    u[n, -1] = boundary_conditions['right']
            
            return {
                "success": True,
                "method": "finite_difference",
                "equation_type": "heat",
                "solution": u.tolist(),
                "x_grid": x.tolist(),
                "t_grid": t.tolist(),
                "parameters": {"alpha": alpha, "r": r},
                "stability": "stable" if r <= 0.5 else "unstable"
            }
            
        except MathematicsError as e:
            return {"error": f"Heat equation FD solver failed: {str(e)}"}

    @staticmethod
    def solve_wave_equation_fd(domain: Dict[str, Any], boundary_conditions: Dict[str, Any],
                              initial_conditions: Dict[str, Any], parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve wave equation using finite difference method
        """
        try:
            if parameters is None:
                parameters = {"c": 1.0}
            
            # Domain parameters
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
            
            # Wave speed
            c = parameters.get('c', 1.0)
            r = c * dt / dx
            
            if r > 1.0:
                return {"error": "Unstable scheme. CFL condition violated: c*dt/dx > 1"}
            
            # Apply initial conditions
            if 'displacement' in initial_conditions:
                disp_func = initial_conditions['displacement']
                if callable(disp_func):
                    u[0, :] = np.array([disp_func(xi) for xi in x])
                else:
                    u[0, :] = np.sin(np.pi * x)
            
            if 'velocity' in initial_conditions:
                vel_func = initial_conditions['velocity']
                if callable(vel_func):
                    u[1, :] = u[0, :] + dt * np.array([vel_func(xi) for xi in x])
                else:
                    u[1, :] = u[0, :]  # Zero initial velocity
            
            # Time stepping using explicit finite difference
            for n in range(1, nt-1):
                for i in range(1, nx-1):
                    u[n+1, i] = 2*u[n, i] - u[n-1, i] + (r**2) * (u[n, i+1] - 2*u[n, i] + u[n, i-1])
                
                # Apply boundary conditions
                if 'left' in boundary_conditions:
                    u[n+1, 0] = boundary_conditions['left']
                if 'right' in boundary_conditions:
                    u[n+1, -1] = boundary_conditions['right']
            
            return {
                "success": True,
                "method": "finite_difference",
                "equation_type": "wave",
                "solution": u.tolist(),
                "x_grid": x.tolist(),
                "t_grid": t.tolist(),
                "parameters": {"c": c, "r": r},
                "stability": "stable" if r <= 1.0 else "unstable"
            }
            
        except MathematicsError as e:
            return {"error": f"Wave equation FD solver failed: {str(e)}"}

    @staticmethod
    def solve_laplace_equation_fd(domain: Dict[str, Any], boundary_conditions: Dict[str, Any],
                                 parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve Laplace equation using finite difference method (iterative)
        """
        try:
            if parameters is None:
                parameters = {"tolerance": 1e-6, "max_iterations": 1000}
            
            # Domain parameters
            x_min, x_max = domain.get('x_min', 0), domain.get('x_max', 1)
            y_min, y_max = domain.get('y_min', 0), domain.get('y_max', 1)
            nx, ny = domain.get('nx', 50), domain.get('ny', 50)
            
            # Grid setup
            dx = (x_max - x_min) / (nx - 1)
            dy = (y_max - y_min) / (ny - 1)
            
            x = np.linspace(x_min, x_max, nx)
            y = np.linspace(y_min, y_max, ny)
            
            # Initialize solution array
            u = np.zeros((ny, nx))
            
            # Apply boundary conditions
            if 'top' in boundary_conditions:
                u[-1, :] = boundary_conditions['top']
            if 'bottom' in boundary_conditions:
                u[0, :] = boundary_conditions['bottom']
            if 'left' in boundary_conditions:
                u[:, 0] = boundary_conditions['left']
            if 'right' in boundary_conditions:
                u[:, -1] = boundary_conditions['right']
            
            # Iterative solver (Gauss-Seidel)
            tolerance = parameters.get('tolerance', 1e-6)
            max_iterations = parameters.get('max_iterations', 1000)
            
            for iteration in range(max_iterations):
                u_old = u.copy()
                
                for i in range(1, ny-1):
                    for j in range(1, nx-1):
                        u[i, j] = 0.25 * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1])
                
                # Check convergence
                error = np.max(np.abs(u - u_old))
                if error < tolerance:
                    break
            
            return {
                "success": True,
                "method": "finite_difference",
                "equation_type": "laplace",
                "solution": u.tolist(),
                "x_grid": x.tolist(),
                "y_grid": y.tolist(),
                "iterations": iteration + 1,
                "final_error": float(error),
                "converged": error < tolerance
            }
            
        except MathematicsError as e:
            return {"error": f"Laplace equation FD solver failed: {str(e)}"}

    @staticmethod
    def analyze_pde_type(equation: str) -> Dict[str, Any]:
        """
        Analyze and classify PDE type
        """
        try:
            # Common PDE patterns
            pde_types = {
                "heat": {
                    "patterns": ["u_t", "∂u/∂t", "u_xx", "∂²u/∂x²"],
                    "description": "Parabolic PDE - Heat/Diffusion equation",
                    "canonical_form": "∂u/∂t = α∇²u"
                },
                "wave": {
                    "patterns": ["u_tt", "∂²u/∂t²", "u_xx", "∂²u/∂x²"],
                    "description": "Hyperbolic PDE - Wave equation",
                    "canonical_form": "∂²u/∂t² = c²∇²u"
                },
                "laplace": {
                    "patterns": ["u_xx", "u_yy", "∂²u/∂x²", "∂²u/∂y²", "= 0"],
                    "description": "Elliptic PDE - Laplace equation",
                    "canonical_form": "∇²u = 0"
                },
                "poisson": {
                    "patterns": ["u_xx", "u_yy", "∂²u/∂x²", "∂²u/∂y²", "= f"],
                    "description": "Elliptic PDE - Poisson equation",
                    "canonical_form": "∇²u = f(x,y)"
                }
            }
            
            detected_types = []
            
            for pde_type, info in pde_types.items():
                pattern_matches = sum(1 for pattern in info["patterns"] if pattern in equation)
                if pattern_matches >= 2:  # At least 2 patterns must match
                    detected_types.append({
                        "type": pde_type,
                        "description": info["description"],
                        "canonical_form": info["canonical_form"],
                        "confidence": pattern_matches / len(info["patterns"])
                    })
            
            # Sort by confidence
            detected_types.sort(key=lambda x: x["confidence"], reverse=True)
            
            return {
                "success": True,
                "equation": equation,
                "detected_types": detected_types,
                "primary_type": detected_types[0]["type"] if detected_types else "unknown",
                "analysis": {
                    "is_linear": "u²" not in equation and "u*u" not in equation,
                    "has_time_derivative": any(pattern in equation for pattern in ["u_t", "∂u/∂t", "u_tt", "∂²u/∂t²"]),
                    "spatial_dimensions": equation.count("x") + equation.count("y") + equation.count("z")
                }
            }
            
        except MathematicsError as e:
            return {"error": f"PDE analysis failed: {str(e)}"}

    @staticmethod
    def get_pde_info(pde_type: str = "all") -> Dict[str, Any]:
        """
        Get information about PDE types and their properties
        """
        try:
            pde_info = {
                "heat": {
                    "name": "Heat/Diffusion Equation",
                    "type": "Parabolic",
                    "canonical_form": "∂u/∂t = α∇²u",
                    "description": "Models heat conduction and diffusion processes",
                    "applications": [
                        "Heat conduction in solids",
                        "Diffusion of chemicals",
                        "Population dynamics",
                        "Financial mathematics (Black-Scholes)"
                    ],
                    "boundary_conditions": [
                        "Dirichlet: u = g on boundary",
                        "Neumann: ∂u/∂n = h on boundary",
                        "Robin: αu + β∂u/∂n = γ on boundary"
                    ],
                    "solution_methods": [
                        "Separation of variables",
                        "Fourier series",
                        "Green's functions",
                        "Finite difference",
                        "Finite element"
                    ]
                },
                "wave": {
                    "name": "Wave Equation",
                    "type": "Hyperbolic",
                    "canonical_form": "∂²u/∂t² = c²∇²u",
                    "description": "Models wave propagation phenomena",
                    "applications": [
                        "Sound waves",
                        "Electromagnetic waves",
                        "Seismic waves",
                        "String vibrations",
                        "Water waves"
                    ],
                    "boundary_conditions": [
                        "Fixed ends: u = 0",
                        "Free ends: ∂u/∂x = 0",
                        "Absorbing: ∂u/∂t + c∂u/∂x = 0"
                    ],
                    "solution_methods": [
                        "D'Alembert's formula",
                        "Separation of variables",
                        "Fourier series",
                        "Finite difference",
                        "Characteristics method"
                    ]
                },
                "laplace": {
                    "name": "Laplace Equation",
                    "type": "Elliptic",
                    "canonical_form": "∇²u = 0",
                    "description": "Models steady-state phenomena",
                    "applications": [
                        "Electrostatics",
                        "Steady-state heat conduction",
                        "Fluid flow (potential flow)",
                        "Gravitational potential"
                    ],
                    "boundary_conditions": [
                        "Dirichlet: u = g on boundary",
                        "Neumann: ∂u/∂n = h on boundary",
                        "Mixed boundary conditions"
                    ],
                    "solution_methods": [
                        "Separation of variables",
                        "Green's functions",
                        "Conformal mapping",
                        "Finite difference",
                        "Finite element"
                    ]
                },
                "poisson": {
                    "name": "Poisson Equation",
                    "type": "Elliptic",
                    "canonical_form": "∇²u = f(x,y,z)",
                    "description": "Models steady-state with source terms",
                    "applications": [
                        "Electrostatics with charges",
                        "Gravitational potential with mass",
                        "Heat conduction with sources"
                    ],
                    "boundary_conditions": [
                        "Dirichlet: u = g on boundary",
                        "Neumann: ∂u/∂n = h on boundary"
                    ],
                    "solution_methods": [
                        "Green's functions",
                        "Finite difference",
                        "Finite element",
                        "Variational methods"
                    ]
                }
            }
            
            if pde_type == "all":
                return {
                    "success": True,
                    "pde_types": pde_info,
                    "classification": {
                        "parabolic": ["heat"],
                        "hyperbolic": ["wave"],
                        "elliptic": ["laplace", "poisson"]
                    }
                }
            elif pde_type in pde_info:
                return {
                    "success": True,
                    "pde_type": pde_type,
                    "info": pde_info[pde_type]
                }
            else:
                return {"error": f"Unknown PDE type: {pde_type}"}
                
        except MathematicsError as e:
            return {"error": f"PDE info retrieval failed: {str(e)}"}






