"""
Partial Differential Equations (PDE) Service for Mathematics AI
Provides capabilities for solving and analyzing partial differential equations

⚠️ Seguridad: este módulo evalúa expresiones de condiciones iniciales/frontera con `eval` en un espacio de nombres reducido.
- No aceptar expresiones de usuarios no confiables.
- Preferir plantillas/funciones predefinidas validadas.
- Revisa `ETHICS_AND_SAFETY.md`.
"""

import numpy as np
import sympy as sp
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import io
import base64

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.pde_service_types import (
    ProcessRequestResult,
    SolveHeatEquationAsyncResult,
    SolveWaveEquationAsyncResult,
    SolveLaplaceEquationAsyncResult,
    GetPdeInfoResult,
    AnalyzePdeTypeResult,
)


class PDEService(BaseService):
    """Service for solving partial differential equations"""

    def __init__(self):
        super().__init__("PDEService")
        self.x, self.y, self.t = sp.symbols('x y t')
        self.common_pdes = {
            'heat': {
                'equation': '∂u/∂t = α * ∂²u/∂x²',
                'description': 'Heat equation - models heat diffusion',
                'applications': ['Heat conduction', 'Diffusion processes', 'Financial mathematics']
            },
            'wave': {
                'equation': '∂²u/∂t² = c² * ∂²u/∂x²',
                'description': 'Wave equation - models wave propagation',
                'applications': ['Sound waves', 'Light waves', 'Seismic waves', 'String vibrations']
            },
            'laplace': {
                'equation': '∂²u/∂x² + ∂²u/∂y² = 0',
                'description': 'Laplace equation - models steady-state phenomena',
                'applications': ['Electrostatics', 'Fluid flow', 'Heat conduction (steady-state)']
            },
            'poisson': {
                'equation': '∂²u/∂x² + ∂²u/∂y² = f(x,y)',
                'description': 'Poisson equation - models steady-state with source',
                'applications': ['Electrostatics with charges', 'Gravitational potential']
            },
            'burgers': {
                'equation': '∂u/∂t + u * ∂u/∂x = ν * ∂²u/∂x²',
                'description': 'Burgers equation - models shock waves and viscous flow',
                'applications': ['Fluid dynamics', 'Traffic flow', 'Shock waves']
            },
            'navier_stokes': {
                'equation': '∂u/∂t + (u·∇)u = -∇p/ρ + ν∇²u',
                'description': 'Navier-Stokes equations - fundamental fluid dynamics',
                'applications': ['Weather prediction', 'Aerodynamics', 'Blood flow']
            }
        }

        logger.info("✅ PDEService initialized")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process PDE service requests"""
        try:
            action = request_data.get("action", "")

            if action == "solve_heat_equation":
                return await self._solve_heat_equation_async(request_data)
            elif action == "solve_wave_equation":
                return await self._solve_wave_equation_async(request_data)
            elif action == "solve_laplace_equation":
                return await self._solve_laplace_equation_async(request_data)
            elif action == "analyze_pde":
                return self.analyze_pde_type(request_data.get("equation", ""))
            elif action == "get_info":
                return self.get_pde_info()
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "solve_heat_equation", "solve_wave_equation", "solve_laplace_equation",
                        "analyze_pde", "get_info"
                    ]
                }
        except BiologyError as e:
            return self.handle_error(e, "process_request")

    async def _solve_heat_equation_async(self, request_data: SolveHeatEquationAsyncResult) -> SolveHeatEquationAsyncResult:
        """Async wrapper for heat equation solver"""
        try:
            result = self.solve_heat_equation_fd(
                L=request_data.get("L", 1.0),
                T=request_data.get("T", 1.0),
                alpha=request_data.get("alpha", 0.01),
                nx=request_data.get("nx", 50),
                nt=request_data.get("nt", 1000),
                initial_condition=request_data.get("initial_condition", "np.sin(np.pi*x)"),
                boundary_conditions=request_data.get("boundary_conditions")
            )
            return {"success": True, "result": result}
        except BiologyError as e:
            return {"success": False, "error": str(e)}

    async def _solve_wave_equation_async(self, request_data: SolveWaveEquationAsyncResult) -> SolveWaveEquationAsyncResult:
        """Async wrapper for wave equation solver"""
        try:
            result = self.solve_wave_equation_fd(
                L=request_data.get("L", 1.0),
                T=request_data.get("T", 2.0),
                c=request_data.get("c", 1.0),
                nx=request_data.get("nx", 50),
                nt=request_data.get("nt", 1000),
                initial_displacement=request_data.get("initial_displacement", "np.sin(np.pi*x)"),
                initial_velocity=request_data.get("initial_velocity", "0")
            )
            return {"success": True, "result": result}
        except BiologyError as e:
            return {"success": False, "error": str(e)}

    async def _solve_laplace_equation_async(self, request_data: SolveLaplaceEquationAsyncResult) -> SolveLaplaceEquationAsyncResult:
        """Async wrapper for Laplace equation solver"""
        try:
            result = self.solve_laplace_equation_fd(
                nx=request_data.get("nx", 50),
                ny=request_data.get("ny", 50),
                boundary_conditions=request_data.get("boundary_conditions")
            )
            return {"success": True, "result": result}
        except BiologyError as e:
            return {"success": False, "error": str(e)}

    def solve_heat_equation_fd(self, L: float = 1.0, T: float = 1.0, alpha: float = 0.01,
                              nx: int = 50, nt: int = 1000, initial_condition: str = "np.sin(np.pi*x)",
                              boundary_conditions: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Solve 1D heat equation using finite difference method with memory optimization

        ∂u/∂t = α * ∂²u/∂x²

        Args:
            L: Length of the domain
            T: Total time
            alpha: Thermal diffusivity
            nx: Number of spatial points (limited for memory)
            nt: Number of time steps (limited for memory)
            initial_condition: Initial condition as string
            boundary_conditions: Boundary conditions

        Returns:
            Dictionary with solution data and visualization
        """
        # Memory optimization: limit grid size
        max_nx = 200
        max_nt = 5000
        
        if nx > max_nx:
            logger.warning(f"Reducing nx from {nx} to {max_nx} for memory optimization")
            nx = max_nx
        
        if nt > max_nt:
            logger.warning(f"Reducing nt from {nt} to {max_nt} for memory optimization")
            nt = max_nt
            
        if boundary_conditions is None:
            boundary_conditions = {"left": "0", "right": "0"}

        # Spatial and temporal discretization
        dx = L / (nx - 1)
        dt = T / nt
        x = np.linspace(0, L, nx)

        # Stability condition for explicit scheme
        if alpha * dt / dx**2 > 0.5:
            # Auto-adjust dt for stability
            dt = 0.4 * dx**2 / alpha
            nt = int(T / dt)
            logger.warning(f"Adjusted dt to {dt:.6f} and nt to {nt} for stability")

        # Memory-efficient solution: only store current and next time steps
        u_current = np.zeros(nx)
        u_next = np.zeros(nx)
        
        # Store solution at selected time points for visualization
        time_snapshots = [0, nt//4, nt//2, 3*nt//4, nt]
        solution_snapshots = {}

        # Set initial condition safely
        try:
            from sympy import sympify, lambdify, symbols
            expr = sympify(initial_condition)
            func_lambda = lambdify(symbols('x'), expr, modules=['numpy', {'pi': np.pi}])
            u_current[:] = func_lambda(x)
        except Exception as e:
            logger.warning(f"Error evaluating initial condition '{initial_condition}': {e}. Using default.")
            u_current[:] = np.sin(np.pi * x)  # Default

        # Store initial snapshot
        solution_snapshots[0] = u_current.copy()

        # Set boundary conditions safely
        try:
            from sympy import sympify
            left_bc = float(sympify(boundary_conditions.get("left", "0")).evalf())
            right_bc = float(sympify(boundary_conditions.get("right", "0")).evalf())
        except Exception as e:
            logger.warning(f"Error evaluating boundary conditions: {e}. Using 0.")
            left_bc = 0.0
            right_bc = 0.0

        # Time stepping using explicit Euler with memory optimization
        r = alpha * dt / dx**2
        for n in range(nt):
            # Update interior points
            u_next[1:-1] = u_current[1:-1] + r * (u_current[:-2] - 2*u_current[1:-1] + u_current[2:])
            
            # Apply boundary conditions
            u_next[0] = left_bc
            u_next[-1] = right_bc
            
            # Store snapshots at selected times
            if n + 1 in time_snapshots:
                solution_snapshots[n + 1] = u_next.copy()
            
            # Swap arrays for next iteration
            u_current, u_next = u_next, u_current

        # Create visualization with reduced memory footprint
        fig, ax = plt.subplots(figsize=(10, 6))
        for n in time_snapshots:
            if n in solution_snapshots:
                ax.plot(x, solution_snapshots[n], label=f't = {n*dt:.3f}')

        ax.set_xlabel('Position x')
        ax.set_ylabel('Temperature u')
        ax.set_title('Heat Equation Solution (Memory Optimized)')
        ax.legend()
        ax.grid(True)

        # Convert plot to base64 with reduced DPI for memory
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)

        return {
            "solution_type": "finite_difference_optimized",
            "equation": "∂u/∂t = α * ∂²u/∂x²",
            "parameters": {
                "L": L, "T": T, "alpha": alpha, "nx": nx, "nt": nt,
                "dx": dx, "dt": dt
            },
            "stability": alpha * dt / dx**2 <= 0.5,
            "final_solution": solution_snapshots[nt].tolist() if nt in solution_snapshots else u_current.tolist(),
            "visualization": f"data:image/png;base64,{image_base64}",
            "method": "Explicit Euler finite difference (memory optimized)",
            "memory_optimizations": {
                "max_nx": max_nx,
                "max_nt": max_nt,
                "snapshots_stored": len(solution_snapshots)
            }
        }

    def solve_wave_equation_fd(self, L: float = 1.0, T: float = 2.0, c: float = 1.0,
                              nx: int = 50, nt: int = 1000,
                              initial_displacement: str = "np.sin(np.pi*x)",
                              initial_velocity: str = "0") -> Dict[str, Any]:
        """
        Solve 1D wave equation using finite difference method with memory optimization

        ∂²u/∂t² = c² * ∂²u/∂x²

        Args:
            L: Length of the domain
            T: Total time
            c: Wave speed
            nx: Number of spatial points (limited for memory)
            nt: Number of time steps (limited for memory)
            initial_displacement: Initial displacement as string
            initial_velocity: Initial velocity as string

        Returns:
            Dictionary with solution data and visualization
        """
        # Memory optimization: limit grid size
        max_nx = 200
        max_nt = 5000
        
        if nx > max_nx:
            logger.warning(f"Reducing nx from {nx} to {max_nx} for memory optimization")
            nx = max_nx
        
        if nt > max_nt:
            logger.warning(f"Reducing nt from {nt} to {max_nt} for memory optimization")
            nt = max_nt
            
        # Spatial and temporal discretization
        dx = L / (nx - 1)
        dt = T / nt
        x = np.linspace(0, L, nx)

        # Stability condition for wave equation
        if c * dt / dx > 1:
            # Auto-adjust dt for stability
            dt = 0.9 * dx / c
            nt = int(T / dt)
            logger.warning(f"Adjusted dt to {dt:.6f} and nt to {nt} for stability")

        # Memory-efficient solution: only store three time levels
        u_prev = np.zeros(nx)  # u^(n-1)
        u_curr = np.zeros(nx)  # u^n
        u_next = np.zeros(nx)  # u^(n+1)
        
        # Store solution at selected time points for visualization
        time_snapshots = [0, nt//4, nt//2, 3*nt//4, nt]
        solution_snapshots = {}

        # Set initial conditions safely
        try:
            from sympy import sympify, lambdify, symbols
            x_sym = symbols('x')
            
            # Initial displacement
            expr_disp = sympify(initial_displacement)
            func_disp = lambdify(x_sym, expr_disp, modules=['numpy', {'pi': np.pi}])
            u_curr[:] = func_disp(x)
            
            # Initial velocity (backward difference approximation)
            expr_vel = sympify(initial_velocity)
            func_vel = lambdify(x_sym, expr_vel, modules=['numpy', {'pi': np.pi}])
            initial_vel = func_vel(x)
            
            u_prev[:] = u_curr[:] - dt * initial_vel
        except Exception as e:
            logger.warning(f"Error evaluating initial conditions: {e}. Using default.")
            u_curr[:] = np.sin(np.pi * x)
            u_prev[:] = u_curr[:]

        # Store initial snapshot
        solution_snapshots[0] = u_curr.copy()

        # Boundary conditions (fixed ends)
        u_prev[0] = u_prev[-1] = 0
        u_curr[0] = u_curr[-1] = 0

        # Time stepping with memory optimization
        r = (c * dt / dx) ** 2
        for n in range(1, nt):
            # Update interior points
            u_next[1:-1] = (2 * u_curr[1:-1] - u_prev[1:-1] + 
                           r * (u_curr[:-2] - 2*u_curr[1:-1] + u_curr[2:]))
            
            # Apply boundary conditions
            u_next[0] = u_next[-1] = 0
            
            # Store snapshots at selected times
            if n in time_snapshots:
                solution_snapshots[n] = u_next.copy()
            
            # Rotate arrays for next iteration
            u_prev, u_curr, u_next = u_curr, u_next, u_prev

        # Create visualization with reduced memory footprint
        fig, ax = plt.subplots(figsize=(10, 6))
        for n in time_snapshots:
            if n in solution_snapshots:
                ax.plot(x, solution_snapshots[n], label=f't = {n*dt:.3f}')

        ax.set_xlabel('Position x')
        ax.set_ylabel('Displacement u')
        ax.set_title('Wave Equation Solution (Memory Optimized)')
        ax.legend()
        ax.grid(True)

        # Convert plot to base64 with reduced DPI for memory
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)

        return {
            "solution_type": "finite_difference_optimized",
            "equation": "∂²u/∂t² = c² * ∂²u/∂x²",
            "parameters": {
                "L": L, "T": T, "c": c, "nx": nx, "nt": nt,
                "dx": dx, "dt": dt
            },
            "stability": c * dt / dx <= 1.0,
            "final_solution": solution_snapshots[nt-1].tolist() if nt-1 in solution_snapshots else u_curr.tolist(),
            "visualization": f"data:image/png;base64,{image_base64}",
            "method": "Explicit finite difference (memory optimized)",
            "memory_optimizations": {
                "max_nx": max_nx,
                "max_nt": max_nt,
                "snapshots_stored": len(solution_snapshots)
            }
        }

    def solve_laplace_equation_fd(self, L: float = 1.0, W: float = 1.0, nx: int = 50, ny: int = 50,
                                 boundary_conditions: Optional[Dict[str, str]] = None,
                                 max_iterations: int = 1000, tolerance: float = 1e-6) -> Dict[str, Any]:
        """
        Solve 2D Laplace equation using finite difference method with memory optimization

        ∇²u = ∂²u/∂x² + ∂²u/∂y² = 0

        Args:
            L: Length in x-direction
            W: Width in y-direction
            nx: Number of points in x-direction (limited for memory)
            ny: Number of points in y-direction (limited for memory)
            boundary_conditions: Boundary conditions for each edge
            max_iterations: Maximum number of iterations (limited for memory)
            tolerance: Convergence tolerance

        Returns:
            Dictionary with solution data and visualization
        """
        # Memory optimization: limit grid size and iterations
        max_nx = 100
        max_ny = 100
        max_iter_limit = 2000
        
        if nx > max_nx:
            logger.warning(f"Reducing nx from {nx} to {max_nx} for memory optimization")
            nx = max_nx
        
        if ny > max_ny:
            logger.warning(f"Reducing ny from {ny} to {max_ny} for memory optimization")
            ny = max_ny
            
        if max_iterations > max_iter_limit:
            logger.warning(f"Reducing max_iterations from {max_iterations} to {max_iter_limit} for memory optimization")
            max_iterations = max_iter_limit

        if boundary_conditions is None:
            boundary_conditions = {
                "left": "0", "right": "0", "bottom": "0", "top": "100"
            }

        # Create grid
        x = np.linspace(0, L, nx)
        y = np.linspace(0, W, ny)
        dx = L / (nx - 1)
        dy = W / (ny - 1)

        # Memory-efficient solution: use two arrays instead of storing all iterations
        u = np.zeros((ny, nx))
        u_new = np.zeros((ny, nx))

        # Set boundary conditions safely
        try:
            from sympy import sympify
            # Bottom boundary (y=0)
            u[0, :] = float(sympify(boundary_conditions.get("bottom", "0")).evalf())
            # Top boundary (y=W)
            u[-1, :] = float(sympify(boundary_conditions.get("top", "100")).evalf())
            # Left boundary (x=0)
            u[:, 0] = float(sympify(boundary_conditions.get("left", "0")).evalf())
            # Right boundary (x=L)
            u[:, -1] = float(sympify(boundary_conditions.get("right", "0")).evalf())
        except Exception as e:
            logger.warning(f"Error evaluating boundary conditions: {e}. Using defaults.")
            # Default boundary conditions
            u[0, :] = 0    # bottom
            u[-1, :] = 100 # top
            u[:, 0] = 0    # left
            u[:, -1] = 0   # right

        # Jacobi iterative method with memory optimization
        iteration = 0
        converged = False
        residual_history = []
        
        # Store residuals at intervals to avoid memory issues
        residual_check_interval = max(1, max_iterations // 100)

        while iteration < max_iterations and not converged:
            # Copy current solution
            u_new[:] = u[:]
            
            # Update interior points using Jacobi method
            for i in range(1, ny - 1):
                for j in range(1, nx - 1):
                    u_new[i, j] = 0.25 * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1])

            # Check convergence periodically to save computation
            if iteration % residual_check_interval == 0:
                residual = np.max(np.abs(u_new - u))
                residual_history.append(residual)
                
                if residual < tolerance:
                    converged = True

            # Update solution
            u, u_new = u_new, u
            iteration += 1

        # Create visualization with reduced memory footprint
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Contour plot with reduced levels for memory
        X, Y = np.meshgrid(x, y)
        contour = ax1.contourf(X, Y, u, levels=20, cmap='viridis')
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')
        ax1.set_title('Laplace Equation Solution (Memory Optimized)')
        plt.colorbar(contour, ax=ax1)

        # Convergence plot (only if we have residual history)
        if residual_history:
            ax2.semilogy(range(0, len(residual_history) * residual_check_interval, residual_check_interval), 
                        residual_history)
            ax2.set_xlabel('Iteration')
            ax2.set_ylabel('Residual')
            ax2.set_title('Convergence History')
            ax2.grid(True)
        else:
            ax2.text(0.5, 0.5, 'Convergence tracking\nnot available', 
                    ha='center', va='center', transform=ax2.transAxes)

        # Convert plot to base64 with reduced DPI for memory
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)

        return {
            "solution_type": "finite_difference_optimized",
            "equation": "∇²u = ∂²u/∂x² + ∂²u/∂y² = 0",
            "parameters": {
                "L": L, "W": W, "nx": nx, "ny": ny,
                "dx": dx, "dy": dy, "max_iterations": max_iterations, "tolerance": tolerance
            },
            "convergence": {
                "converged": converged,
                "iterations": iteration,
                "final_residual": residual_history[-1] if residual_history else None
            },
            "solution_matrix": u.tolist(),
            "visualization": f"data:image/png;base64,{image_base64}",
            "method": "Jacobi iterative finite difference (memory optimized)",
            "memory_optimizations": {
                "max_nx": max_nx,
                "max_ny": max_ny,
                "max_iterations": max_iter_limit,
                "residual_check_interval": residual_check_interval
            }
        }

    def solve_pde_symbolically(self, equation: str, variables: Optional[List[str]] = None,
                              boundary_conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Attempt symbolic solution of PDE using SymPy

        Args:
            equation: PDE as string (e.g., "diff(u(x,t), t) - alpha*diff(u(x,t), x, 2)")
            variables: List of variables
            boundary_conditions: Boundary conditions

        Returns:
            Dictionary with symbolic solution attempt
        """
        if variables is None:
            variables = ['x', 't']

        try:
            # Parse the equation
            parsed_eq = sp.sympify(equation)

            result = {
                "solution_type": "symbolic",
                "equation": equation,
                "variables": variables,
                "parsed_equation": str(parsed_eq),
                "attempted_solution": "Symbolic PDE solving is complex and often requires specific boundary conditions"
            }

            # Try some common PDE patterns
            if 'diff(u(x,t), t)' in equation and 'diff(u(x,t), x, 2)' in equation:
                result["recognized_as"] = "Heat equation"
                result["general_solution"] = "Requires separation of variables or specific boundary conditions"
            elif 'diff(u(x,t), t, 2)' in equation and 'diff(u(x,t), x, 2)' in equation:
                result["recognized_as"] = "Wave equation"
                result["general_solution"] = "d'Alembert formula or separation of variables"
            elif 'diff(u(x,y), x, 2)' in equation and 'diff(u(x,y), y, 2)' in equation:
                result["recognized_as"] = "Laplace equation"
                result["general_solution"] = "Harmonic functions, requires boundary conditions"

            return result

        except BiologyError as e:
            return {
                "solution_type": "symbolic",
                "equation": equation,
                "error": f"Could not parse equation: {str(e)}",
                "suggestion": "Try using finite difference methods for numerical solutions"
            }

    def get_pde_info(self) -> GetPdeInfoResult:
        """Get information about supported PDEs"""
        return {
            "supported_pdes": self.common_pdes,
            "numerical_methods": [
                "Finite Difference Method (FDM)",
                "Finite Element Method (FEM)",
                "Finite Volume Method (FVM)",
                "Boundary Element Method (BEM)"
            ],
            "implemented_methods": [
                "1D Heat Equation (FDM)",
                "1D Wave Equation (FDM)",
                "2D Laplace Equation (FDM)",
                "Symbolic PDE Analysis"
            ],
            "applications": [
                "Heat transfer and diffusion",
                "Wave propagation (acoustics, electromagnetism)",
                "Fluid dynamics (Navier-Stokes)",
                "Structural mechanics",
                "Electromagnetic field problems",
                "Quantum mechanics"
            ]
        }

    def analyze_pde_type(self, equation: str) -> AnalyzePdeTypeResult:
        """Analyze the type and properties of a PDE"""
        analysis = {
            "equation": equation,
            "classification": "Unknown",
            "order": "Unknown",
            "linearity": "Unknown",
            "homogeneity": "Unknown"
        }

        # Check for common PDE patterns
        if 'diff(u,' in equation:
            # Determine order
            if ', 2)' in equation:
                analysis["order"] = "Second order"
            elif ', 1)' in equation:
                analysis["order"] = "First order"
            else:
                analysis["order"] = "Higher order"

            # Determine type
            if 'diff(u(x,t), t)' in equation and 'diff(u(x,t), x, 2)' in equation:
                analysis["classification"] = "Parabolic (Heat equation)"
            elif 'diff(u(x,t), t, 2)' in equation and 'diff(u(x,t), x, 2)' in equation:
                analysis["classification"] = "Hyperbolic (Wave equation)"
            elif 'diff(u(x,y), x, 2)' in equation and 'diff(u(x,y), y, 2)' in equation:
                if 'diff(u(x,y), t)' not in equation:
                    analysis["classification"] = "Elliptic (Laplace/Poisson equation)"

            # Check linearity
            if '*' in equation or any(op in equation for op in ['sin', 'cos', 'exp', 'log']):
                analysis["linearity"] = "Nonlinear"
            else:
                analysis["linearity"] = "Linear"

        return analysis
