"""
Advanced Algebra Service
Servicio para álgebra avanzada: matrices, números complejos, polinomios
"""

import numpy as np
import sympy as sp
from typing import List, Dict, Union, Any
from app.exceptions.domain.mathematics import MathematicsError


class AdvancedAlgebraService:
    """Servicio para álgebra avanzada"""
    
    @staticmethod
    def matrix_determinant(matrix: List[List[float]]) -> float:
        """Calcula el determinante de una matriz"""
        try:
            A = np.array(matrix)
            if A.shape[0] != A.shape[1]:
                raise ValueError("Solo se puede calcular el determinante de una matriz cuadrada")
            return float(np.linalg.det(A))
        except MathematicsError as e:
            raise ValueError(f"Error calculando determinante: {str(e)}")
    
    @staticmethod
    def matrix_inverse(matrix: List[List[float]]) -> List[List[float]]:
        """Calcula la inversa de una matriz"""
        try:
            A = np.array(matrix)
            if A.shape[0] != A.shape[1]:
                raise ValueError("Solo se puede invertir una matriz cuadrada")
            return np.linalg.inv(A).tolist()
        except MathematicsError as e:
            raise ValueError(f"Error calculando inversa: {str(e)}")
    
    @staticmethod
    def matrix_eigenvalues(matrix: List[List[float]]) -> List[float]:
        """Calcula los eigenvalores de una matriz"""
        try:
            A = np.array(matrix)
            if A.shape[0] != A.shape[1]:
                raise ValueError("Solo se pueden calcular eigenvalores de una matriz cuadrada")
            eigenvals, _ = np.linalg.eig(A)
            return eigenvals.tolist()
        except MathematicsError as e:
            raise ValueError(f"Error calculando eigenvalores: {str(e)}")
    
    @staticmethod
    def matrix_eigenvectors(matrix: List[List[float]]) -> List[List[float]]:
        """Calcula los eigenvectores de una matriz"""
        try:
            A = np.array(matrix)
            if A.shape[0] != A.shape[1]:
                raise ValueError("Solo se pueden calcular eigenvectores de una matriz cuadrada")
            _, eigenvecs = np.linalg.eig(A)
            return eigenvecs.tolist()
        except MathematicsError as e:
            raise ValueError(f"Error calculando eigenvectores: {str(e)}")
    
    @staticmethod
    def complex_operations(real1: float, imag1: float, real2: float, imag2: float, operation: str) -> Dict[str, Any]:
        """Operaciones con números complejos"""
        try:
            z1 = complex(real1, imag1)
            z2 = complex(real2, imag2)
            
            if operation == "add":
                result = z1 + z2
            elif operation == "subtract":
                result = z1 - z2
            elif operation == "multiply":
                result = z1 * z2
            elif operation == "divide":
                if z2 == 0:
                    raise ValueError("División por cero")
                result = z1 / z2
            elif operation == "conjugate":
                result = z1.conjugate()
            elif operation == "modulus":
                result = abs(z1)
            elif operation == "argument":
                result = np.angle(z1)
            else:
                raise ValueError(f"Operación no soportada: {operation}")
            
            return {
                "operation": operation,
                "input": f"({real1} + {imag1}i) {operation} ({real2} + {imag2}i)",
                "result": str(result),
                "real": result.real if isinstance(result, complex) else result,
                "imaginary": result.imag if isinstance(result, complex) else 0,
                "modulus": abs(result) if isinstance(result, complex) else abs(result),
                "argument": np.angle(result) if isinstance(result, complex) else 0
            }
        except MathematicsError as e:
            raise ValueError(f"Error en operación con números complejos: {str(e)}")
    
    @staticmethod
    def polynomial_roots(coefficients: List[float]) -> List[Union[float, str]]:
        """Encuentra las raíces de un polinomio"""
        try:
            roots = np.roots(coefficients)
            result = []
            for root in roots:
                if np.isreal(root):
                    result.append(float(root.real))
                else:
                    result.append(f"{root.real:.4f} + {root.imag:.4f}i")
            return result
        except MathematicsError as e:
            raise ValueError(f"Error encontrando raíces: {str(e)}")
    
    @staticmethod
    def polynomial_expand(expression: str) -> str:
        """Expande una expresión polinomial"""
        try:
            poly = sp.sympify(expression)
            expanded = sp.expand(poly)
            return str(expanded)
        except MathematicsError as e:
            raise ValueError(f"Error expandiendo polinomio: {str(e)}")
    
    @staticmethod
    def solve_linear_system(coefficient_matrix: List[List[float]], constants: List[float]) -> List[float]:
        """Resuelve un sistema de ecuaciones lineales"""
        try:
            A = np.array(coefficient_matrix)
            b = np.array(constants)
            
            if A.shape[0] != len(b):
                raise ValueError("Dimensiones inconsistentes")
            
            solution = np.linalg.solve(A, b)
            return solution.tolist()
        except MathematicsError as e:
            raise ValueError(f"Error resolviendo sistema: {str(e)}")
    
    @staticmethod
    def gauss_elimination(coefficient_matrix: List[List[float]], constants: List[float]) -> List[float]:
        """Resuelve usando eliminación gaussiana"""
        try:
            A = np.array(coefficient_matrix, dtype=float)
            b = np.array(constants, dtype=float)
            
            n = len(b)
            
            # Crear matriz aumentada
            Ab = np.column_stack([A, b])
            
            # Eliminación hacia adelante
            for i in range(n):
                # Encontrar el pivote
                max_row = i
                for k in range(i + 1, n):
                    if abs(Ab[k][i]) > abs(Ab[max_row][i]):
                        max_row = k
                
                # Intercambiar filas
                Ab[i], Ab[max_row] = Ab[max_row].copy(), Ab[i].copy()
                
                # Eliminar columna
                for k in range(i + 1, n):
                    factor = Ab[k][i] / Ab[i][i]
                    for j in range(i, n + 1):
                        Ab[k][j] -= factor * Ab[i][j]
            
            # Sustitución hacia atrás
            x = np.zeros(n)
            for i in range(n - 1, -1, -1):
                x[i] = Ab[i][n]
                for j in range(i + 1, n):
                    x[i] -= Ab[i][j] * x[j]
                x[i] /= Ab[i][i]
            
            return x.tolist()
        except MathematicsError as e:
            raise ValueError(f"Error en eliminación gaussiana: {str(e)}")
    
    @staticmethod
    def get_examples() -> List[Dict]:
        """
        Devuelve ejemplos de operaciones de álgebra avanzada
        
        Returns:
            Lista de ejemplos
        """
        return [
            {
                "category": "matrices",
                "operation": "determinant",
                "description": "Cálculo del determinante de una matriz",
                "example": {
                    "matrix": [[1, 2], [3, 4]]
                }
            },
            {
                "category": "complex_numbers",
                "operation": "multiply",
                "description": "Multiplicación de números complejos",
                "example": {
                    "real1": 1, "imag1": 2,
                    "real2": 3, "imag2": 4
                }
            },
            {
                "category": "polynomials",
                "operation": "roots",
                "description": "Raíces de un polinomio",
                "example": {
                    "coefficients": [1, -5, 6]
                }
            },
            {
                "category": "linear_systems",
                "operation": "solve",
                "description": "Sistema de ecuaciones lineales",
                "example": {
                    "coefficient_matrix": [[2, 3], [1, -1]],
                    "constants": [7, 1]
                }
            }
        ]

    @staticmethod
    def power_series_expansion(function: str, variable: str = "z", center: str = "0", order: int = 6) -> Dict[str, Any]:
        """Expansión en series de potencias de una función"""
        try:
            import sympy as sp
            
            # Convertir strings a símbolos de SymPy
            var = sp.Symbol(variable)
            center_point = sp.sympify(center)
            expr = sp.sympify(function)
            
            # Calcular la serie de Taylor/Laurent
            series = sp.series(expr, var, center_point, order)
            
            return {
                "status": "success",
                "function": function,
                "variable": variable,
                "center": center,
                "order": order,
                "series": str(series),
                "latex": sp.latex(series),
                "coefficients": [str(coeff) for coeff in sp.Poly(series.removeO(), var).all_coeffs()]
            }
        except MathematicsError as e:
            return {"status": "failed", "error": str(e)}

    @staticmethod
    def residue_calculation(function: str, pole: str, variable: str = "z") -> Dict[str, Any]:
        """Cálculo de residuos en polos"""
        try:
            import sympy as sp
            
            var = sp.Symbol(variable)
            pole_point = sp.sympify(pole)
            expr = sp.sympify(function)
            
            # Calcular el residuo usando SymPy
            residue = sp.residue(expr, var, pole_point)
            
            return {
                "status": "success",
                "function": function,
                "pole": pole,
                "variable": variable,
                "residue": str(residue),
                "latex": sp.latex(residue)
            }
        except MathematicsError as e:
            return {"status": "failed", "error": str(e)}

    @staticmethod
    def contour_integral(function: str, contour_type: str = "circle", center: str = "0", 
                        radius: str = "1", variable: str = "z") -> Dict[str, Any]:
        """Integración de contorno"""
        try:
            import sympy as sp
            
            var = sp.Symbol(variable)
            expr = sp.sympify(function)
            center_point = sp.sympify(center)
            radius_val = sp.sympify(radius)
            
            if contour_type == "circle":
                # Para contornos circulares, usar el teorema de residuos
                # Encontrar singularidades dentro del contorno
                singularities = sp.solve(sp.denom(expr), var)
                total_residue = 0
                
                for sing in singularities:
                    # Verificar si la singularidad está dentro del círculo
                    distance = abs(complex(sing.evalf()) - complex(center_point.evalf()))
                    if distance < float(radius_val.evalf()):
                        residue = sp.residue(expr, var, sing)
                        total_residue += residue
                
                integral_value = 2 * sp.pi * sp.I * total_residue
                
                return {
                    "status": "success",
                    "function": function,
                    "contour_type": contour_type,
                    "center": center,
                    "radius": radius,
                    "integral": str(integral_value),
                    "latex": sp.latex(integral_value),
                    "singularities": [str(s) for s in singularities]
                }
            else:
                return {"status": "failed", "error": f"Contour type '{contour_type}' not supported"}
                
        except MathematicsError as e:
            return {"status": "failed", "error": str(e)}

    @staticmethod
    def bessel_function(order: float, argument: str, function_type: str = "J") -> Dict[str, Any]:
        """Funciones de Bessel"""
        try:
            import sympy as sp
            
            arg = sp.sympify(argument)
            
            if function_type == "J":
                bessel_func = sp.besselj(order, arg)
            elif function_type == "Y":
                bessel_func = sp.bessely(order, arg)
            elif function_type == "I":
                bessel_func = sp.besseli(order, arg)
            elif function_type == "K":
                bessel_func = sp.besselk(order, arg)
            else:
                return {"status": "failed", "error": f"Bessel function type '{function_type}' not supported"}
            
            return {
                "status": "success",
                "order": order,
                "argument": argument,
                "function_type": function_type,
                "result": str(bessel_func),
                "latex": sp.latex(bessel_func),
                "numerical_value": str(bessel_func.evalf()) if bessel_func.is_number else None
            }
        except MathematicsError as e:
            return {"status": "failed", "error": str(e)}

    @staticmethod
    def legendre_polynomial(degree: int, argument: str = "x") -> Dict[str, Any]:
        """Polinomios de Legendre"""
        try:
            import sympy as sp
            
            var = sp.Symbol(argument)
            legendre_poly = sp.legendre(degree, var)
            
            return {
                "status": "success",
                "degree": degree,
                "argument": argument,
                "polynomial": str(legendre_poly),
                "latex": sp.latex(legendre_poly),
                "expanded": str(sp.expand(legendre_poly)),
                "roots": [str(root) for root in sp.solve(legendre_poly, var)]
            }
        except MathematicsError as e:
            return {"status": "failed", "error": str(e)}

    @staticmethod
    def hermite_polynomial(degree: int, argument: str = "x") -> Dict[str, Any]:
        """Polinomios de Hermite"""
        try:
            import sympy as sp
            
            var = sp.Symbol(argument)
            hermite_poly = sp.hermite(degree, var)
            
            return {
                "status": "success",
                "degree": degree,
                "argument": argument,
                "polynomial": str(hermite_poly),
                "latex": sp.latex(hermite_poly),
                "expanded": str(sp.expand(hermite_poly)),
                "derivative": str(sp.diff(hermite_poly, var))
            }
        except MathematicsError as e:
            return {"status": "failed", "error": str(e)}

    @staticmethod
    def series_convergence_test(series: str, variable: str = "n", test_type: str = "ratio") -> Dict[str, Any]:
        """Pruebas de convergencia de series"""
        try:
            import sympy as sp
            
            var = sp.Symbol(variable)
            expr = sp.sympify(series)
            
            if test_type == "ratio":
                # Prueba de la razón
                next_term = expr.subs(var, var + 1)
                ratio = sp.simplify(next_term / expr)
                limit_ratio = sp.limit(sp.Abs(ratio), var, sp.oo)
                
                if limit_ratio < 1:
                    convergence = "convergent"
                elif limit_ratio > 1:
                    convergence = "divergent"
                else:
                    convergence = "inconclusive"
                    
            elif test_type == "root":
                # Prueba de la raíz
                root_test = sp.limit(sp.Abs(expr)**(1/var), var, sp.oo)
                
                if root_test < 1:
                    convergence = "convergent"
                elif root_test > 1:
                    convergence = "divergent"
                else:
                    convergence = "inconclusive"
                    
            else:
                return {"status": "failed", "error": f"Test type '{test_type}' not supported"}
            
            return {
                "status": "success",
                "series": series,
                "variable": variable,
                "test_type": test_type,
                "convergence": convergence,
                "limit_value": str(limit_ratio if test_type == "ratio" else root_test)
            }
        except MathematicsError as e:
            return {"status": "failed", "error": str(e)}

    @staticmethod
    def analytic_continuation(function: str, original_domain: str, extension_domain: str, 
                            variable: str = "z") -> Dict[str, Any]:
        """Continuación analítica de funciones"""
        try:
            import sympy as sp
            
            var = sp.Symbol(variable)
            expr = sp.sympify(function)
            
            # Expansión en serie de Taylor alrededor de diferentes puntos
            expansions = {}
            points = [0, 1, -1, sp.I, -sp.I]
            
            for point in points:
                try:
                    series_exp = sp.series(expr, var, point, 6)
                    expansions[str(point)] = str(series_exp)
                except MathematicsError:
                    expansions[str(point)] = "expansion_failed"
            
            return {
                "status": "success",
                "function": function,
                "variable": variable,
                "original_domain": original_domain,
                "extension_domain": extension_domain,
                "expansions": expansions,
                "method": "series_expansion"
            }
        except MathematicsError as e:
            return {"status": "failed", "error": str(e)}

    @staticmethod
    def get_series_examples() -> Dict[str, Any]:
        """Ejemplos de series complejas"""
        try:
            import sympy as sp
            
            x = sp.Symbol('x')
            z = sp.Symbol('z')
            
            examples = {
                "geometric_series": {
                    "function": "1/(1-z)",
                    "series": str(sp.series(1/(1-z), z, 0, 6)),
                    "convergence": "|z| < 1",
                    "type": "power_series"
                },
                "exponential": {
                    "function": "exp(z)",
                    "series": str(sp.series(sp.exp(z), z, 0, 6)),
                    "convergence": "all z",
                    "type": "entire_function"
                },
                "logarithm": {
                    "function": "log(1+z)",
                    "series": str(sp.series(sp.log(1+z), z, 0, 6)),
                    "convergence": "|z| < 1",
                    "type": "branch_cut"
                },
                "sine": {
                    "function": "sin(z)",
                    "series": str(sp.series(sp.sin(z), z, 0, 6)),
                    "convergence": "all z",
                    "type": "entire_function"
                }
            }
            
            return {
                "status": "success",
                "examples": examples,
                "count": len(examples)
            }
        except MathematicsError as e:
            return {"status": "failed", "error": str(e)}

    @staticmethod
    def power_series_expansion(function: str, variable: str = "z", center: str = "0", order: int = 6) -> Dict[str, Any]:
        """Expansión en series de potencias de una función"""
        try:
            import sympy as sp
            
            # Convertir strings a símbolos de SymPy
            var = sp.Symbol(variable)
            center_point = sp.sympify(center)
            expr = sp.sympify(function)
            
            # Calcular la serie de Taylor/Laurent
            series = sp.series(expr, var, center_point, order)
            
            return {
                "status": "success",
                "function": function,
                "variable": variable,
                "center": center,
                "order": order,
                "series": str(series),
                "latex": sp.latex(series),
                "coefficients": [str(coeff) for coeff in sp.Poly(series.removeO(), var).all_coeffs()]
            }
        except MathematicsError as e:
            return {"status": "failed", "error": str(e)}






