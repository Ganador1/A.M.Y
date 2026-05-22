"""
AXIOM Advanced NumPy Operations Module
Exploiting NumPy's full numerical computing capabilities
"""

import numpy as np
from numpy import linalg, fft, random, polynomial
from numpy.linalg import solve, inv, det, eig, svd, qr
from numpy.fft import fft as np_fft, ifft, fft2, ifft2, fftfreq, fftshift
from numpy.random import Generator, PCG64, MT19937
from numpy.polynomial import Polynomial, Chebyshev, Legendre, Hermite
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass
import warnings

logger = logging.getLogger(__name__)

@dataclass
class NumPyConfig:
    """Configuration for advanced NumPy operations"""
    dtype: np.dtype = np.float64
    random_seed: Optional[int] = None
    use_parallel: bool = True
    max_workers: Optional[int] = None
    memory_efficient: bool = True
    precision: str = 'high'

class AdvancedNumPyOperations:
    """Advanced NumPy operations exploiting full numerical capabilities"""

    def __init__(self, config: Optional[NumPyConfig] = None):
        self.config = config or NumPyConfig()

        # Setup random number generator
        if self.config.random_seed is not None:
            self.rng = Generator(PCG64(self.config.random_seed))
        else:
            self.rng = Generator(PCG64())

        # Setup thread/process pools
        self.max_workers = self.config.max_workers or mp.cpu_count()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)

        # Memory management
        self._setup_memory_management()

        logger.info("✅ Advanced NumPy Operations initialized")

    def _setup_memory_management(self):
        """Setup memory-efficient operations"""
        # Set NumPy to use memory efficiently
        np.seterr(all='warn')  # Warn on numerical errors
        if self.config.memory_efficient:
            # Use memory mapping for large arrays when possible
            self.use_memory_map = True
        else:
            self.use_memory_map = False

    def advanced_array_operations(self, arrays: List[np.ndarray],
                                operation: str = 'elementwise') -> Dict[str, Any]:
        """Advanced array operations with broadcasting and vectorization"""
        results = {}

        try:
            # Broadcasting operations
            if operation == 'broadcasting':
                # Automatic broadcasting
                broadcasted = np.broadcast_arrays(*arrays)
                results['broadcasted_shapes'] = [arr.shape for arr in broadcasted]
                results['broadcasted_arrays'] = [arr.tolist() for arr in broadcasted]

            elif operation == 'vectorized':
                # Vectorized operations
                if len(arrays) >= 2:
                    # Element-wise operations
                    results['add'] = (arrays[0] + arrays[1]).tolist()
                    results['subtract'] = (arrays[0] - arrays[1]).tolist()
                    results['multiply'] = (arrays[0] * arrays[1]).tolist()
                    results['divide'] = (arrays[0] / arrays[1]).tolist()

                    # Advanced operations
                    results['power'] = np.power(arrays[0], arrays[1]).tolist()
                    results['maximum'] = np.maximum(arrays[0], arrays[1]).tolist()
                    results['minimum'] = np.minimum(arrays[0], arrays[1]).tolist()

            elif operation == 'reduction':
                # Reduction operations
                for i, arr in enumerate(arrays):
                    results[f'array_{i}'] = {
                        'sum': np.sum(arr),
                        'mean': np.mean(arr),
                        'std': np.std(arr),
                        'var': np.var(arr),
                        'min': np.min(arr),
                        'max': np.max(arr),
                        'product': np.prod(arr),
                        'cumsum': np.cumsum(arr).tolist(),
                        'cumprod': np.cumprod(arr).tolist()
                    }

            elif operation == 'reshaping':
                # Advanced reshaping
                for i, arr in enumerate(arrays):
                    original_shape = arr.shape
                    flat = arr.flatten()
                    results[f'array_{i}_reshaping'] = {
                        'original_shape': original_shape,
                        'flattened': flat.tolist(),
                        'reshaped_2d': arr.reshape(-1, 1).tolist() if arr.size > 0 else [],
                        'transposed': arr.T.tolist(),
                        'raveled': np.ravel(arr).tolist()
                    }

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_linear_algebra(self, matrix: np.ndarray,
                              operation: str = 'decompose') -> Dict[str, Any]:
        """Advanced linear algebra operations"""
        results = {}

        try:
            # Matrix properties
            results['shape'] = matrix.shape
            results['rank'] = np.linalg.matrix_rank(matrix)
            results['trace'] = np.trace(matrix)
            results['determinant'] = det(matrix)
            results['condition_number'] = np.linalg.cond(matrix)

            if operation == 'decompose':
                # Multiple decompositions
                if matrix.shape[0] == matrix.shape[1]:  # Square matrix
                    # QR decomposition
                    Q, R = qr(matrix)
                    results['QR'] = {
                        'Q': Q.tolist(),
                        'R': R.tolist()
                    }

                    # Eigenvalue decomposition
                    eigenvals, eigenvecs = eig(matrix)
                    results['eigen'] = {
                        'values': eigenvals.tolist(),
                        'vectors': eigenvecs.tolist()
                    }

                    # SVD
                    U, s, Vt = svd(matrix)
                    results['SVD'] = {
                        'U': U.tolist(),
                        'singular_values': s.tolist(),
                        'Vt': Vt.tolist()
                    }

            elif operation == 'solve':
                # Solve linear systems
                if matrix.shape[0] == matrix.shape[1]:
                    b = np.ones(matrix.shape[0])
                    x = solve(matrix, b)
                    results['solution'] = x.tolist()

                    # Verify solution
                    residual = matrix @ x - b
                    results['residual'] = residual.tolist()
                    results['residual_norm'] = np.linalg.norm(residual)

            elif operation == 'inverse':
                if matrix.shape[0] == matrix.shape[1]:
                    try:
                        inv_matrix = inv(matrix)
                        results['inverse'] = inv_matrix.tolist()

                        # Verify inverse
                        identity_check = matrix @ inv_matrix
                        results['inverse_check'] = np.allclose(identity_check, np.eye(matrix.shape[0]))
                    except np.linalg.LinAlgError:
                        results['inverse'] = "Matrix is singular"

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_fft_operations(self, signal: np.ndarray,
                              sampling_rate: float = 1000.0) -> Dict[str, Any]:
        """Advanced Fast Fourier Transform operations"""
        results = {}

        try:
            # 1D FFT
            fft_result = np_fft(signal)
            freqs = fftfreq(len(signal), 1/sampling_rate)

            results['fft_1d'] = {
                'frequencies': freqs.tolist(),
                'magnitude': np.abs(fft_result).tolist(),
                'phase': np.angle(fft_result).tolist(),
                'power_spectrum': (np.abs(fft_result) ** 2).tolist()
            }

            # Shifted FFT (center zero frequency)
            shifted_fft = fftshift(fft_result)
            shifted_freqs = fftshift(freqs)
            results['fft_shifted'] = {
                'frequencies': shifted_freqs.tolist(),
                'magnitude': np.abs(shifted_fft).tolist()
            }

            # 2D FFT if applicable
            if signal.ndim == 2:
                fft_2d = fft2(signal)
                results['fft_2d'] = {
                    'magnitude': np.abs(fft_2d).tolist(),
                    'phase': np.angle(fft_2d).tolist()
                }

            # Inverse FFT
            reconstructed = ifft(fft_result)
            results['reconstruction'] = {
                'real': np.real(reconstructed).tolist(),
                'imag': np.imag(reconstructed).tolist(),
                'reconstruction_error': np.linalg.norm(signal - np.real(reconstructed))
            }

            # Windowed FFT
            window = np.hanning(len(signal))
            windowed_signal = signal * window
            windowed_fft = np_fft(windowed_signal)
            results['windowed_fft'] = {
                'window': window.tolist(),
                'magnitude': np.abs(windowed_fft).tolist()
            }

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_random_operations(self, size: Union[int, Tuple],
                                distribution: str = 'normal',
                                params: Optional[Dict] = None) -> Dict[str, Any]:
        """Advanced random number generation and analysis"""
        results = {}

        try:
            params = params or {}

            # Generate random data
            if distribution == 'normal':
                mu = params.get('mu', 0.0)
                sigma = params.get('sigma', 1.0)
                data = self.rng.normal(mu, sigma, size)
                results['distribution'] = 'normal'
                results['parameters'] = {'mu': mu, 'sigma': sigma}

            elif distribution == 'uniform':
                low = params.get('low', 0.0)
                high = params.get('high', 1.0)
                data = self.rng.uniform(low, high, size)
                results['distribution'] = 'uniform'
                results['parameters'] = {'low': low, 'high': high}

            elif distribution == 'exponential':
                scale = params.get('scale', 1.0)
                data = self.rng.exponential(scale, size)
                results['distribution'] = 'exponential'
                results['parameters'] = {'scale': scale}

            elif distribution == 'gamma':
                shape = params.get('shape', 2.0)
                scale = params.get('scale', 1.0)
                data = self.rng.gamma(shape, scale, size)
                results['distribution'] = 'gamma'
                results['parameters'] = {'shape': shape, 'scale': scale}

            # Statistical analysis
            results['data'] = data.tolist()
            results['statistics'] = {
                'mean': np.mean(data),
                'std': np.std(data),
                'min': np.min(data),
                'max': np.max(data),
                'median': np.median(data),
                'skewness': self._calculate_skewness(data),
                'kurtosis': self._calculate_kurtosis(data)
            }

            # Distribution fitting
            if distribution == 'normal':
                # Test for normality
                results['normality_test'] = self._shapiro_wilk_test(data)

            # Random sampling
            sample_size = min(100, len(data))
            sample = self.rng.choice(data, size=sample_size, replace=False)
            results['sample'] = sample.tolist()

        except Exception as e:
            results['error'] = str(e)

        return results

    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data"""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 3)

    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of data"""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 4) - 3

    def _shapiro_wilk_test(self, data: np.ndarray) -> Dict[str, float]:
        """Simplified Shapiro-Wilk test for normality"""
        # This is a simplified version - in practice, use scipy.stats.shapiro
        n = len(data)
        if n < 3:
            return {'statistic': 1.0, 'p_value': 1.0}

        # Sort data
        sorted_data = np.sort(data)

        # Calculate test statistic (simplified)
        std = np.std(sorted_data)

        # This is not the actual Shapiro-Wilk statistic
        # In practice, use scipy.stats.shapiro for accurate results
        statistic = 1.0 - abs(np.mean(sorted_data) - np.median(sorted_data)) / std
        p_value = 1.0 if statistic > 0.9 else 0.0

        return {'statistic': statistic, 'p_value': p_value}

    def advanced_polynomial_operations(self, coeffs: List[float],
                                     operation: str = 'evaluate') -> Dict[str, Any]:
        """Advanced polynomial operations"""
        results = {}

        try:
            poly = np.poly1d(coeffs)

            if operation == 'evaluate':
                # Evaluate at multiple points
                x_vals = np.linspace(-10, 10, 100)
                y_vals = poly(x_vals)
                results['evaluation'] = {
                    'x': x_vals.tolist(),
                    'y': y_vals.tolist()
                }

            elif operation == 'roots':
                roots = poly.roots
                results['roots'] = roots.tolist()

            elif operation == 'derivative':
                deriv = poly.deriv()
                results['derivative_coeffs'] = deriv.coeffs.tolist()

            elif operation == 'integral':
                integ = poly.integ()
                results['integral_coeffs'] = integ.coeffs.tolist()

            elif operation == 'fit':
                # Generate sample data and fit polynomial
                x_data = np.linspace(0, 10, 50)
                y_data = 2*x_data**2 + 3*x_data + 1 + self.rng.normal(0, 1, 50)

                fit_coeffs = np.polyfit(x_data, y_data, len(coeffs)-1)
                results['polynomial_fit'] = {
                    'original_coeffs': coeffs,
                    'fitted_coeffs': fit_coeffs.tolist(),
                    'x_data': x_data.tolist(),
                    'y_data': y_data.tolist()
                }

            # General polynomial properties
            results['polynomial'] = {
                'coeffs': poly.coeffs.tolist(),
                'degree': poly.order,
                'string': str(poly)
            }

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_memory_operations(self, array_size: Tuple,
                                operation: str = 'efficient') -> Dict[str, Any]:
        """Advanced memory-efficient operations"""
        results = {}

        try:
            if operation == 'efficient':
                # Create large array efficiently
                if self.use_memory_map:
                    # Use memory mapping for large arrays
                    large_array = np.memmap('temp_array.dat', dtype=self.config.dtype,
                                          mode='w+', shape=array_size)
                else:
                    large_array = np.zeros(array_size, dtype=self.config.dtype)

                results['array_info'] = {
                    'shape': large_array.shape,
                    'dtype': str(large_array.dtype),
                    'nbytes': large_array.nbytes,
                    'memory_mapped': isinstance(large_array, np.memmap)
                }

                # Clean up
                if isinstance(large_array, np.memmap):
                    large_array = None  # Close memory map
                    import os
                    if os.path.exists('temp_array.dat'):
                        os.remove('temp_array.dat')

            elif operation == 'chunked':
                # Process large data in chunks
                total_size = np.prod(array_size)
                chunk_size = min(1000000, total_size)  # 1M elements per chunk

                chunks = []
                for i in range(0, total_size, chunk_size):
                    end_idx = min(i + chunk_size, total_size)
                    chunk = np.arange(i, end_idx, dtype=self.config.dtype)
                    chunks.append(chunk.tolist()[:10])  # Store only first 10 elements

                results['chunked_processing'] = {
                    'total_elements': total_size,
                    'chunk_size': chunk_size,
                    'num_chunks': len(chunks),
                    'sample_chunks': chunks[:3]  # Show first 3 chunks
                }

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_parallel_operations(self, data: np.ndarray,
                                   operation: str = 'parallel_sum') -> Dict[str, Any]:
        """Advanced parallel operations using multiple cores"""
        results = {}

        try:
            if operation == 'parallel_sum':
                # Parallel sum using thread pool
                def chunk_sum(chunk):
                    return np.sum(chunk)

                chunk_size = len(data) // self.max_workers
                chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

                # Submit tasks to thread pool
                futures = [self.thread_pool.submit(chunk_sum, chunk) for chunk in chunks]
                partial_sums = [future.result() for future in futures]

                results['parallel_sum'] = {
                    'total_sum': sum(partial_sums),
                    'partial_sums': partial_sums,
                    'num_workers': len(chunks)
                }

            elif operation == 'parallel_fft':
                # Parallel FFT on multiple signals
                if data.ndim == 2:
                    def signal_fft(signal):
                        return np_fft(signal)

                    futures = [self.thread_pool.submit(signal_fft, data[i, :])
                             for i in range(data.shape[0])]

                    fft_results = [future.result() for future in futures]
                    results['parallel_fft'] = {
                        'fft_magnitudes': [np.abs(fft).tolist() for fft in fft_results],
                        'num_signals': len(fft_results)
                    }

            elif operation == 'parallel_matrix_mult':
                # Parallel matrix multiplication
                if data.ndim == 3 and data.shape[0] >= 2:
                    def matrix_multiply(a, b):
                        return np.dot(a, b)

                    matrices = [data[i] for i in range(min(4, data.shape[0]))]
                    futures = []

                    # Multiply consecutive pairs
                    for i in range(0, len(matrices)-1, 2):
                        future = self.thread_pool.submit(matrix_multiply,
                                                       matrices[i], matrices[i+1])
                        futures.append(future)

                    results_matrices = [future.result() for future in futures]
                    results['parallel_matrix_mult'] = {
                        'result_shapes': [m.shape for m in results_matrices],
                        'num_operations': len(futures)
                    }

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_vectorization(self, data: np.ndarray,
                             operation: str = 'vectorized_ops') -> Dict[str, Any]:
        """Advanced vectorized operations for performance"""
        results = {}

        try:
            if operation == 'vectorized_ops':
                # Vectorized mathematical operations
                results['sin'] = np.sin(data).tolist()
                results['cos'] = np.cos(data).tolist()
                results['exp'] = np.exp(data).tolist()
                results['log'] = np.log(np.abs(data) + 1e-10).tolist()  # Avoid log(0)
                results['sqrt'] = np.sqrt(np.abs(data)).tolist()

            elif operation == 'conditional_ops':
                # Vectorized conditional operations
                results['where_positive'] = np.where(data > 0, data, 0).tolist()
                results['where_negative'] = np.where(data < 0, data, 0).tolist()
                results['clipped'] = np.clip(data, -1, 1).tolist()

            elif operation == 'broadcasting_demo':
                # Broadcasting demonstration
                scalar = 2.0
                vector = np.array([1, 2, 3])
                matrix = np.array([[1, 2, 3], [4, 5, 6]])

                results['scalar_broadcast'] = (data * scalar).tolist()
                results['vector_broadcast'] = (data.reshape(-1, 1) + vector).tolist()
                results['matrix_broadcast'] = (data.reshape(-1, 1) + matrix).tolist()

            elif operation == 'ufunc_operations':
                # Universal function operations
                results['add_reduce'] = np.add.reduce(data)
                results['multiply_reduce'] = np.multiply.reduce(data)
                results['add_accumulate'] = np.add.accumulate(data).tolist()
                results['multiply_accumulate'] = np.multiply.accumulate(data).tolist()

        except Exception as e:
            results['error'] = str(e)

        return results

    def numerical_computation_pipeline(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Complete numerical computation pipeline"""
        results = {
            'original_problem': problem,
            'computation_steps': [],
            'final_results': {},
            'performance_metrics': {}
        }

        start_time = time.time()

        try:
            problem_type = problem.get('type', 'general')

            if problem_type == 'linear_algebra':
                matrix = np.array(problem['matrix'])
                operation = problem.get('operation', 'decompose')
                la_results = self.advanced_linear_algebra(matrix, operation)
                results['final_results']['linear_algebra'] = la_results
                results['computation_steps'].append('linear_algebra')

            elif problem_type == 'fft':
                signal = np.array(problem['signal'])
                sampling_rate = problem.get('sampling_rate', 1000.0)
                fft_results = self.advanced_fft_operations(signal, sampling_rate)
                results['final_results']['fft'] = fft_results
                results['computation_steps'].append('fft')

            elif problem_type == 'random':
                size = problem['size']
                distribution = problem.get('distribution', 'normal')
                params = problem.get('params', {})
                rand_results = self.advanced_random_operations(size, distribution, params)
                results['final_results']['random'] = rand_results
                results['computation_steps'].append('random')

            elif problem_type == 'polynomial':
                coeffs = problem['coefficients']
                operation = problem.get('operation', 'evaluate')
                poly_results = self.advanced_polynomial_operations(coeffs, operation)
                results['final_results']['polynomial'] = poly_results
                results['computation_steps'].append('polynomial')

            elif problem_type == 'parallel':
                data = np.array(problem['data'])
                operation = problem.get('operation', 'parallel_sum')
                parallel_results = self.advanced_parallel_operations(data, operation)
                results['final_results']['parallel'] = parallel_results
                results['computation_steps'].append('parallel')

            # General numerical computation
            if 'arrays' in problem:
                arrays = [np.array(arr) for arr in problem['arrays']]
                operation = problem.get('array_operation', 'elementwise')
                array_results = self.advanced_array_operations(arrays, operation)
                results['final_results']['array_operations'] = array_results
                results['computation_steps'].append('array_operations')

        except Exception as e:
            results['error'] = str(e)

        # Performance metrics
        end_time = time.time()
        results['performance_metrics'] = {
            'computation_time': end_time - start_time,
            'steps_completed': len(results['computation_steps']),
            'results_count': len(results['final_results'])
        }

        return results

# Global instance
advanced_numpy_ops = AdvancedNumPyOperations()

def get_advanced_numpy_operations() -> AdvancedNumPyOperations:
    """Get the global advanced numpy operations instance"""
    return advanced_numpy_ops
