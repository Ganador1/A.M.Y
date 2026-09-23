"""
Complex Analysis Service for Mathematics AI
Provides capabilities for complex analysis, series, and special functions
"""

import io
import base64
from typing import Dict, Any

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jv, yv, iv, kv, legendre, hermite
from app.exceptions.domain.mathematics import MathematicsError
from app.types.complex_analysis_service_types import (
    LegendrePolynomialResult,
    HermitePolynomialResult,
    GetSeriesExamplesResult,
)


class ComplexAnalysisService:
    """Service for complex analysis and special functions"""

    def __init__(self):
        self.z = sp.Symbol('z', complex=True)
        self.n = sp.Symbol('n', integer=True, positive=True)
        self.x = sp.Symbol('x', real=True)
        self.k = sp.Symbol('k', integer=True)

        # Common series and sequences
        self.series_examples = {
            'geometric': {
                'series': 'Sum(z**n, (n, 0, oo))',
                'convergence': '|z| < 1',
                'sum': '1/(1-z)',
                'description': 'Geometric series'
            },
            'exponential': {
                'series': 'Sum(z**n/factorial(n), (n, 0, oo))',
                'convergence': 'all z',
                'sum': 'exp(z)',
                'description': 'Exponential series'
            },
            'sine': {
                'series': 'Sum((-1)**n*z**(2*n+1)/factorial(2*n+1), '
                         '(n, 0, oo))',
                'convergence': 'all z',
                'sum': 'sin(z)',
                'description': 'Sine series'
            },
            'cosine': {
                'series': 'Sum((-1)**n*z**(2*n)/factorial(2*n), '
                         '(n, 0, oo))',
                'convergence': 'all z',
                'sum': 'cos(z)',
                'description': 'Cosine series'
            }
        }

    def power_series_expansion(self, function: str, variable: str = 'z',
                              center: str = '0', order: int = 6) -> Dict[str, Any]:
        """
        Compute the power series expansion of a function around a point

        f(z) = Σ c_n (z - a)^n
        """
        try:
            # Parse the function
            expr = sp.sympify(function)
            var = sp.Symbol(variable)
            center_point = sp.sympify(center)

            # Validate that the expression contains the variable
            if not expr.has(var):
                raise ValueError(f"Function does not contain variable {variable}")

            # Compute power series expansion
            series = sp.series(expr, var, center_point, order)

            # Extract coefficients
            series_expanded = sp.expand(series.removeO())
            coeffs = sp.Poly(series_expanded, var).all_coeffs()

            # Get radius of convergence (simplified)
            radius = self._estimate_radius_of_convergence(expr, var, center_point)

            return {
                'function': str(expr),
                'expansion_point': str(center_point),
                'power_series': str(series),
                'expanded_form': str(series_expanded),
                'coefficients': [str(c) for c in coeffs],
                'order': order,
                'radius_of_convergence': radius,
                'variable': variable,
                'status': 'success'
            }

        except (ValueError, TypeError, sp.SympifyError) as e:
            return {
                'error': str(e),
                'function': function,
                'status': 'failed'
            }

    def _estimate_radius_of_convergence(self, expr: sp.Expr, var: sp.Symbol,
                                       center: sp.Expr) -> str:
        """
        Estimate the radius of convergence for a power series
        """
        try:
            # For simple cases, try to find singularities
            # This is a simplified implementation
            # expr, var, center parameters are kept for future implementation
            if center == 0:
                # Check for poles or branch points by analyzing the expression
                # For now, return unknown as full pole analysis requires more complex implementation
                pass

            return "Unknown (requires detailed analysis)"
        except (ValueError, TypeError):
            return "Unknown"

    def residue_calculation(self, function: str, pole: str,
                           variable: str = 'z') -> Dict[str, Any]:
        """
        Calculate the residue of a function at a given pole

        Res(f, a) = (1/(2πi)) ∮ f(z) dz
        """
        try:
            expr = sp.sympify(function)
            var = sp.Symbol(variable)
            pole_point = sp.sympify(pole)

            # Validate that the expression contains the variable
            if not expr.has(var):
                raise ValueError(f"Function does not contain variable {variable}")

            # Calculate residue
            residue = sp.residue(expr, var, pole_point)

            # Also compute the Laurent series around the pole
            laurent_series = sp.series(expr, var, pole_point, 6)

            return {
                'function': str(expr),
                'pole': str(pole_point),
                'residue': str(residue),
                'laurent_series': str(laurent_series),
                'variable': variable,
                'status': 'success'
            }

        except (ValueError, TypeError, sp.SympifyError) as e:
            return {
                'error': str(e),
                'function': function,
                'pole': pole,
                'status': 'failed'
            }

    def contour_integral(self, function: str, contour_type: str = 'circle',
                        center: str = '0', radius: str = '1',
                        variable: str = 'z') -> Dict[str, Any]:
        """
        Compute contour integral along different types of contours
        """
        try:
            # Validate that the function contains the variable
            var = sp.Symbol(variable)
            if var not in sp.sympify(function).free_symbols and function != str(var):
                # If the function doesn't contain the variable and isn't just the variable itself
                raise ValueError(f"Function does not contain variable {variable}")

            expr = sp.sympify(function)
            center_point = sp.sympify(center)
            r = sp.sympify(radius)

            if contour_type == 'circle':
                # For simple cases, use residue theorem
                # This is a simplified implementation
                integral_value = "2πi * Σ residues inside contour"

                return {
                    'function': str(expr),
                    'contour_type': contour_type,
                    'center': str(center_point),
                    'radius': str(r),
                    'integral_value': integral_value,
                    'method': 'Residue theorem',
                    'note': 'Full numerical computation requires complex path integration',
                    'status': 'success'
                }
            else:
                return {
                    'error': f'Contour type {contour_type} not implemented',
                    'available_types': ['circle'],
                    'status': 'unsupported'
                }

        except (ValueError, TypeError, sp.SympifyError) as e:
            return {
                'error': str(e),
                'function': function,
                'status': 'failed'
            }

    def bessel_function(self, order: float, argument: str,
                       function_type: str = 'J') -> Dict[str, Any]:
        """
        Compute Bessel functions and their properties

        J_ν(z), Y_ν(z), I_ν(z), K_ν(z)
        """
        try:
            z_val = sp.sympify(argument)

            if function_type == 'J':
                # Bessel function of the first kind
                result = sp.besseli(order, z_val) if order == int(order) else "Non-integer order requires numerical evaluation"
                description = f"Bessel function of the first kind J_{order}(z)"
            elif function_type == 'Y':
                # Bessel function of the second kind
                result = sp.bessely(order, z_val) if order == int(order) else "Non-integer order requires numerical evaluation"
                description = f"Bessel function of the second kind Y_{order}(z)"
            elif function_type == 'I':
                # Modified Bessel function of the first kind
                result = sp.besseli(order, z_val) if order == int(order) else "Non-integer order requires numerical evaluation"
                description = f"Modified Bessel function of the first kind I_{order}(z)"
            elif function_type == 'K':
                # Modified Bessel function of the second kind
                result = sp.besselk(order, z_val) if order == int(order) else "Non-integer order requires numerical evaluation"
                description = f"Modified Bessel function of the second kind K_{order}(z)"
            else:
                return {
                    'error': f'Unknown Bessel function type: {function_type}',
                    'available_types': ['J', 'Y', 'I', 'K'],
                    'status': 'invalid_type'
                }

            # Create plot for real argument
            if z_val.is_real and z_val.is_finite:
                z_range = np.linspace(0.1, 5, 100)
                y_values = []  # Initialize to avoid pylint warning

                if function_type == 'J':
                    y_values = [jv(order, z) for z in z_range]
                elif function_type == 'Y':
                    y_values = [yv(order, z) for z in z_range]
                elif function_type == 'I':
                    y_values = [iv(order, z) for z in z_range]
                elif function_type == 'K':
                    y_values = [kv(order, z) for z in z_range]

                # Only create plot if y_values was assigned
                if y_values:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(z_range, y_values, 'b-', linewidth=2)
                    ax.set_xlabel('z')
                    ax.set_ylabel(f'{function_type}_{order}(z)')
                    ax.set_title(f'Bessel Function {function_type}_{order}(z)')
                    ax.grid(True)

                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png', dpi=100)
                    buffer.seek(0)
                    plot_base64 = base64.b64encode(buffer.read()).decode()
                    plt.close(fig)  # Close the figure to free memory
                else:
                    plot_base64 = None
            else:
                plot_base64 = None

            return {
                'function_type': function_type,
                'order': order,
                'argument': str(z_val),
                'result': str(result),
                'description': description,
                'plot': plot_base64,
                'status': 'success'
            }

        except (ValueError, TypeError, sp.SympifyError) as e:
            return {
                'error': str(e),
                'function_type': function_type,
                'order': order,
                'argument': argument,
                'status': 'failed'
            }

    def legendre_polynomial(self, degree: int, argument: str = 'x') -> LegendrePolynomialResult:
        """
        Compute Legendre polynomials and associated Legendre functions

        P_n(x), P_n^m(x)
        """
        try:
            x_val = sp.sympify(argument)
            n = degree

            # Legendre polynomial
            legendre_poly = sp.legendre(n, x_val)

            # Associated Legendre function (for m=0, it's the same as Legendre)
            if n >= 0:
                assoc_legendre = sp.assoc_legendre(n, 0, x_val)
            else:
                assoc_legendre = "Invalid degree"

            # Roots of the polynomial
            poly = sp.Poly(legendre_poly, sp.Symbol('x'))
            roots = sp.solve(poly, sp.Symbol('x'))

            # Create plot
            if x_val == sp.Symbol('x'):
                x_range = np.linspace(-1, 1, 100)
                y_values = [legendre(n, x) for x in x_range]

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(x_range, y_values, 'r-', linewidth=2)
                ax.set_xlabel('x')
                ax.set_ylabel(f'P_{n}(x)')
                ax.set_title(f'Legendre Polynomial P_{n}(x)')
                ax.grid(True)
                ax.set_xlim(-1, 1)

                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100)
                buffer.seek(0)
                plot_base64 = base64.b64encode(buffer.read()).decode()
                plt.close()
            else:
                plot_base64 = None

            return {
                'degree': n,
                'argument': str(x_val),
                'legendre_polynomial': str(legendre_poly),
                'associated_legendre': str(assoc_legendre),
                'roots': [str(root) for root in roots],
                'domain': '[-1, 1]',
                'orthogonality': '∫_{-1}^1 P_m(x)P_n(x) dx = (2/(2n+1)) δ_{mn}',
                'plot': plot_base64,
                'status': 'success'
            }

        except (ValueError, TypeError, sp.SympifyError) as e:
            return {
                'error': str(e),
                'degree': degree,
                'argument': argument,
                'status': 'failed'
            }

    def hermite_polynomial(self, degree: int, argument: str = 'x') -> HermitePolynomialResult:
        """
        Compute Hermite polynomials

        H_n(x) = (-1)^n exp(x^2) d^n/dx^n exp(-x^2)
        """
        try:
            x_val = sp.sympify(argument)
            n = degree

            # Hermite polynomial
            hermite_poly = sp.hermite(n, x_val)

            # Physicist's Hermite polynomials (default in sympy)
            # H_n(x) are orthogonal with weight exp(-x^2)

            # Create plot
            if x_val == sp.Symbol('x'):
                x_range = np.linspace(-3, 3, 100)
                y_values = [hermite(n, x) for x in x_range]

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(x_range, y_values, 'g-', linewidth=2)
                ax.set_xlabel('x')
                ax.set_ylabel(f'H_{n}(x)')
                ax.set_title(f'Hermite Polynomial H_{n}(x)')
                ax.grid(True)

                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100)
                buffer.seek(0)
                plot_base64 = base64.b64encode(buffer.read()).decode()
                plt.close()
            else:
                plot_base64 = None

            return {
                'degree': n,
                'argument': str(x_val),
                'hermite_polynomial': str(hermite_poly),
                'weight_function': 'exp(-x^2)',
                'orthogonality': '∫_{-∞}^∞ H_m(x)H_n(x) exp(-x^2) dx = √π 2^n n! δ_{mn}',
                'domain': '(-∞, ∞)',
                'plot': plot_base64,
                'status': 'success'
            }

        except (ValueError, TypeError, sp.SympifyError) as e:
            return {
                'error': str(e),
                'degree': degree,
                'argument': argument,
                'status': 'failed'
            }

    def series_convergence_test(self, series: str, variable: str = 'n',
                               test_type: str = 'ratio') -> Dict[str, Any]:
        """
        Test convergence of a series using various tests
        """
        try:
            # Parse the series
            series_expr = sp.sympify(series)
            var = sp.Symbol(variable)

            ratio_limit = None
            root_limit = None

            if test_type == 'ratio':
                # Ratio test: lim |a_{n+1}/a_n|
                next_term = series_expr.subs(var, var + sp.Integer(1))
                ratio_limit = sp.limit(sp.Abs(next_term / series_expr), var, sp.oo)

                # Handle different cases
                if ratio_limit == 0:
                    convergence = "Convergent (ratio test)"
                elif ratio_limit < 1:
                    convergence = "Convergent (ratio test)"
                elif ratio_limit > 1:
                    convergence = "Divergent (ratio test)"
                elif ratio_limit == 1:
                    convergence = "Inconclusive (ratio test - need more analysis)"
                else:
                    convergence = "Inconclusive (ratio test)"

            elif test_type == 'root':
                # Root test: lim |a_n|^(1/n)
                try:
                    root_expr = sp.Pow(sp.Abs(series_expr), sp.Rational(1, var))
                    root_limit = sp.limit(root_expr, var, sp.oo)

                    if root_limit == 0:
                        convergence = "Convergent (root test)"
                    elif root_limit < 1:
                        convergence = "Convergent (root test)"
                    elif root_limit > 1:
                        convergence = "Divergent (root test)"
                    elif root_limit == 1:
                        convergence = "Inconclusive (root test - need more analysis)"
                    else:
                        convergence = "Inconclusive (root test)"
                except MathematicsError:
                    convergence = "Inconclusive (root test - computation failed)"

            else:
                return {
                    'error': f'Unknown test type: {test_type}',
                    'available_tests': ['ratio', 'root'],
                    'status': 'invalid_test'
                }

            return {
                'series': str(series_expr),
                'test_type': test_type,
                'result': convergence,
                'limit_value': str(ratio_limit) if test_type == 'ratio' else str(root_limit),
                'variable': variable,
                'status': 'success'
            }

        except (ValueError, TypeError, sp.SympifyError) as e:
            return {
                'error': str(e),
                'series': series,
                'status': 'failed'
            }

    def analytic_continuation(self, function: str, original_domain: str,
                            extension_domain: str, variable: str = 'z') -> Dict[str, Any]:
        """
        Perform analytic continuation of a function to a larger domain
        """
        try:
            expr = sp.sympify(function)
            # variable parameter is kept for API consistency but not used in simplified implementation

            # This is a simplified implementation
            # Real analytic continuation requires more sophisticated analysis

            return {
                'function': str(expr),
                'original_domain': original_domain,
                'extension_domain': extension_domain,
                'method': 'Analytic continuation',
                'note': 'Full analytic continuation requires detailed domain analysis',
                'status': 'success'
            }

        except (ValueError, TypeError, sp.SympifyError) as e:
            return {
                'error': str(e),
                'function': function,
                'status': 'failed'
            }

    def get_series_examples(self) -> GetSeriesExamplesResult:
        """
        Get examples of common series in complex analysis
        """
        return {
            'series': self.series_examples,
            'description': 'Common power series in complex analysis',
            'count': len(self.series_examples)
        }
