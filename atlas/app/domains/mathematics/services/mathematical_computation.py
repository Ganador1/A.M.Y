"""
Mathematical Computation Service
Provides advanced mathematical computation capabilities
"""

import numpy as np
import sympy as sp
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
from scipy import integrate, optimize, linalg
from scipy.special import factorial, gamma, beta
import matplotlib.pyplot as plt
from app.exceptions.domain.mathematics import MathematicsError

logger = logging.getLogger(__name__)

class SymbolicMath:
    """Symbolic mathematics operations"""
    
    @staticmethod
    def solve_equation(equation_str: str, variable: str = "x") -> List[str]:
        """Solve symbolic equation"""
        try:
            x = sp.Symbol(variable)
            eq = sp.sympify(equation_str)
            solutions = sp.solve(eq, x)
            return [str(sol) for sol in solutions]
        except MathematicsError as e:
            logger.error(f"Error solving equation: {e}")
            return []
    
    @staticmethod
    def differentiate(expression_str: str, variable: str = "x", order: int = 1) -> str:
        """Calculate derivative"""
        try:
            x = sp.Symbol(variable)
            expr = sp.sympify(expression_str)
            derivative = sp.diff(expr, x, order)
            return str(derivative)
        except MathematicsError as e:
            logger.error(f"Error calculating derivative: {e}")
            return ""
    
    @staticmethod
    def integrate_symbolic(expression_str: str, variable: str = "x", 
                          limits: Optional[List[Union[str, float]]] = None) -> str:
        """Calculate symbolic integral"""
        try:
            x = sp.Symbol(variable)
            expr = sp.sympify(expression_str)
            
            if limits:
                if len(limits) == 2:
                    result = sp.integrate(expr, (x, limits[0], limits[1]))
                else:
                    result = sp.integrate(expr, x)
            else:
                result = sp.integrate(expr, x)
            
            return str(result)
        except MathematicsError as e:
            logger.error(f"Error calculating integral: {e}")
            return ""
    
    @staticmethod
    def series_expansion(expression_str: str, variable: str = "x", 
                        point: Union[str, float] = 0, order: int = 5) -> str:
        """Calculate series expansion"""
        try:
            x = sp.Symbol(variable)
            expr = sp.sympify(expression_str)
            series = sp.series(expr, x, point, order + 1)
            return str(series.removeO())
        except MathematicsError as e:
            logger.error(f"Error calculating series expansion: {e}")
            return ""

class NumericalMath:
    """Numerical mathematics operations"""
    
    @staticmethod
    def numerical_integration(func, limits: List[float], method: str = "quad") -> Dict[str, Any]:
        """Perform numerical integration"""
        try:
            if method == "quad":
                result, error = integrate.quad(func, limits[0], limits[1])
                return {"result": result, "error": error, "method": method}
            elif method == "trapz":
                x = np.linspace(limits[0], limits[1], 1000)
                y = [func(xi) for xi in x]
                result = integrate.trapz(y, x)
                return {"result": result, "error": None, "method": method}
            else:
                return {"error": f"Unknown integration method: {method}"}
        except MathematicsError as e:
            logger.error(f"Error in numerical integration: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def find_roots(func, initial_guess: float, method: str = "brentq",
                  bounds: Optional[List[float]] = None) -> Dict[str, Any]:
        """Find roots of a function"""
        try:
            if method == "brentq" and bounds:
                root = optimize.brentq(func, bounds[0], bounds[1])
            elif method == "newton":
                root = optimize.newton(func, initial_guess)
            else:
                root = optimize.fsolve(func, initial_guess)[0]
            
            return {"root": root, "method": method, "success": True}
        except MathematicsError as e:
            logger.error(f"Error finding roots: {e}")
            return {"error": str(e), "success": False}
    
    @staticmethod
    def optimize_function(func, initial_guess: List[float], 
                         bounds: Optional[List[List[float]]] = None,
                         method: str = "minimize") -> Dict[str, Any]:
        """Optimize a function"""
        try:
            if bounds:
                result = optimize.minimize(func, initial_guess, bounds=bounds, method="L-BFGS-B")
            else:
                result = optimize.minimize(func, initial_guess)
            
            return {
                "optimal_point": result.x.tolist(),
                "optimal_value": result.fun,
                "success": result.success,
                "message": result.message,
                "iterations": result.nit
            }
        except MathematicsError as e:
            logger.error(f"Error in optimization: {e}")
            return {"error": str(e), "success": False}

