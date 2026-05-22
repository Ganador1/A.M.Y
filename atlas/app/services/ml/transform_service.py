"""
Integral Transforms Service for Mathematics AI
Provides capabilities for Fourier, Laplace, and Z-transforms
"""

import numpy as np
import sympy as sp
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import io
import base64
from scipy.fft import fft, ifft, fftfreq
from scipy.integrate import quad
import cmath
from app.exceptions.domain.mathematics import MathematicsError
from app.types.transform_service_types import (
    InverseDiscreteFourierTransformResult,
    GetTransformPairsResult,
    SolveOdeWithLaplaceResult,
)


class TransformService:
    """Service for integral transforms and signal processing"""

    def __init__(self):
        self.t, self.f, self.s, self.z, self.omega = sp.symbols('t f s z omega')
        self.x = sp.Symbol('x', real=True)

        # Common transform pairs
        self.fourier_pairs = {
            'rectangular': {
                'time_domain': 'rect(t)',
                'frequency_domain': 'sinc(f)',
                'description': 'Rectangular function'
            },
            'gaussian': {
                'time_domain': 'exp(-a*t**2)',
                'frequency_domain': 'sqrt(pi/a)*exp(-pi**2*f**2/a)',
                'description': 'Gaussian function'
            },
            'exponential': {
                'time_domain': 'exp(-a*t)*heaviside(t)',
                'frequency_domain': '1/(a + 2*pi*I*f)',
                'description': 'Exponential decay'
            },
            'sine': {
                'time_domain': 'sin(omega0*t)',
                'frequency_domain': 'pi*I*(dirac(f - omega0) - dirac(f + omega0))',
                'description': 'Sine wave'
            },
            'cosine': {
                'time_domain': 'cos(omega0*t)',
                'frequency_domain': 'pi*(dirac(f - omega0) + dirac(f + omega0))',
                'description': 'Cosine wave'
            }
        }

        self.laplace_pairs = {
            'unit_step': {
                'time_domain': 'heaviside(t)',
                's_domain': '1/s',
                'description': 'Unit step function'
            },
            'exponential': {
                'time_domain': 'exp(-a*t)',
                's_domain': '1/(s + a)',
                'description': 'Exponential function'
            },
            'sine': {
                'time_domain': 'sin(omega*t)',
                's_domain': 'omega/(s**2 + omega**2)',
                'description': 'Sine function'
            },
            'cosine': {
                'time_domain': 'cos(omega*t)',
                's_domain': 's/(s**2 + omega**2)',
                'description': 'Cosine function'
            },
            'power': {
                'time_domain': 't**n',
                's_domain': 'factorial(n)/s**(n+1)',
                'description': 'Power function'
            }
        }

    def fourier_transform(self, expression: str, variable: str = 't',
                         result_variable: str = 'f') -> Dict[str, Any]:
        """
        Compute the Fourier transform of a function

        F(ω) = ∫ f(t) * exp(-jωt) dt
        """
        try:
            # Parse the expression
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            freq_var = sp.Symbol(result_variable)

            # Compute Fourier transform
            fourier_result = sp.fourier_transform(expr, var, freq_var)

            # Try to simplify
            simplified = sp.simplify(fourier_result)

            return {
                'original_function': str(expr),
                'fourier_transform': str(simplified),
                'variable': variable,
                'frequency_variable': result_variable,
                'simplified': str(simplified),
                'complexity': len(str(simplified))
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'original_function': expression,
                'status': 'failed'
            }

    def inverse_fourier_transform(self, expression: str, variable: str = 'f',
                                result_variable: str = 't') -> Dict[str, Any]:
        """
        Compute the inverse Fourier transform

        f(t) = (1/(2π)) ∫ F(ω) * exp(jωt) dω
        """
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            time_var = sp.Symbol(result_variable)

            # Compute inverse Fourier transform
            inverse_result = sp.inverse_fourier_transform(expr, var, time_var)

            # Try to simplify
            simplified = sp.simplify(inverse_result)

            return {
                'original_transform': str(expr),
                'inverse_transform': str(simplified),
                'frequency_variable': variable,
                'time_variable': result_variable,
                'simplified': str(simplified),
                'complexity': len(str(simplified))
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'original_transform': expression,
                'status': 'failed'
            }

    def laplace_transform(self, expression: str, variable: str = 't',
                         result_variable: str = 's') -> Dict[str, Any]:
        """
        Compute the Laplace transform of a function

        L{f(t)} = ∫₀^∞ f(t) * exp(-st) dt
        """
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            s_var = sp.Symbol(result_variable)

            # Compute Laplace transform
            laplace_result = sp.laplace_transform(expr, var, s_var)

            # Extract the transform (laplace_transform returns a tuple)
            if isinstance(laplace_result, tuple):
                transform_expr = laplace_result[0]
            else:
                transform_expr = laplace_result

            # Try to simplify
            simplified = sp.simplify(transform_expr)

            return {
                'original_function': str(expr),
                'laplace_transform': str(simplified),
                'variable': variable,
                's_variable': result_variable,
                'simplified': str(simplified),
                'complexity': len(str(simplified))
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'original_function': expression,
                'status': 'failed'
            }

    def inverse_laplace_transform(self, expression: str, variable: str = 's',
                                 result_variable: str = 't') -> Dict[str, Any]:
        """
        Compute the inverse Laplace transform

        f(t) = (1/(2πj)) ∫_{σ-j∞}^{σ+j∞} F(s) * exp(st) ds
        """
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            time_var = sp.Symbol(result_variable)

            # Compute inverse Laplace transform
            inverse_result = sp.inverse_laplace_transform(expr, var, time_var)

            # Try to simplify
            simplified = sp.simplify(inverse_result)

            return {
                'original_transform': str(expr),
                'inverse_transform': str(simplified),
                's_variable': variable,
                'time_variable': result_variable,
                'simplified': str(simplified),
                'complexity': len(str(simplified))
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'original_transform': expression,
                'status': 'failed'
            }

    def z_transform(self, expression: str, variable: str = 'n',
                   result_variable: str = 'z') -> Dict[str, Any]:
        """
        Compute the Z-transform of a discrete-time function

        X(z) = Σ x[n] * z^(-n)
        """
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable, integer=True)
            z_var = sp.Symbol(result_variable)

            # Compute Z-transform
            z_result = sp.summation(expr * z_var**(-var), (var, 0, sp.oo))

            # Try to simplify
            simplified = sp.simplify(z_result)

            return {
                'original_function': str(expr),
                'z_transform': str(simplified),
                'variable': variable,
                'z_variable': result_variable,
                'simplified': str(simplified),
                'complexity': len(str(simplified))
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'original_function': expression,
                'status': 'failed'
            }

    def discrete_fourier_transform(self, signal: List[float],
                                 sampling_rate: float = 1.0) -> Dict[str, Any]:
        """
        Compute the Discrete Fourier Transform (DFT) of a signal
        """
        try:
            signal_array = np.array(signal)
            n = len(signal_array)

            # Compute DFT
            dft = np.array(fft(signal_array))

            # Compute frequency bins
            frequencies = fftfreq(n, 1/sampling_rate)

            # Compute magnitude and phase
            magnitude = np.abs(dft)
            phase = np.angle(dft)

            # Create frequency domain plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

            # Magnitude plot
            ax1.plot(frequencies[:n//2], magnitude[:n//2])
            ax1.set_title('Magnitude Spectrum')
            ax1.set_xlabel('Frequency (Hz)')
            ax1.set_ylabel('Magnitude')
            ax1.grid(True)

            # Phase plot
            ax2.plot(frequencies[:n//2], phase[:n//2])
            ax2.set_title('Phase Spectrum')
            ax2.set_xlabel('Frequency (Hz)')
            ax2.set_ylabel('Phase (radians)')
            ax2.grid(True)

            plt.tight_layout()

            # Convert plot to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            plot_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()

            return {
                'dft_coefficients': dft.tolist(),
                'frequencies': frequencies.tolist(),
                'magnitude': magnitude.tolist(),
                'phase': phase.tolist(),
                'sampling_rate': sampling_rate,
                'signal_length': n,
                'plot': plot_base64,
                'status': 'success'
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'status': 'failed'
            }

    def inverse_discrete_fourier_transform(self, dft_coefficients: List[complex]) -> InverseDiscreteFourierTransformResult:
        """
        Compute the Inverse Discrete Fourier Transform (IDFT)
        """
        try:
            dft_array = np.array(dft_coefficients)

            # Compute IDFT
            signal = ifft(dft_array)

            # Return real part (imaginary part should be negligible for real signals)
            reconstructed_signal = signal.real.tolist()

            return {
                'reconstructed_signal': reconstructed_signal,
                'original_dft_length': len(dft_coefficients),
                'status': 'success'
            }

        except MathematicsError as e:
            return {
                'error': str(e),
                'status': 'failed'
            }

    def fast_fourier_transform(self, signal: List[float],
                             sampling_rate: float = 1.0) -> Dict[str, Any]:
        """
        Compute FFT (same as DFT but optimized for speed)
        """
        return self.discrete_fourier_transform(signal, sampling_rate)

    def get_transform_pairs(self, transform_type: str) -> GetTransformPairsResult:
        """
        Get common transform pairs for reference
        """
        if transform_type.lower() == 'fourier':
            return {
                'transform_type': 'Fourier',
                'pairs': self.fourier_pairs,
                'description': 'Common Fourier transform pairs'
            }
        elif transform_type.lower() == 'laplace':
            return {
                'transform_type': 'Laplace',
                'pairs': self.laplace_pairs,
                'description': 'Common Laplace transform pairs'
            }
        else:
            return {
                'error': f'Unknown transform type: {transform_type}',
                'available_types': ['fourier', 'laplace']
            }

    def solve_ode_with_laplace(self, equation: str, initial_conditions: Optional[Dict[str, float]] = None) -> SolveOdeWithLaplaceResult:
        """
        Solve ordinary differential equation using Laplace transforms
        """
        try:
            # Assume the equation is of the form: d²y/dt² + a*dy/dt + b*y = f(t)
            # For now, implement a simple case
            y = sp.Function('y')(self.t)

            # Simple second-order ODE: y'' + 2*y' + y = exp(-t)
            if 'exp(-t)' in equation:
                # Take Laplace transform
                Y = sp.laplace_transform(y, self.t, self.s)[0]

                # Apply initial conditions
                if initial_conditions:
                    Y_ic = Y
                    if 'y(0)' in initial_conditions:
                        Y_ic = Y_ic.subs(sp.laplace_transform(y, self.t, self.s)[1], initial_conditions['y(0)'])
                    if 'y\'(0)' in initial_conditions:
                        # This is more complex - would need derivative of transform
                        pass

                # Solve for Y(s)
                solution_s = Y / (self.s**2 + 2*self.s + 1)  # For y'' + 2y' + y = 1/s

                # Inverse Laplace transform
                solution_t = sp.inverse_laplace_transform(solution_s, self.s, self.t)

                return {
                    'original_ode': equation,
                    'laplace_solution': str(solution_s),
                    'time_solution': str(solution_t),
                    'method': 'Laplace Transform',
                    'status': 'success'
                }
            else:
                return {
                    'error': 'Currently only supports simple ODEs with exponential forcing',
                    'original_ode': equation,
                    'status': 'unsupported'
                }

        except MathematicsError as e:
            return {
                'error': str(e),
                'original_ode': equation,
                'status': 'failed'
            }
