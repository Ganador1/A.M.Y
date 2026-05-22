"""
AXIOM Advanced SciPy Operations Module
Exploiting SciPy's full scientific computing capabilities
"""

import numpy as np

# SciPy imports are heavy (C extensions); import lazily and guard to make test collection faster.
try:
    import scipy as sp
    from scipy import optimize, integrate, linalg, sparse, signal, stats, ndimage, fft
    from scipy.sparse.linalg import LinearOperator, eigsh, svds
    from scipy.optimize import minimize, differential_evolution, basinhopping
    from scipy.integrate import solve_ivp, solve_bvp, odeint, quad
    from scipy.linalg import solve, inv, det, eig, svd, schur, lu, qr
    from scipy.signal import butter, filtfilt, find_peaks, welch, spectrogram
    from scipy.stats import norm, t, chi2, f, poisson, expon, gamma, beta
    from scipy.ndimage import gaussian_filter, median_filter, sobel, laplace
    from scipy.fft import fft, ifft, fft2, ifft2, fftfreq
    from scipy.interpolate import interp1d, interp2d, griddata, splrep, splev
    from scipy.special import erf, gamma as gamma_special, beta as beta_special, legendre, hermite
    from scipy.spatial import distance_matrix, KDTree, ConvexHull, Delaunay
    from scipy.cluster import hierarchy
    from scipy.io import savemat, loadmat, wavfile
    SCIPY_AVAILABLE = True
except Exception:
    # SciPy not available; set placeholders and delay import until runtime when needed
    sp = None
    optimize = integrate = linalg = sparse = signal = stats = ndimage = fft = None
    LinearOperator = eigsh = svds = None
    minimize = differential_evolution = basinhopping = None
    solve_ivp = solve_bvp = odeint = quad = None
    solve = inv = det = eig = svd = schur = lu = qr = None
    butter = filtfilt = find_peaks = welch = spectrogram = None
    norm = t = chi2 = f = poisson = expon = gamma_special = beta_special = None
    gaussian_filter = median_filter = sobel = laplace = None
    fft = ifft = fft2 = ifft2 = fftfreq = None
    interp1d = interp2d = griddata = splrep = splev = None
    erf = legendre = hermite = None
    distance_matrix = KDTree = ConvexHull = Delaunay = None
    hierarchy = None
    savemat = loadmat = wavfile = None
    SCIPY_AVAILABLE = False

import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass
import time
import warnings

logger = logging.getLogger(__name__)

@dataclass
class SciPyConfig:
    """Configuration for advanced SciPy operations"""
    optimization_method: str = 'L-BFGS-B'
    integration_method: str = 'RK45'
    linear_solver: str = 'auto'
    fft_backend: str = 'auto'
    sparse_solver: str = 'auto'
    numerical_precision: float = 1e-8
    max_iterations: int = 10000
    use_parallel: bool = True