class LinearAlgebra:
    """Linear algebra operations"""
    
    @staticmethod
    def matrix_operations(matrix_a: List[List[float]], 
                         matrix_b: Optional[List[List[float]]] = None,
                         operation: str = "eigenvalues") -> Dict[str, Any]:
        """Perform matrix operations"""
        try:
            A = np.array(matrix_a)
            result = {"operation": operation}
            
            if operation == "eigenvalues":
                eigenvals = linalg.eigvals(A)
                result["eigenvalues"] = eigenvals.tolist()
                
            elif operation == "eigenvectors":
                eigenvals, eigenvecs = linalg.eig(A)
                result["eigenvalues"] = eigenvals.tolist()
                result["eigenvectors"] = eigenvecs.tolist()
                
            elif operation == "determinant":
                det = linalg.det(A)
                result["determinant"] = det
                
            elif operation == "inverse":
                inv = linalg.inv(A)
                result["inverse"] = inv.tolist()
                
            elif operation == "svd":
                U, s, Vt = linalg.svd(A)
                result["U"] = U.tolist()
                result["singular_values"] = s.tolist()
                result["Vt"] = Vt.tolist()
                
            elif operation == "multiply" and matrix_b is not None:
                B = np.array(matrix_b)
                product = np.dot(A, B)
                result["result"] = product.tolist()
                
            else:
                result["error"] = f"Unknown operation or missing matrix_b: {operation}"
                
            result["success"] = True
            return result
            
        except MathematicsError as e:
            logger.error(f"Error in matrix operations: {e}")
            return {"error": str(e), "success": False}
    
    @staticmethod
    def solve_linear_system(coefficient_matrix: List[List[float]], 
                           constants: List[float]) -> Dict[str, Any]:
        """Solve system of linear equations"""
        try:
            A = np.array(coefficient_matrix)
            b = np.array(constants)
            
            solution = linalg.solve(A, b)
            
            return {
                "solution": solution.tolist(),
                "residual": np.linalg.norm(A @ solution - b),
                "condition_number": np.linalg.cond(A),
                "success": True
            }
        except MathematicsError as e:
            logger.error(f"Error solving linear system: {e}")
            return {"error": str(e), "success": False}

class SpecialFunctions:
    """Special mathematical functions"""
    
    @staticmethod
    def gamma_function(x: float) -> float:
        """Calculate gamma function"""
        return gamma(x)
    
    @staticmethod
    def beta_function(a: float, b: float) -> float:
        """Calculate beta function"""
        return beta(a, b)
    
    @staticmethod
    def factorial_function(n: int) -> float:
        """Calculate factorial"""
        return factorial(n, exact=False)
    
    @staticmethod
    def bessel_functions(x: float, n: int = 0, kind: str = "first") -> float:
        """Calculate Bessel functions"""
        try:
            from scipy.special import jv, yv, iv, kv
            
            if kind == "first":
                return jv(n, x)
            elif kind == "second":
                return yv(n, x)
            elif kind == "modified_first":
                return iv(n, x)
            elif kind == "modified_second":
                return kv(n, x)
            else:
                raise ValueError(f"Unknown Bessel function kind: {kind}")
        except MathematicsError as e:
            logger.error(f"Error calculating Bessel function: {e}")
            return 0.0

class StatisticalMath:
    """Statistical mathematics operations"""
    
    @staticmethod
    def descriptive_statistics(data: List[float]) -> Dict[str, float]:
        """Calculate descriptive statistics"""
        data_array = np.array(data)
        
        return {
            "mean": np.mean(data_array),
            "median": np.median(data_array),
            "std_dev": np.std(data_array),
            "variance": np.var(data_array),
            "min": np.min(data_array),
            "max": np.max(data_array),
            "range": np.max(data_array) - np.min(data_array),
            "skewness": float(np.mean(((data_array - np.mean(data_array)) / np.std(data_array)) ** 3)),
            "kurtosis": float(np.mean(((data_array - np.mean(data_array)) / np.std(data_array)) ** 4) - 3)
        }
    
    @staticmethod
    def correlation_analysis(x_data: List[float], y_data: List[float]) -> Dict[str, Any]:
        """Perform correlation analysis"""
        try:
            x = np.array(x_data)
            y = np.array(y_data)
            
            correlation = np.corrcoef(x, y)[0, 1]
            
            # Linear regression
            slope, intercept = np.polyfit(x, y, 1)
            
            # R-squared
            y_pred = slope * x + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)
            
            return {
                "correlation": correlation,
                "slope": slope,
                "intercept": intercept,
                "r_squared": r_squared,
                "equation": f"y = {slope:.4f}x + {intercept:.4f}",
                "success": True
            }
        except MathematicsError as e:
            logger.error(f"Error in correlation analysis: {e}")
            return {"error": str(e), "success": False}

