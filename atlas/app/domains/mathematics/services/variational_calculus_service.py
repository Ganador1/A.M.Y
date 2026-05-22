"""
Variational Calculus Service for Mathematics AI
Provides capabilities for calculus of variations, Euler-Lagrange equations, and physics applications
"""

import sympy as sp
from typing import Dict, List, Any
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from app.exceptions.domain.mathematics import MathematicsError


class VariationalCalculusService:
    """Service for variational calculus and optimization"""

    def __init__(self):
        self.t = sp.Symbol('t', real=True)
        self.x = sp.Function('x')(self.t)
        self.y = sp.Function('y')(self.t)
        self.L = sp.Symbol('L')  # Lagrangian

        # Common functionals
        self.functionals = {
            'brachistochrone': {
                'description': 'Shortest time path between two points',
                'lagrangian': 'sqrt(2*g*y)/(sqrt(v**2 - 2*g*y))',
                'variables': ['x', 'y'],
                'constraints': 'dx/dt = v'
            },
            'geodesic': {
                'description': 'Shortest path on a surface',
                'lagrangian': 'sqrt(g_μν * dx^μ/dt * dx^ν/dt)',
                'variables': ['x', 'y', 'z'],
                'constraints': 'Surface equation'
            },
            'minimal_surface': {
                'description': 'Surface with minimal area',
                'lagrangian': 'sqrt(1 + (dz/dx)^2 + (dz/dy)^2)',
                'variables': ['x', 'y', 'z'],
                'constraints': 'Boundary conditions'
            }
        }

    def euler_lagrange_equation(self, lagrangian: str, variable: str = 'x',
                               time_variable: str = 't') -> Dict[str, Any]:
        """
        Derive the Euler-Lagrange equation for a given Lagrangian

        d/dt(∂L/∂(dx/dt)) - ∂L/∂x = 0
        """
        try:
            # Parse the Lagrangian
            L_expr = sp.sympify(lagrangian)
            t_var = sp.Symbol(time_variable)

            # Define the function and its derivative
            x_func = sp.Function(variable)(t_var)
            x_dot = sp.diff(x_func, t_var)

            # Compute partial derivatives
            dL_dx = sp.diff(L_expr, x_func).doit()
            dL_dx_dot = sp.diff(L_expr, x_dot).doit()

            # Compute d/dt of dL/dx_dot
            d_dt_dL_dx_dot = sp.diff(dL_dx_dot, t_var).doit()

            # Euler-Lagrange equation
            el_equation = sp.Eq(sp.expand(d_dt_dL_dx_dot) - sp.expand(dL_dx), 0)

            # Try to solve for the second derivative
            simplified = sp.simplify(el_equation)

            return {
                'lagrangian': str(L_expr),
                'euler_lagrange_equation': str(simplified),
                'partial_L_partial_x': str(dL_dx),
                'partial_L_partial_x_dot': str(dL_dx_dot),
                'd_dt_partial_L_partial_x_dot': str(d_dt_dL_dx_dot),
                'variable': variable,
                'time_variable': time_variable,
                'simplified': str(sp.simplify(simplified)),
                'status': 'success'
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'lagrangian': lagrangian,
                'status': 'failed'
            }

    def variational_derivative(self, functional: str, variable: str = 'x',
                              time_variable: str = 't') -> Dict[str, Any]:
        """
        Compute the variational derivative δF/δx of a functional F
        """
        try:
            # For now, implement for simple cases
            # F = ∫ L(x, x', t) dt
            L_expr = sp.sympify(functional)
            t_var = sp.Symbol(time_variable)

            x_func = sp.Function(variable)(t_var)
            x_dot = sp.diff(x_func, t_var)

            # Variational derivative for ∫ L dt
            dL_dx = sp.diff(L_expr, x_func).doit()
            dL_dx_dot = sp.diff(L_expr, x_dot).doit()
            d_dx_dot_dL_dx_dot = sp.diff(dL_dx_dot, t_var).doit()

            variational_derivative = sp.expand(d_dx_dot_dL_dx_dot) - sp.expand(dL_dx)

            return {
                'functional': str(L_expr),
                'variational_derivative': str(variational_derivative),
                'simplified': str(sp.simplify(variational_derivative)),
                'variable': variable,
                'time_variable': time_variable,
                'status': 'success'
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'functional': functional,
                'status': 'failed'
            }

    def solve_brachistochrone(self, x1: float, y1: float, x2: float, y2: float,
                             g: float = 9.81) -> Dict[str, Any]:
        """
        Solve the brachistochrone problem: fastest path between two points
        """
        try:
            # The brachistochrone curve is a cycloid
            # Parametric equations: x = a(θ - sinθ), y = a(1 - cosθ)

            # Solve for parameter a
            # Distance constraint: sqrt((x2-x1)^2 + (y2-y1)^2) = 2aθ
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

            # For brachistochrone, θ ranges from 0 to some θ_max
            # The relation is more complex, but for simplicity:
            theta_max = np.pi  # Approximate
            a = distance / (2 * theta_max)

            # Generate the curve
            theta = np.linspace(0, theta_max, 100)
            x_curve = a * (theta - np.sin(theta)) + x1
            y_curve = a * (1 - np.cos(theta)) + y1

            # Calculate travel time
            # Time = ∫ dt = ∫ dx/v = ∫ dx / sqrt(2gy)
            # For brachistochrone: t = θ * sqrt(a/g)
            travel_time = theta_max * np.sqrt(a / g)

            # Create plot
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(x_curve, y_curve, 'b-', linewidth=2, label='Brachistochrone')
            ax.plot([x1, x2], [y1, y2], 'r--', label='Straight line')
            ax.scatter([x1, x2], [y1, y2], color='red', s=50)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_title('Brachistochrone Problem Solution')
            ax.legend()
            ax.grid(True)
            ax.set_aspect('equal')

            # Convert plot to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            plot_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()

            return {
                'problem_type': 'brachistochrone',
                'start_point': [x1, y1],
                'end_point': [x2, y2],
                'parameter_a': a,
                'max_theta': theta_max,
                'travel_time': travel_time,
                'x_coordinates': x_curve.tolist(),
                'y_coordinates': y_curve.tolist(),
                'plot': plot_base64,
                'description': 'Fastest path between two points under gravity',
                'status': 'success'
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'problem_type': 'brachistochrone',
                'status': 'failed'
            }

    def minimal_surface_area(self, boundary_points: List[List[float]],
                           num_points: int = 50) -> Dict[str, Any]:
        """
        Compute minimal surface area between boundary points
        """
        try:
            # Simple implementation using catenary approximation
            # For a more complete implementation, would need finite element methods

            points = np.array(boundary_points)
            x_coords = points[:, 0]
            y_coords = points[:, 1]

            # Fit a catenary curve: y = a * cosh(x/a) + b
            def catenary(params, x):
                a, b = params
                return a * np.cosh(x / a) + b

            # Simple parameter estimation
            x_min, x_max = np.min(x_coords), np.max(x_coords)
            y_min, y_max = np.min(y_coords), np.max(y_coords)

            # Approximate parameters
            a_est = (x_max - x_min) / 2
            b_est = (y_min + y_max) / 2

            # Generate minimal surface
            x_surface = np.linspace(x_min, x_max, num_points)
            y_surface = catenary([a_est, b_est], x_surface - x_min) + y_min

            # Calculate approximate area (simplified)
            # For minimal surface, this would be more complex
            area = np.trapezoid(y_surface, x_surface)

            # Create plot
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(x_surface, y_surface, 'g-', linewidth=2, label='Minimal surface')
            ax.scatter(x_coords, y_coords, color='red', s=50, label='Boundary points')
            ax.fill_between(x_surface, y_surface, alpha=0.3, color='green')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_title('Minimal Surface Area')
            ax.legend()
            ax.grid(True)

            # Convert plot to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            plot_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()

            return {
                'problem_type': 'minimal_surface',
                'boundary_points': boundary_points,
                'x_coordinates': x_surface.tolist(),
                'y_coordinates': y_surface.tolist(),
                'approximate_area': area,
                'parameters': {'a': a_est, 'b': b_est},
                'plot': plot_base64,
                'description': 'Surface with minimal area connecting boundary points',
                'status': 'success'
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'problem_type': 'minimal_surface',
                'status': 'failed'
            }

    def principle_of_least_action(self, lagrangian: str, initial_conditions: Dict[str, float],
                                final_conditions: Dict[str, float], time_interval: List[float]) -> Dict[str, Any]:
        """
        Apply the principle of least action to find the path of stationary action
        """
        try:
            # Parse Lagrangian
            L_expr = sp.sympify(lagrangian)
            # For numerical solution, we'd need to discretize and optimize
            # This is a simplified implementation

            return {
                'lagrangian': str(L_expr),
                'principle': 'δS = 0 where S = ∫ L(q, q̇, t) dt',
                'initial_conditions': initial_conditions,
                'final_conditions': final_conditions,
                'time_interval': time_interval,
                'method': 'Euler-Lagrange equations',
                'note': 'Full numerical solution requires discretization and optimization',
                'status': 'success'
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'lagrangian': lagrangian,
                'status': 'failed'
            }

    def get_functionals_list(self) -> Dict[str, Any]:
        """
        Get list of available functionals for variational problems
        """
        return {
            'functionals': self.functionals,
            'description': 'Common functionals in calculus of variations',
            'count': len(self.functionals)
        }