class AdvancedSciPyOperations:
    """Advanced SciPy operations exploiting full scientific capabilities"""

    def __init__(self, config: Optional[SciPyConfig] = None):
        self.config = config or SciPyConfig()
        self._setup_fft_backend()
        self._setup_sparse_solver()

        logger.info("✅ Advanced SciPy Operations initialized")

    def _setup_fft_backend(self):
        """Setup FFT backend for optimal performance"""
        try:
            # Try to use pyfftw if available for better performance
            import pyfftw
            fft.set_backend(pyfftw.interfaces.scipy_fft)
            logger.info("Using pyfftw FFT backend")
        except ImportError:
            logger.info("Using default NumPy FFT backend")

    def _setup_sparse_solver(self):
        """Setup sparse linear algebra solver"""
        try:
            # Try to use MUMPS if available
            import pymumps
            logger.info("MUMPS sparse solver available")
        except ImportError:
            logger.info("Using default sparse solvers")

    def advanced_optimization(self, objective: Callable, bounds: List[Tuple],
                            constraints: Optional[List] = None,
                            method: Optional[str] = None) -> Dict[str, Any]:
        """Advanced multi-dimensional optimization with multiple algorithms"""
        results = {}
        method = method or self.config.optimization_method

        # Global optimization methods
        global_methods = ['differential_evolution', 'basinhopping', 'shgo', 'dual_annealing']

        for opt_method in [method] + global_methods:
            try:
                if opt_method == 'differential_evolution':
                    result = differential_evolution(objective, bounds,
                                                  maxiter=self.config.max_iterations)
                elif opt_method == 'basinhopping':
                    x0 = np.mean(bounds, axis=1)  # Initial guess at center
                    result = basinhopping(objective, x0,
                                        niter=self.config.max_iterations)
                elif opt_method == 'shgo':
                    result = optimize.shgo(objective, bounds,
                                         n=self.config.max_iterations)
                elif opt_method == 'dual_annealing':
                    result = optimize.dual_annealing(objective, bounds,
                                                   maxiter=self.config.max_iterations)
                else:
                    # Local optimization
                    x0 = np.mean(bounds, axis=1)
                    result = minimize(objective, x0, method=opt_method, bounds=bounds,
                                    constraints=constraints,
                                    options={'maxiter': self.config.max_iterations})

                results[opt_method] = {
                    'success': result.success,
                    'x': result.x.tolist() if hasattr(result, 'x') else None,
                    'fun': result.fun,
                    'nfev': getattr(result, 'nfev', None),
                    'message': getattr(result, 'message', '')
                }

            except Exception as e:
                results[opt_method] = {'error': str(e)}

        # Multi-objective optimization
        try:
            from scipy.optimize import NonlinearConstraint, LinearConstraint

            if constraints:
                # Convert constraints to scipy format
                scipy_constraints = []
                for constraint in constraints:
                    if constraint.get('type') == 'eq':
                        scipy_constraints.append(
                            NonlinearConstraint(constraint['fun'], 0, 0)
                        )
                    elif constraint.get('type') == 'ineq':
                        scipy_constraints.append(
                            NonlinearConstraint(constraint['fun'], 0, np.inf)
                        )

                result = minimize(objective, np.mean(bounds, axis=1),
                                method='SLSQP', bounds=bounds,
                                constraints=scipy_constraints)

                results['constrained'] = {
                    'success': result.success,
                    'x': result.x.tolist(),
                    'fun': result.fun
                }

        except Exception as e:
            results['constrained'] = {'error': str(e)}

        return results

    def advanced_integration(self, integrand: Callable, limits: List[Tuple],
                           method: Optional[str] = None) -> Dict[str, Any]:
        """Advanced numerical integration with multiple methods"""
        results = {}
        method = method or self.config.integration_method

        # Multiple integration methods
        methods = ['quad', 'romberg', 'adaptive', 'gauss']

        for int_method in methods:
            try:
                if int_method == 'quad':
                    if len(limits) == 1:
                        result = quad(integrand, limits[0][0], limits[0][1])
                    else:
                        # Multiple integration
                        result = integrate.nquad(integrand, limits)

                elif int_method == 'romberg':
                    if len(limits) == 1:
                        result = integrate.romberg(integrand, limits[0][0], limits[0][1])
                    else:
                        result = (np.nan, np.nan)  # Romberg doesn't support multiple integrals

                elif int_method == 'adaptive':
                    if len(limits) == 1:
                        result = integrate.quadrature(integrand, limits[0][0], limits[0][1])
                    else:
                        result = (np.nan, np.nan)

                elif int_method == 'gauss':
                    if len(limits) == 1:
                        result = integrate.fixed_quad(integrand, limits[0][0], limits[0][1])
                    else:
                        result = (np.nan, np.nan)

                if len(limits) == 1:
                    results[int_method] = {
                        'value': result[0],
                        'error': result[1] if len(result) > 1 else None
                    }
                else:
                    results[int_method] = {
                        'value': result[0],
                        'error': result[1] if len(result) > 1 else None
                    }

            except Exception as e:
                results[int_method] = {'error': str(e)}

        # ODE solving
        try:
            def ode_func(t, y):
                return integrand(t, y) if callable(integrand) else integrand

            if len(limits) == 1:
                t_span = (limits[0][0], limits[0][1])
                y0 = [0.0]  # Initial condition
                sol = solve_ivp(ode_func, t_span, y0, method=method)

                results['ode_solution'] = {
                    't': sol.t.tolist(),
                    'y': sol.y.tolist(),
                    'success': sol.success,
                    'message': sol.message
                }

        except Exception as e:
            results['ode_solution'] = {'error': str(e)}

        return results

    def advanced_linear_algebra(self, matrix: np.ndarray,
                              operation: str = 'solve') -> Dict[str, Any]:
        """Advanced linear algebra operations"""
        results = {}

        try:
            # Basic matrix properties
            results['shape'] = matrix.shape
            results['rank'] = np.linalg.matrix_rank(matrix)
            results['condition_number'] = np.linalg.cond(matrix)

            if operation == 'solve':
                # Solve linear system Ax = b
                if matrix.shape[0] == matrix.shape[1]:
                    b = np.ones(matrix.shape[0])
                    x = solve(matrix, b)
                    results['solution'] = x.tolist()

                    # Verify solution
                    residual = np.dot(matrix, x) - b
                    results['residual_norm'] = np.linalg.norm(residual)

            elif operation == 'eigen':
                # Eigenvalue decomposition
                eigenvals, eigenvecs = eig(matrix)
                results['eigenvalues'] = eigenvals.tolist()
                results['eigenvectors'] = eigenvecs.tolist()

                # Sort by absolute value
                idx = np.argsort(np.abs(eigenvals))[::-1]
                results['eigenvalues_sorted'] = eigenvals[idx].tolist()

            elif operation == 'svd':
                # Singular value decomposition
                U, s, Vt = svd(matrix)
                results['U'] = U.tolist()
                results['singular_values'] = s.tolist()
                results['Vt'] = Vt.tolist()

            elif operation == 'decomposition':
                # Matrix decompositions
                P, L, U = lu(matrix)
                results['LU_P'] = P.tolist()
                results['LU_L'] = L.tolist()
                results['LU_U'] = U.tolist()

                Q, R = qr(matrix)
                results['QR_Q'] = Q.tolist()
                results['QR_R'] = R.tolist()

                T, Z = schur(matrix)
                results['Schur_T'] = T.tolist()
                results['Schur_Z'] = Z.tolist()

            # Matrix norms
            results['frobenius_norm'] = np.linalg.norm(matrix, 'fro')
            results['spectral_norm'] = np.linalg.norm(matrix, 2)
            results['nuclear_norm'] = np.linalg.norm(matrix, 'nuc')

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_signal_processing(self, signal_data: np.ndarray,
                                 sampling_rate: float = 1000.0) -> Dict[str, Any]:
        """Advanced signal processing operations"""
        results = {}

        try:
            # Basic signal properties
            results['length'] = len(signal_data)
            results['mean'] = np.mean(signal_data)
            results['std'] = np.std(signal_data)
            results['rms'] = np.sqrt(np.mean(signal_data**2))

            # Filtering
            nyquist = sampling_rate / 2
            cutoff = nyquist * 0.1  # Low-pass filter

            b, a = butter(4, cutoff/nyquist, btype='low')
            filtered_signal = filtfilt(b, a, signal_data)
            results['filtered_signal'] = filtered_signal.tolist()

            # Peak detection
            peaks, properties = find_peaks(signal_data, height=np.mean(signal_data))
            results['peaks'] = {
                'indices': peaks.tolist(),
                'heights': properties['peak_heights'].tolist() if 'peak_heights' in properties else []
            }

            # Spectral analysis
            frequencies, psd = welch(signal_data, fs=sampling_rate, nperseg=1024)
            results['power_spectral_density'] = {
                'frequencies': frequencies.tolist(),
                'psd': psd.tolist()
            }

            # Spectrogram
            f, t, Sxx = spectrogram(signal_data, fs=sampling_rate, nperseg=256)
            results['spectrogram'] = {
                'frequencies': f.tolist(),
                'times': t.tolist(),
                'spectrogram': Sxx.tolist()
            }

            # Autocorrelation
            autocorr = np.correlate(signal_data, signal_data, mode='full')
            autocorr = autocorr[autocorr.size // 2:]  # Take second half
            results['autocorrelation'] = autocorr.tolist()

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_statistics(self, data: np.ndarray,
                          distribution: str = 'normal') -> Dict[str, Any]:
        """Advanced statistical analysis"""
        results = {}

        try:
            # Basic statistics
            results['mean'] = np.mean(data)
            results['median'] = np.median(data)
            results['std'] = np.std(data)
            results['variance'] = np.var(data)
            results['skewness'] = stats.skew(data)
            results['kurtosis'] = stats.kurtosis(data)

            # Distribution fitting
            if distribution == 'normal':
                params = stats.norm.fit(data)
                results['normal_fit'] = {
                    'mu': params[0],
                    'sigma': params[1]
                }

                # Goodness of fit
                _, p_value = stats.normaltest(data)
                results['normality_test'] = {
                    'p_value': p_value,
                    'is_normal': p_value > 0.05
                }

            elif distribution == 't':
                df, loc, scale = stats.t.fit(data)
                results['t_fit'] = {
                    'df': df,
                    'loc': loc,
                    'scale': scale
                }

            # Hypothesis testing
            _, p_value = stats.ttest_1samp(data, 0)
            results['t_test'] = {
                'p_value': p_value,
                'significant': p_value < 0.05
            }

            # Confidence intervals
            mean, std = np.mean(data), np.std(data)
            n = len(data)
            se = std / np.sqrt(n)
            ci_lower = mean - 1.96 * se
            ci_upper = mean + 1.96 * se
            results['confidence_interval_95'] = {
                'lower': ci_lower,
                'upper': ci_upper
            }

            # Bootstrap confidence interval
            bootstrap_means = []
            for _ in range(1000):
                sample = np.random.choice(data, size=n, replace=True)
                bootstrap_means.append(np.mean(sample))

            results['bootstrap_ci_95'] = {
                'lower': np.percentile(bootstrap_means, 2.5),
                'upper': np.percentile(bootstrap_means, 97.5)
            }

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_image_processing(self, image: np.ndarray) -> Dict[str, Any]:
        """Advanced image processing operations"""
        results = {}

        try:
            # Basic image properties
            results['shape'] = image.shape
            results['dtype'] = str(image.dtype)
            results['min_value'] = np.min(image)
            results['max_value'] = np.max(image)
            results['mean_value'] = np.mean(image)

            # Filtering
            gaussian_filtered = gaussian_filter(image, sigma=1)
            results['gaussian_filtered'] = gaussian_filtered.tolist()

            median_filtered = median_filter(image, size=3)
            results['median_filtered'] = median_filtered.tolist()

            # Edge detection
            sobel_x = sobel(image, axis=0)
            sobel_y = sobel(image, axis=1)
            sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            results['sobel_edges'] = sobel_magnitude.tolist()

            # Laplacian
            laplacian = laplace(image)
            results['laplacian'] = laplacian.tolist()

            # Morphological operations
            from scipy.ndimage import binary_opening, binary_closing

            # Thresholding
            threshold = np.mean(image)
            binary = image > threshold
            results['binary_threshold'] = binary.tolist()

            # Connected components
            from scipy.ndimage import label
            labeled, num_features = label(binary)
            results['connected_components'] = {
                'labeled_image': labeled.tolist(),
                'num_features': num_features
            }

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_fft_analysis(self, signal: np.ndarray,
                            sampling_rate: float = 1000.0) -> Dict[str, Any]:
        """Advanced Fast Fourier Transform analysis"""
        results = {}

        try:
            # 1D FFT
            fft_result = fft(signal)
            frequencies = fftfreq(len(signal), 1/sampling_rate)

            results['fft_1d'] = {
                'frequencies': frequencies.tolist(),
                'magnitude': np.abs(fft_result).tolist(),
                'phase': np.angle(fft_result).tolist(),
                'power': (np.abs(fft_result)**2).tolist()
            }

            # 2D FFT (if signal is 2D)
            if signal.ndim == 2:
                fft_2d = fft2(signal)
                results['fft_2d'] = {
                    'magnitude': np.abs(fft_2d).tolist(),
                    'phase': np.angle(fft_2d).tolist()
                }

            # Windowed FFT
            from scipy.signal import windows
            window = windows.hann(len(signal))
            windowed_signal = signal * window
            windowed_fft = fft(windowed_signal)

            results['windowed_fft'] = {
                'window': window.tolist(),
                'magnitude': np.abs(windowed_fft).tolist()
            }

            # Short-time Fourier transform
            from scipy.signal import stft
            f, t, Zxx = stft(signal, fs=sampling_rate, nperseg=256)
            results['stft'] = {
                'frequencies': f.tolist(),
                'times': t.tolist(),
                'spectrogram': np.abs(Zxx).tolist()
            }

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_interpolation(self, x_data: np.ndarray, y_data: np.ndarray,
                             x_new: np.ndarray, method: str = 'cubic') -> Dict[str, Any]:
        """Advanced interpolation methods"""
        results = {}

        try:
            # Linear interpolation
            linear_interp = interp1d(x_data, y_data, kind='linear')
            results['linear'] = linear_interp(x_new).tolist()

            # Cubic spline interpolation
            cubic_interp = interp1d(x_data, y_data, kind='cubic')
            results['cubic'] = cubic_interp(x_new).tolist()

            # Spline interpolation with control
            tck = splrep(x_data, y_data, s=0)
            results['spline'] = splev(x_new, tck).tolist()

            # Radial basis function interpolation
            from scipy.interpolate import Rbf
            rbf_interp = Rbf(x_data, y_data, function='multiquadric')
            results['rbf'] = rbf_interp(x_new).tolist()

            # Polynomial interpolation
            poly_coeffs = np.polyfit(x_data, y_data, 3)
            poly_interp = np.polyval(poly_coeffs, x_new)
            results['polynomial'] = poly_interp.tolist()

            # 2D interpolation (if applicable)
            if len(x_data.shape) == 2 and len(y_data.shape) == 2:
                grid_interp = interp2d(x_data[:, 0], x_data[:, 1], y_data, kind='cubic')
                results['2d_interpolation'] = 'Available for 2D data'

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_special_functions(self, x: Union[float, np.ndarray],
                                 function: str = 'bessel') -> Dict[str, Any]:
        """Advanced special functions evaluation"""
        results = {}

        try:
            x_array = np.asarray(x)

            # Error function
            results['erf'] = erf(x_array).tolist()

            # Gamma function
            results['gamma'] = gamma(x_array).tolist()

            # Beta function
            if np.all(x_array > 0):
                results['beta'] = beta(x_array, x_array).tolist()

            # Legendre polynomials
            results['legendre_p2'] = legendre(2)(x_array).tolist()

            # Hermite polynomials
            results['hermite_h2'] = hermite(2)(x_array).tolist()

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_spatial_analysis(self, points: np.ndarray) -> Dict[str, Any]:
        """Advanced spatial analysis operations"""
        results = {}

        try:
            # Distance matrix
            dist_matrix = distance_matrix(points, points)
            results['distance_matrix'] = dist_matrix.tolist()

            # K-d tree for nearest neighbor search
            kdtree = KDTree(points)
            distances, indices = kdtree.query(points, k=3)  # 3 nearest neighbors
            results['nearest_neighbors'] = {
                'distances': distances.tolist(),
                'indices': indices.tolist()
            }

            # Convex hull
            if points.shape[1] == 2:  # 2D points
                hull = ConvexHull(points)
                results['convex_hull'] = {
                    'vertices': hull.vertices.tolist(),
                    'area': hull.area,
                    'volume': hull.volume
                }

                # Delaunay triangulation
                tri = Delaunay(points)
                results['delaunay'] = {
                    'simplices': tri.simplices.tolist(),
                    'neighbors': tri.neighbors.tolist()
                }

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_clustering(self, data: np.ndarray, n_clusters: int = 3) -> Dict[str, Any]:
        """Advanced clustering analysis"""
        results = {}

        try:
            # Hierarchical clustering
            linkage_matrix = hierarchy.linkage(data, method='ward')
            results['hierarchical'] = {
                'linkage_matrix': linkage_matrix.tolist()
            }

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_sparse_operations(self, matrix: sparse.spmatrix) -> Dict[str, Any]:
        """Advanced sparse matrix operations"""
        results = {}

        try:
            # Sparse matrix properties
            results['shape'] = matrix.shape
            results['nnz'] = matrix.nnz
            results['density'] = matrix.nnz / (matrix.shape[0] * matrix.shape[1])
            results['format'] = matrix.format

            # Eigenvalue computation for sparse matrices
            if matrix.shape[0] == matrix.shape[1]:
                eigenvals, eigenvecs = eigsh(matrix, k=min(10, matrix.shape[0]-1))
                results['eigenvalues'] = eigenvals.tolist()

            # SVD for sparse matrices
            U, s, Vt = svds(matrix, k=min(10, min(matrix.shape)-1))
            results['singular_values'] = s.tolist()

            # Sparse matrix-vector multiplication
            v = np.ones(matrix.shape[1])
            result = matrix @ v
            results['matrix_vector_product'] = result.tolist()

        except Exception as e:
            results['error'] = str(e)

        return results

    def scientific_computation_pipeline(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Complete scientific computation pipeline"""
        results = {
            'original_problem': problem,
            'computation_steps': [],
            'final_results': {},
            'performance_metrics': {}
        }

        start_time = time.time()

        try:
            problem_type = problem.get('type', 'general')

            if problem_type == 'optimization':
                objective = problem['objective']
                bounds = problem['bounds']
                opt_results = self.advanced_optimization(objective, bounds)
                results['final_results']['optimization'] = opt_results
                results['computation_steps'].append('optimization')

            elif problem_type == 'integration':
                integrand = problem['integrand']
                limits = problem['limits']
                int_results = self.advanced_integration(integrand, limits)
                results['final_results']['integration'] = int_results
                results['computation_steps'].append('integration')

            elif problem_type == 'linear_algebra':
                matrix = np.array(problem['matrix'])
                operation = problem.get('operation', 'solve')
                la_results = self.advanced_linear_algebra(matrix, operation)
                results['final_results']['linear_algebra'] = la_results
                results['computation_steps'].append('linear_algebra')

            elif problem_type == 'signal_processing':
                signal_data = np.array(problem['signal'])
                sampling_rate = problem.get('sampling_rate', 1000.0)
                sp_results = self.advanced_signal_processing(signal_data, sampling_rate)
                results['final_results']['signal_processing'] = sp_results
                results['computation_steps'].append('signal_processing')

            elif problem_type == 'statistics':
                data = np.array(problem['data'])
                distribution = problem.get('distribution', 'normal')
                stat_results = self.advanced_statistics(data, distribution)
                results['final_results']['statistics'] = stat_results
                results['computation_steps'].append('statistics')

            elif problem_type == 'fft':
                signal = np.array(problem['signal'])
                sampling_rate = problem.get('sampling_rate', 1000.0)
                fft_results = self.advanced_fft_analysis(signal, sampling_rate)
                results['final_results']['fft'] = fft_results
                results['computation_steps'].append('fft')

            # General scientific computation
            if 'data' in problem:
                data = np.array(problem['data'])

                # Apply multiple analyses
                if data.ndim == 1:
                    # 1D signal analysis
                    results['final_results']['signal_analysis'] = self.advanced_signal_processing(data)
                    results['final_results']['fft_analysis'] = self.advanced_fft_analysis(data)
                    results['final_results']['statistics'] = self.advanced_statistics(data)

                elif data.ndim == 2 and data.shape[1] <= 3:
                    # Spatial data analysis
                    results['final_results']['spatial_analysis'] = self.advanced_spatial_analysis(data)
                    results['final_results']['clustering'] = self.advanced_clustering(data)

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
advanced_scipy_ops = AdvancedSciPyOperations()

def get_advanced_scipy_operations() -> AdvancedSciPyOperations:
    """Get the global advanced scipy operations instance"""
    return advanced_scipy_ops