class MathematicalComputationService:
    """Main service for mathematical computations"""
    
    def __init__(self):
        self.symbolic = SymbolicMath()
        self.numerical = NumericalMath()
        self.linear_algebra = LinearAlgebra()
        self.special_functions = SpecialFunctions()
        self.statistics = StatisticalMath()
        logger.info("Mathematical Computation Service initialized")
    
    def compute(self, computation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform mathematical computation"""
        try:
            start_time = datetime.now()
            result = {
                "computation_type": computation_type,
                "timestamp": start_time.isoformat()
            }
            
            if computation_type == "solve_equation":
                solutions = self.symbolic.solve_equation(
                    parameters["equation"], 
                    parameters.get("variable", "x")
                )
                result["solutions"] = solutions
                
            elif computation_type == "differentiate":
                derivative = self.symbolic.differentiate(
                    parameters["expression"],
                    parameters.get("variable", "x"),
                    parameters.get("order", 1)
                )
                result["derivative"] = derivative
                
            elif computation_type == "integrate":
                integral = self.symbolic.integrate_symbolic(
                    parameters["expression"],
                    parameters.get("variable", "x"),
                    parameters.get("limits")
                )
                result["integral"] = integral
                
            elif computation_type == "matrix_eigenvalues":
                matrix_result = self.linear_algebra.matrix_operations(
                    parameters["matrix"], operation="eigenvalues"
                )
                result.update(matrix_result)
                
            elif computation_type == "solve_linear_system":
                system_result = self.linear_algebra.solve_linear_system(
                    parameters["coefficient_matrix"],
                    parameters["constants"]
                )
                result.update(system_result)
                
            elif computation_type == "descriptive_stats":
                stats_result = self.statistics.descriptive_statistics(
                    parameters["data"]
                )
                result["statistics"] = stats_result
                
            elif computation_type == "correlation":
                corr_result = self.statistics.correlation_analysis(
                    parameters["x_data"],
                    parameters["y_data"]
                )
                result.update(corr_result)
                
            else:
                result["error"] = f"Unknown computation type: {computation_type}"
                return result
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            result["processing_time"] = processing_time
            result["success"] = True
            
            return result
            
        except MathematicsError as e:
            logger.error(f"Error in mathematical computation: {e}")
            return {
                "computation_type": computation_type,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def batch_compute(self, computations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform batch computations"""
        results = []
        
        for computation in computations:
            comp_type = computation.get("type")
            parameters = computation.get("parameters", {})
            
            if comp_type:
                result = self.compute(comp_type, parameters)
                results.append(result)
            else:
                results.append({
                    "error": "Missing computation type",
                    "success": False
                })
        
        return results
    
    def create_function(self, expression_str: str, variables: List[str]) -> callable:
        """Create a callable function from symbolic expression"""
        try:
            symbols = [sp.Symbol(var) for var in variables]
            expr = sp.sympify(expression_str)
            func = sp.lambdify(symbols, expr, "numpy")
            return func
        except MathematicsError as e:
            logger.error(f"Error creating function: {e}")
            return lambda *args: 0.0

# Global service instance
mathematical_computation_service = MathematicalComputationService()

def compute_math(computation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Perform mathematical computation"""
    return mathematical_computation_service.compute(computation_type, parameters)

def solve_equation(equation: str, variable: str = "x") -> List[str]:
    """Solve a symbolic equation"""
    return SymbolicMath.solve_equation(equation, variable)

def differentiate(expression: str, variable: str = "x", order: int = 1) -> str:
    """Calculate derivative"""
    return SymbolicMath.differentiate(expression, variable, order)
