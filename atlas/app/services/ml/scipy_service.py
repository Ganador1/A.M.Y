"""
SciPy Service - Integración Numérica y Estadística Avanzada
Proporciona operaciones numéricas, integración, optimización y estadística
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SciPyService:
    """Servicio para operaciones numéricas y estadísticas usando SciPy"""
    
    def __init__(self):
        self.service_name = "SciPyService"
        logger.info(f"✅ {self.service_name} initialized")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes de operaciones numéricas
        
        Operaciones soportadas:
        - 'integrate': Integración numérica
        - 'optimize': Optimización de funciones
        - 'interpolate': Interpolación de datos
        - 'fft': Transformada rápida de Fourier
        - 'stats': Análisis estadístico
        - 'linear_algebra': Álgebra lineal
        - 'ode_solve': Resolver ecuaciones diferenciales ordinarias
        """
        # Soportar tanto 'action' como 'operation' para compatibilidad
        operation = request_data.get('operation') or request_data.get('action')
        
        if operation == 'integrate':
            return await self.numerical_integration(request_data)
        elif operation == 'optimize':
            return await self.optimize_function(request_data)
        elif operation == 'interpolate':
            return await self.interpolate_data(request_data)
        elif operation == 'fft':
            return await self.compute_fft(request_data)
        elif operation == 'stats':
            return await self.statistical_analysis(request_data)
        elif operation == 'linear_algebra':
            return await self.linear_algebra_ops(request_data)
        elif operation == 'ode_solve':
            return await self.solve_ode(request_data)
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "supported_operations": ['integrate', 'optimize', 'interpolate', 'fft', 'stats', 'linear_algebra', 'ode_solve']
            }
    
    async def numerical_integration(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integración numérica de funciones"""
        try:
            from scipy import integrate
            import numpy as np
            
            method = request_data.get('method', 'quad')
            lower = request_data.get('lower', 0)
            upper = request_data.get('upper', 1)
            
            # Función de ejemplo (puede ser parametrizada)
            func_type = request_data.get('function', 'polynomial')
            
            if func_type == 'polynomial':
                # x^2
                func = lambda x: x**2
            elif func_type == 'exponential':
                # e^x
                func = lambda x: np.exp(x)
            elif func_type == 'sine':
                # sin(x)
                func = lambda x: np.sin(x)
            else:
                func = lambda x: x**2
            
            if method == 'quad':
                result, error = integrate.quad(func, lower, upper)
                
                return {
                    "success": True,
                    "operation": "numerical_integration",
                    "method": "quad",
                    "limits": [lower, upper],
                    "result": float(result),
                    "error_estimate": float(error),
                    "function": func_type
                }
            elif method == 'trapz':
                x_vals = np.linspace(lower, upper, 100)
                y_vals = func(x_vals)
                result = integrate.trapz(y_vals, x_vals)
                
                return {
                    "success": True,
                    "operation": "numerical_integration",
                    "method": "trapz",
                    "limits": [lower, upper],
                    "result": float(result),
                    "points": 100,
                    "function": func_type
                }
            
        except Exception as e:
            logger.error(f"Error in numerical integration: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "numerical_integration"
            }
    
    async def optimize_function(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimización de funciones"""
        try:
            from scipy import optimize
            import numpy as np
            
            method = request_data.get('method', 'minimize')
            
            # Función de prueba: Rosenbrock function
            def rosenbrock(x):
                return sum(100.0 * (x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0)
            
            x0 = np.array(request_data.get('initial_guess', [1.3, 0.7, 0.8, 1.9, 1.2]))
            
            result = optimize.minimize(rosenbrock, x0, method='BFGS')
            
            return {
                "success": True,
                "operation": "optimize",
                "method": "BFGS",
                "initial_guess": x0.tolist(),
                "optimal_point": result.x.tolist(),
                "optimal_value": float(result.fun),
                "iterations": int(result.nit),
                "converged": bool(result.success)
            }
            
        except Exception as e:
            logger.error(f"Error in optimization: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "optimize"
            }
    
    async def interpolate_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Interpolación de datos"""
        try:
            from scipy import interpolate
            import numpy as np
            
            # Datos de ejemplo
            x = np.array(request_data.get('x', [0, 1, 2, 3, 4, 5]))
            y = np.array(request_data.get('y', [0, 1, 4, 9, 16, 25]))
            
            kind = request_data.get('kind', 'cubic')
            
            f = interpolate.interp1d(x, y, kind=kind)
            
            # Puntos de interpolación
            x_new = np.linspace(x.min(), x.max(), 20)
            y_new = f(x_new)
            
            return {
                "success": True,
                "operation": "interpolate",
                "kind": kind,
                "original_points": len(x),
                "interpolated_points": len(x_new),
                "x_interpolated": x_new.tolist(),
                "y_interpolated": y_new.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error in interpolation: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "interpolate"
            }
    
    async def compute_fft(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transformada rápida de Fourier"""
        try:
            from scipy.fft import fft, fftfreq
            import numpy as np
            
            # Señal de ejemplo
            N = request_data.get('sample_points', 600)
            T = request_data.get('sample_spacing', 1.0 / 800.0)
            
            x = np.linspace(0.0, N*T, N, endpoint=False)
            y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
            
            yf = fft(y)
            xf = fftfreq(N, T)[:N//2]
            
            return {
                "success": True,
                "operation": "fft",
                "sample_points": N,
                "sample_spacing": T,
                "frequencies_computed": len(xf),
                "dominant_frequencies": xf[:10].tolist(),
                "magnitudes": (2.0/N * np.abs(yf[0:N//2]))[:10].tolist()
            }
            
        except Exception as e:
            logger.error(f"Error in FFT: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "fft"
            }
    
    async def statistical_analysis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análisis estadístico avanzado"""
        try:
            from scipy import stats
            import numpy as np
            
            # Datos de ejemplo
            data = np.array(request_data.get('data', np.random.normal(100, 15, 100)))
            
            # Estadísticas descriptivas
            mean = np.mean(data)
            std = np.std(data)
            
            # Test de normalidad
            statistic, p_value = stats.normaltest(data)
            
            # Intervalos de confianza
            confidence_level = request_data.get('confidence', 0.95)
            ci = stats.t.interval(confidence_level, len(data)-1, 
                                 loc=mean, scale=stats.sem(data))
            
            return {
                "success": True,
                "operation": "stats",
                "sample_size": len(data),
                "mean": float(mean),
                "std_dev": float(std),
                "normality_test": {
                    "statistic": float(statistic),
                    "p_value": float(p_value),
                    "is_normal": p_value > 0.05
                },
                "confidence_interval": {
                    "level": confidence_level,
                    "lower": float(ci[0]),
                    "upper": float(ci[1])
                }
            }
            
        except Exception as e:
            logger.error(f"Error in statistical analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "stats"
            }
    
    async def linear_algebra_ops(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Operaciones de álgebra lineal"""
        try:
            from scipy import linalg
            import numpy as np
            
            operation_type = request_data.get('type', 'eigenvalues')
            
            # Matriz de ejemplo
            A = np.array(request_data.get('matrix', [[1, 2], [3, 4]]))
            
            if operation_type == 'eigenvalues':
                eigenvalues, eigenvectors = linalg.eig(A)
                
                return {
                    "success": True,
                    "operation": "linear_algebra",
                    "type": "eigenvalues",
                    "matrix_shape": A.shape,
                    "eigenvalues": eigenvalues.tolist(),
                    "eigenvectors": eigenvectors.tolist()
                }
            elif operation_type == 'det':
                det = linalg.det(A)
                
                return {
                    "success": True,
                    "operation": "linear_algebra",
                    "type": "determinant",
                    "determinant": float(det)
                }
            
        except Exception as e:
            logger.error(f"Error in linear algebra: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "linear_algebra"
            }
    
    async def solve_ode(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolver ecuaciones diferenciales ordinarias"""
        try:
            from scipy.integrate import solve_ivp
            import numpy as np
            
            # Ejemplo: dy/dt = -2y
            def exponential_decay(t, y):
                return -2 * y
            
            t_span = (0, 5)
            y0 = [1]
            
            sol = solve_ivp(exponential_decay, t_span, y0, 
                          t_eval=np.linspace(0, 5, 50))
            
            return {
                "success": True,
                "operation": "ode_solve",
                "method": "RK45",
                "time_span": t_span,
                "initial_condition": y0,
                "solution_points": len(sol.t),
                "final_value": float(sol.y[0][-1]),
                "converged": sol.success
            }
            
        except Exception as e:
            logger.error(f"Error solving ODE: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "ode_solve"
            }
