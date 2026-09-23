"""
AXIOM - Servicio de Fotometría de Apertura Óptima
Fotometría automática con optimización de apertura, corrección de fondo y estimación de ruido
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from app.exceptions.domain.biology import BiologyError

try:
    from scipy import optimize, ndimage
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy no está disponible. Funcionalidad limitada.")

try:
    from photutils.aperture import aperture_photometry, CircularAperture, CircularAnnulus
    from photutils.background import Background2D, MedianBackground
    from photutils.detection import DAOStarFinder
    PHOTUTILS_AVAILABLE = True
except ImportError:
    PHOTUTILS_AVAILABLE = False
    logging.warning("Photutils no está disponible. Funcionalidad de fotometría limitada.")

try:
    from astropy.stats import SigmaClip, sigma_clipped_stats
    from astropy.modeling import models, fitting
    ASTROPY_AVAILABLE = True
except ImportError:
    ASTROPY_AVAILABLE = False
    logging.warning("Astropy no está disponible. Funcionalidad limitada.")


class ApertureOptimizationMethod(Enum):
    """Métodos de optimización de apertura"""
    SNR_MAXIMIZATION = "snr_maximization"
    CURVE_OF_GROWTH = "curve_of_growth"
    SEEING_BASED = "seeing_based"
    PROFILE_FITTING = "profile_fitting"
    ERROR_MINIMIZATION = "error_minimization"


class BackgroundEstimationMethod(Enum):
    """Métodos de estimación de fondo"""
    MEDIAN_FILTER = "median_filter"
    MEAN_FILTER = "mean_filter"
    SIGMA_CLIPPED_MEDIAN = "sigma_clipped_median"
    ANNULUS = "annulus"
    MESH_INTERPOLATION = "mesh_interpolation"
    SOURCE_MASK = "source_mask"


@dataclass
class PhotometryAperture:
    """Definición de apertura fotométrica"""
    center_x: float
    center_y: float
    radius: float
    background_inner_radius: float
    background_outer_radius: float
    optimization_method: ApertureOptimizationMethod
    seeing_fwhm: Optional[float] = None


@dataclass
class PhotometryResult:
    """Resultado de medición fotométrica"""
    source_flux: float
    source_flux_error: float
    background_flux: float
    background_flux_error: float
    background_rms: float
    aperture_area: float
    background_area: float
    snr: float
    magnitude: float
    magnitude_error: float
    aperture_correction: float


@dataclass
class OptimalApertureResults:
    """Resultados de optimización de apertura"""
    optimal_radius: float
    optimization_curve: List[float]
    test_radii: List[float]
    snr_values: List[float]
    flux_values: List[float]
    error_values: List[float]
    seeing_estimate: float
    background_stats: Dict[str, float]


class OptimalAperturePhotometryService:
    """
    Servicio para fotometría automática con apertura óptima

    Capacidades:
    - Optimización automática de radio de apertura
    - Múltiples métodos de estimación de fondo
    - Corrección de apertura automática
    - Estimación de ruido precisa
    - Detección automática de seeing
    - Fotometría de fuentes múltiples
    - Análisis de curva de crecimiento
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        if not SCIPY_AVAILABLE:
            self.logger.error("SciPy no disponible. Funcionalidad limitada.")

        if not PHOTUTILS_AVAILABLE:
            self.logger.error("Photutils no disponible. Funcionalidad de fotometría muy limitada.")

        if not ASTROPY_AVAILABLE:
            self.logger.error("Astropy no disponible. Funcionalidad limitada.")

        # Configurar parámetros por defecto
        self._setup_default_parameters()

        self.logger.info("OptimalAperturePhotometryService inicializado correctamente")

    def _setup_default_parameters(self):
        """Configura parámetros por defecto"""
        self.default_params = {
            'aperture_range': (1.0, 10.0),  # rango de radios a probar (píxeles)
            'aperture_steps': 20,  # número de radios a probar
            'background_annulus_factor': (2.5, 4.0),  # factores para anillo de fondo
            'sigma_clip': (3.0, 5),  # sigma y iteraciones para clipping
            'source_detection_threshold': 5.0,  # umbral sigma para detección
            'seeing_estimation_percentile': 80,  # percentil para estimación de seeing
            'aperture_correction_radius': 20.0,  # radio para corrección de apertura
            'minimum_snr': 3.0,  # SNR mínimo requerido
            'saturation_threshold': 50000,  # umbral de saturación
            'contamination_radius': 5.0  # radio para detectar contaminación
        }

    def detect_sources_automatically(
        self,
        image: np.ndarray,
        threshold_sigma: float = 5.0,
        fwhm_estimate: float = 3.0,
        max_sources: int = 100
    ) -> List[Dict[str, float]]:
        """
        Detecta fuentes automáticamente en la imagen

        Args:
            image: Imagen 2D
            threshold_sigma: Umbral de detección en sigma
            fwhm_estimate: Estimación inicial de FWHM
            max_sources: Número máximo de fuentes a detectar

        Returns:
            Lista de fuentes detectadas con posiciones y propiedades
        """
        if not PHOTUTILS_AVAILABLE:
            raise ImportError("Photutils no disponible")

        # Estimación rápida de fondo y ruido
        sigma_clip = SigmaClip(sigma=3.0)
        bkg_estimator = MedianBackground()
        bkg = Background2D(image, (50, 50), filter_size=(3, 3),
                          sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)

        # Detectar fuentes
        daofind = DAOStarFinder(fwhm=fwhm_estimate, threshold=threshold_sigma * bkg.background_rms_median)
        sources = daofind(image - bkg.background)

        if sources is None:
            return []

        # Limitar número de fuentes y ordenar por flujo
        sources.sort('flux')
        sources.reverse()
        sources = sources[:max_sources]

        # Convertir a lista de diccionarios
        detected_sources = []
        for source in sources:
            detected_sources.append({
                'x': float(source['xcentroid']),
                'y': float(source['ycentroid']),
                'flux': float(source['flux']),
                'peak': float(source['peak']),
                'fwhm': fwhm_estimate
            })

        self.logger.info(f"Detectadas {len(detected_sources)} fuentes automáticamente")
        return detected_sources

    def estimate_seeing(
        self,
        image: np.ndarray,
        sources: Optional[List[Dict[str, float]]] = None,
        percentile: float = 80
    ) -> float:
        """
        Estima el seeing (FWHM) de la imagen

        Args:
            image: Imagen 2D
            sources: Lista de fuentes (opcional, se detectan automáticamente)
            percentile: Percentil para estadística robusta

        Returns:
            FWHM estimado en píxeles
        """
        if sources is None:
            sources = self.detect_sources_automatically(image, max_sources=20)

        if not sources:
            self.logger.warning("No se encontraron fuentes para estimar seeing")
            return 3.0  # valor por defecto

        fwhm_measurements = []

        for source in sources[:10]:  # usar solo las 10 mejores fuentes
            try:
                fwhm = self._measure_source_fwhm(
                    image, source['x'], source['y'],
                    aperture_size=15
                )
                if 1.0 < fwhm < 20.0:  # filtrar valores razonables
                    fwhm_measurements.append(fwhm)
            except BiologyError as e:
                self.logger.debug(f"Error midiendo FWHM en ({source['x']}, {source['y']}): {e}")
                continue

        if not fwhm_measurements:
            self.logger.warning("No se pudieron medir FWHM válidos")
            return 3.0

        # Usar percentil para estadística robusta
        seeing_fwhm = np.percentile(fwhm_measurements, percentile)

        self.logger.info(f"Seeing estimado: {seeing_fwhm:.2f} píxeles")
        return float(seeing_fwhm)

    def optimize_aperture_radius(
        self,
        image: np.ndarray,
        center_x: float,
        center_y: float,
        method: ApertureOptimizationMethod = ApertureOptimizationMethod.SNR_MAXIMIZATION,
        seeing_fwhm: Optional[float] = None,
        radius_range: Optional[tuple] = None
    ) -> OptimalApertureResults:
        """
        Optimiza el radio de apertura para una fuente

        Args:
            image: Imagen 2D
            center_x: Posición X de la fuente
            center_y: Posición Y de la fuente
            method: Método de optimización
            seeing_fwhm: FWHM conocido (opcional)
            radius_range: Rango de radios a probar (opcional)

        Returns:
            OptimalApertureResults con radio óptimo y curvas
        """
        if not PHOTUTILS_AVAILABLE:
            raise ImportError("Photutils no disponible")

        # Estimar seeing si no se proporciona
        if seeing_fwhm is None:
            seeing_fwhm = self.estimate_seeing(image)

        # Definir rango de radios a probar
        if radius_range is None:
            min_radius = max(0.5 * seeing_fwhm, 1.0)
            max_radius = min(5.0 * seeing_fwhm, 15.0)
            radius_range = (min_radius, max_radius)

        test_radii = np.linspace(radius_range[0], radius_range[1],
                                self.default_params['aperture_steps'])

        # Arrays para almacenar resultados
        snr_values = []
        flux_values = []
        error_values = []

        # Estimar fondo una vez
        background_stats = self._estimate_background(image, center_x, center_y,
                                                   radius_range[1] * 2)

        for radius in test_radii:
            try:
                # Realizar fotometría con este radio
                photometry = self._perform_aperture_photometry(
                    image, center_x, center_y, radius,
                    background_stats=background_stats
                )

                snr_values.append(photometry.snr)
                flux_values.append(photometry.source_flux)
                error_values.append(photometry.source_flux_error)

            except BiologyError as e:
                self.logger.debug(f"Error en fotometría con radio {radius:.2f}: {e}")
                snr_values.append(0.0)
                flux_values.append(0.0)
                error_values.append(np.inf)

        # Aplicar método de optimización
        optimal_radius = self._apply_optimization_method(
            method, test_radii, snr_values, flux_values, error_values, seeing_fwhm
        )

        return OptimalApertureResults(
            optimal_radius=float(optimal_radius),
            optimization_curve=flux_values.copy(),
            test_radii=test_radii.tolist(),
            snr_values=snr_values.copy(),
            flux_values=flux_values.copy(),
            error_values=error_values.copy(),
            seeing_estimate=float(seeing_fwhm),
            background_stats=background_stats
        )

    def perform_optimal_photometry(
        self,
        image: np.ndarray,
        center_x: float,
        center_y: float,
        method: ApertureOptimizationMethod = ApertureOptimizationMethod.SNR_MAXIMIZATION,
        background_method: BackgroundEstimationMethod = BackgroundEstimationMethod.ANNULUS,
        apply_aperture_correction: bool = True
    ) -> PhotometryResult:
        """
        Realiza fotometría con apertura optimizada

        Args:
            image: Imagen 2D
            center_x: Posición X de la fuente
            center_y: Posición Y de la fuente
            method: Método de optimización de apertura
            background_method: Método de estimación de fondo
            apply_aperture_correction: Si aplicar corrección de apertura

        Returns:
            PhotometryResult con mediciones optimizadas
        """
        # Optimizar apertura
        optimization_results = self.optimize_aperture_radius(
            image, center_x, center_y, method
        )

        optimal_radius = optimization_results.optimal_radius

        # Realizar fotometría con apertura óptima
        photometry = self._perform_aperture_photometry(
            image, center_x, center_y, optimal_radius,
            background_method=background_method
        )

        # Aplicar corrección de apertura si se solicita
        if apply_aperture_correction:
            correction = self._calculate_aperture_correction(
                image, center_x, center_y, optimal_radius,
                optimization_results.seeing_estimate
            )
            photometry.aperture_correction = correction
            photometry.source_flux *= correction
            photometry.magnitude -= 2.5 * np.log10(correction)

        return photometry

    def multi_source_photometry(
        self,
        image: np.ndarray,
        sources: List[Dict[str, float]],
        method: ApertureOptimizationMethod = ApertureOptimizationMethod.SNR_MAXIMIZATION,
        optimize_individually: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> List[PhotometryResult]:
        """
        Fotometría optimizada para múltiples fuentes

        Args:
            image: Imagen 2D
            sources: Lista de fuentes con posiciones
            method: Método de optimización
            optimize_individually: Si optimizar cada fuente individualmente
            progress_callback: Función de callback para progreso (opcional)

        Returns:
            Lista de PhotometryResult para cada fuente
        """
        results = []

        # Estimar seeing global si no se optimiza individualmente
        global_seeing = None
        if not optimize_individually:
            global_seeing = self.estimate_seeing(image, sources)

        for i, source in enumerate(sources):
            try:
                if optimize_individually or global_seeing is None:
                    # Optimizar apertura individualmente
                    photometry = self.perform_optimal_photometry(
                        image, source['x'], source['y'], method
                    )
                else:
                    # Usar radio basado en seeing global
                    optimal_radius = global_seeing * 1.5  # factor típico
                    photometry = self._perform_aperture_photometry(
                        image, source['x'], source['y'], optimal_radius
                    )

                results.append(photometry)

                # Callback de progreso
                if progress_callback:
                    progress_callback(i + 1, len(sources))

            except BiologyError as e:
                self.logger.warning(f"Error en fotometría de fuente {i}: {e}")
                # Crear resultado con valores nulos
                null_result = PhotometryResult(
                    source_flux=0.0, source_flux_error=np.inf,
                    background_flux=0.0, background_flux_error=np.inf,
                    background_rms=0.0, aperture_area=0.0, background_area=0.0,
                    snr=0.0, magnitude=np.inf, magnitude_error=np.inf,
                    aperture_correction=1.0
                )
                results.append(null_result)

        self.logger.info(f"Fotometría completada para {len(results)} fuentes")
        return results

    def _measure_source_fwhm(
        self,
        image: np.ndarray,
        center_x: float,
        center_y: float,
        aperture_size: int = 15
    ) -> float:
        """Mide FWHM de una fuente mediante ajuste gaussiano"""
        if not ASTROPY_AVAILABLE:
            return 3.0  # valor por defecto

        # Extraer subimagen
        x_int, y_int = int(center_x), int(center_y)
        half_size = aperture_size // 2

        y_slice = slice(max(0, y_int - half_size),
                       min(image.shape[0], y_int + half_size + 1))
        x_slice = slice(max(0, x_int - half_size),
                       min(image.shape[1], x_int + half_size + 1))

        subimage = image[y_slice, x_slice]

        if subimage.size == 0:
            return 3.0

        # Crear grilla de coordenadas
        y_grid, x_grid = np.mgrid[0:subimage.shape[0], 0:subimage.shape[1]]

        # Estimar parámetros iniciales
        bg_level = np.median(subimage)
        peak = np.max(subimage) - bg_level
        y_center = subimage.shape[0] / 2.0
        x_center = subimage.shape[1] / 2.0

        # Crear modelo gaussiano 2D
        gaussian_model = models.Gaussian2D(
            amplitude=peak, x_mean=x_center, y_mean=y_center,
            x_stddev=1.5, y_stddev=1.5
        ) + models.Const2D(amplitude=bg_level)

        # Ajustar modelo
        fitter = fitting.LevMarLSQFitter()
        try:
            fitted_model = fitter(gaussian_model, x_grid, y_grid, subimage)

            # Extraer FWHM (promedio de x e y)
            x_stddev = fitted_model.x_stddev_0.value
            y_stddev = fitted_model.y_stddev_0.value
            fwhm = 2.355 * np.sqrt(x_stddev * y_stddev)  # FWHM geométrico

            return float(fwhm)

        except BiologyError:
            # Si falla el ajuste, usar método de momentos
            return self._estimate_fwhm_moments(subimage)

    def _estimate_fwhm_moments(self, subimage: np.ndarray) -> float:
        """Estima FWHM usando momentos de la imagen"""
        # Método simple basado en momentos de segundo orden
        bg_level = np.percentile(subimage, 10)
        signal = subimage - bg_level
        signal = np.maximum(signal, 0)

        if np.sum(signal) == 0:
            return 3.0

        # Calcular momentos
        y_indices, x_indices = np.mgrid[0:signal.shape[0], 0:signal.shape[1]]

        total_signal = np.sum(signal)
        x_mean = np.sum(x_indices * signal) / total_signal
        y_mean = np.sum(y_indices * signal) / total_signal

        x_var = np.sum((x_indices - x_mean)**2 * signal) / total_signal
        y_var = np.sum((y_indices - y_mean)**2 * signal) / total_signal

        # Convertir varianza a FWHM
        fwhm = 2.355 * np.sqrt((x_var + y_var) / 2)
        return float(fwhm)

    def _estimate_background(
        self,
        image: np.ndarray,
        center_x: float,
        center_y: float,
        exclude_radius: float,
        method: BackgroundEstimationMethod = BackgroundEstimationMethod.ANNULUS
    ) -> Dict[str, float]:
        """Estima estadísticas del fondo"""
        if method == BackgroundEstimationMethod.ANNULUS:
            return self._estimate_background_annulus(
                image, center_x, center_y, exclude_radius
            )
        elif method == BackgroundEstimationMethod.SIGMA_CLIPPED_MEDIAN:
            return self._estimate_background_sigma_clipped(image)
        else:
            # Método por defecto: anillo
            return self._estimate_background_annulus(
                image, center_x, center_y, exclude_radius
            )

    def _estimate_background_annulus(
        self,
        image: np.ndarray,
        center_x: float,
        center_y: float,
        exclude_radius: float
    ) -> Dict[str, float]:
        """Estima fondo usando anillo alrededor de la fuente"""
        inner_radius = exclude_radius * 2.5
        outer_radius = exclude_radius * 4.0

        if not PHOTUTILS_AVAILABLE:
            # Método simple sin photutils
            y_indices, x_indices = np.mgrid[0:image.shape[0], 0:image.shape[1]]
            distances = np.sqrt((x_indices - center_x)**2 + (y_indices - center_y)**2)

            annulus_mask = (distances >= inner_radius) & (distances <= outer_radius)
            annulus_pixels = image[annulus_mask]

            if len(annulus_pixels) == 0:
                return {'mean': 0.0, 'median': 0.0, 'std': 1.0, 'area': 0.0}

            return {
                'mean': float(np.mean(annulus_pixels)),
                'median': float(np.median(annulus_pixels)),
                'std': float(np.std(annulus_pixels)),
                'area': float(len(annulus_pixels))
            }

        # Usar photutils
        annulus_aperture = CircularAnnulus((center_x, center_y),
                                         r_in=inner_radius, r_out=outer_radius)
        annulus_mask = annulus_aperture.to_mask(method='center')
        annulus_data = annulus_mask.multiply(image)
        annulus_data_1d = annulus_data[annulus_mask.data > 0]

        if len(annulus_data_1d) == 0:
            return {'mean': 0.0, 'median': 0.0, 'std': 1.0, 'area': 0.0}

        # Aplicar sigma clipping
        if ASTROPY_AVAILABLE:
            sigma_clip = SigmaClip(sigma=3.0, maxiters=5)
            mean, median, std = sigma_clipped_stats(annulus_data_1d, sigma_clip=sigma_clip)
        else:
            mean = np.mean(annulus_data_1d)
            median = np.median(annulus_data_1d)
            std = np.std(annulus_data_1d)

        return {
            'mean': float(mean),
            'median': float(median),
            'std': float(std),
            'area': float(len(annulus_data_1d))
        }

    def _estimate_background_sigma_clipped(self, image: np.ndarray) -> Dict[str, float]:
        """Estima fondo usando sigma clipping global"""
        if ASTROPY_AVAILABLE:
            sigma_clip = SigmaClip(sigma=3.0, maxiters=10)
            mean, median, std = sigma_clipped_stats(image, sigma_clip=sigma_clip)
        else:
            # Método simple sin astropy
            flat_image = image.flatten()
            median = np.median(flat_image)
            mad = np.median(np.abs(flat_image - median))
            std = mad * 1.4826  # conversión MAD a std

            # Filtrar outliers
            mask = np.abs(flat_image - median) < 3 * std
            mean = np.mean(flat_image[mask])

        return {
            'mean': float(mean),
            'median': float(median),
            'std': float(std),
            'area': float(image.size)
        }

    def _perform_aperture_photometry(
        self,
        image: np.ndarray,
        center_x: float,
        center_y: float,
        radius: float,
        background_method: BackgroundEstimationMethod = BackgroundEstimationMethod.ANNULUS,
        background_stats: Optional[Dict[str, float]] = None
    ) -> PhotometryResult:
        """Realiza fotometría de apertura básica"""
        if not PHOTUTILS_AVAILABLE:
            # Implementación básica sin photutils
            return self._basic_aperture_photometry(
                image, center_x, center_y, radius, background_stats
            )

        # Crear apertura
        aperture = CircularAperture((center_x, center_y), r=radius)

        # Realizar fotometría
        phot_table = aperture_photometry(image, aperture)
        source_flux = float(phot_table['aperture_sum'][0])

        # Estimar fondo si no se proporciona
        if background_stats is None:
            background_stats = self._estimate_background(
                image, center_x, center_y, radius, background_method
            )

        # Corrección de fondo
        aperture_area = np.pi * radius**2
        background_flux_total = background_stats['median'] * aperture_area
        source_flux_corrected = source_flux - background_flux_total

        # Estimación de errores
        background_error = background_stats['std'] * np.sqrt(aperture_area)
        if ASTROPY_AVAILABLE and hasattr(image, 'uncertainty'):
            # Si la imagen tiene incertidumbres, usarlas
            source_error = np.sqrt(source_flux_corrected + background_error**2)
        else:
            # Asumir ruido poissoniano + fondo
            source_error = np.sqrt(abs(source_flux_corrected) + background_error**2)

        # Calcular SNR y magnitud
        snr = source_flux_corrected / source_error if source_error > 0 else 0.0

        if source_flux_corrected > 0:
            magnitude = -2.5 * np.log10(source_flux_corrected)
            magnitude_error = 1.0857 * source_error / source_flux_corrected
        else:
            magnitude = np.inf
            magnitude_error = np.inf

        return PhotometryResult(
            source_flux=float(source_flux_corrected),
            source_flux_error=float(source_error),
            background_flux=float(background_stats['median']),
            background_flux_error=float(background_stats['std']),
            background_rms=float(background_stats['std']),
            aperture_area=float(aperture_area),
            background_area=float(background_stats['area']),
            snr=float(snr),
            magnitude=float(magnitude),
            magnitude_error=float(magnitude_error),
            aperture_correction=1.0
        )

    def _basic_aperture_photometry(
        self,
        image: np.ndarray,
        center_x: float,
        center_y: float,
        radius: float,
        background_stats: Optional[Dict[str, float]]
    ) -> PhotometryResult:
        """Fotometría básica sin dependencias externas"""
        # Crear máscara circular
        y_indices, x_indices = np.mgrid[0:image.shape[0], 0:image.shape[1]]
        distances = np.sqrt((x_indices - center_x)**2 + (y_indices - center_y)**2)
        aperture_mask = distances <= radius

        # Flujo total en apertura
        source_flux = np.sum(image[aperture_mask])
        aperture_area = np.sum(aperture_mask)

        # Estimar fondo si no se proporciona
        if background_stats is None:
            background_stats = self._estimate_background(
                image, center_x, center_y, radius
            )

        # Corrección de fondo
        background_flux_total = background_stats['median'] * aperture_area
        source_flux_corrected = source_flux - background_flux_total

        # Estimación de errores (simple)
        background_error = background_stats['std'] * np.sqrt(aperture_area)
        source_error = np.sqrt(abs(source_flux_corrected) + background_error**2)

        # SNR y magnitud
        snr = source_flux_corrected / source_error if source_error > 0 else 0.0

        if source_flux_corrected > 0:
            magnitude = -2.5 * np.log10(source_flux_corrected)
            magnitude_error = 1.0857 * source_error / source_flux_corrected
        else:
            magnitude = np.inf
            magnitude_error = np.inf

        return PhotometryResult(
            source_flux=float(source_flux_corrected),
            source_flux_error=float(source_error),
            background_flux=float(background_stats['median']),
            background_flux_error=float(background_stats['std']),
            background_rms=float(background_stats['std']),
            aperture_area=float(aperture_area),
            background_area=float(background_stats['area']),
            snr=float(snr),
            magnitude=float(magnitude),
            magnitude_error=float(magnitude_error),
            aperture_correction=1.0
        )

    def _apply_optimization_method(
        self,
        method: ApertureOptimizationMethod,
        test_radii: np.ndarray,
        snr_values: List[float],
        flux_values: List[float],
        error_values: List[float],
        seeing_fwhm: float
    ) -> float:
        """Aplica el método de optimización especificado"""
        if method == ApertureOptimizationMethod.SNR_MAXIMIZATION:
            # Maximizar SNR
            max_snr_idx = np.argmax(snr_values)
            return test_radii[max_snr_idx]

        elif method == ApertureOptimizationMethod.SEEING_BASED:
            # Usar múltiplo del seeing
            optimal_radius = seeing_fwhm * 1.5  # factor típico
            # Encontrar el radio más cercano
            closest_idx = np.argmin(np.abs(test_radii - optimal_radius))
            return test_radii[closest_idx]

        elif method == ApertureOptimizationMethod.CURVE_OF_GROWTH:
            # Buscar donde la curva de crecimiento se estabiliza
            return self._find_curve_of_growth_plateau(test_radii, flux_values)

        elif method == ApertureOptimizationMethod.ERROR_MINIMIZATION:
            # Minimizar error relativo
            relative_errors = [err / flux if flux > 0 else np.inf
                             for err, flux in zip(error_values, flux_values)]
            min_error_idx = np.argmin(relative_errors)
            return test_radii[min_error_idx]

        else:
            # Por defecto: maximizar SNR
            max_snr_idx = np.argmax(snr_values)
            return test_radii[max_snr_idx]

    def _find_curve_of_growth_plateau(
        self,
        radii: np.ndarray,
        flux_values: List[float]
    ) -> float:
        """Encuentra donde la curva de crecimiento alcanza una meseta"""
        if len(flux_values) < 3:
            return radii[len(radii)//2]  # valor medio por defecto

        # Calcular derivadas para encontrar donde el crecimiento se ralentiza
        flux_array = np.array(flux_values)
        derivatives = np.gradient(flux_array)

        # Normalizar derivadas
        max_derivative = np.max(np.abs(derivatives))
        if max_derivative > 0:
            normalized_derivatives = np.abs(derivatives) / max_derivative
        else:
            return radii[-1]

        # Buscar donde la derivada cae por debajo de un umbral
        threshold = 0.1  # 10% de la derivada máxima
        plateau_indices = np.where(normalized_derivatives < threshold)[0]

        if len(plateau_indices) > 0:
            return radii[plateau_indices[0]]
        else:
            # Si no encuentra meseta, usar 75% del rango
            return radii[int(0.75 * len(radii))]

    def _calculate_aperture_correction(
        self,
        image: np.ndarray,
        center_x: float,
        center_y: float,
        measurement_radius: float,
        seeing_fwhm: float,
        reference_radius: float = 20.0
    ) -> float:
        """Calcula corrección de apertura usando PSF"""
        try:
            # Medir flujo en apertura de referencia (grande)
            ref_photometry = self._perform_aperture_photometry(
                image, center_x, center_y, reference_radius
            )
            ref_flux = ref_photometry.source_flux

            # Medir flujo en apertura de medición
            meas_photometry = self._perform_aperture_photometry(
                image, center_x, center_y, measurement_radius
            )
            meas_flux = meas_photometry.source_flux

            # Corrección = flujo_total / flujo_medido
            if meas_flux > 0 and ref_flux > meas_flux:
                correction = ref_flux / meas_flux
                return min(correction, 3.0)  # limitar corrección máxima
            else:
                return 1.0

        except BiologyError:
            # Si falla, usar corrección teórica basada en PSF gaussiana
            return self._theoretical_aperture_correction(
                measurement_radius, seeing_fwhm
            )

    def _theoretical_aperture_correction(
        self,
        radius: float,
        seeing_fwhm: float
    ) -> float:
        """Corrección teórica para PSF gaussiana"""
        sigma = seeing_fwhm / 2.355

        # Fracción de flujo contenida en apertura circular para gaussiana
        # Aproximación para r >> sigma
        if radius > 3 * sigma:
            correction = 1.0 / (1.0 - np.exp(-0.5 * (radius / sigma)**2))
        else:
            # Para aperturas pequeñas, usar expansión
            x = radius / sigma
            enclosed_fraction = 1.0 - np.exp(-0.5 * x**2)
            correction = 1.0 / enclosed_fraction if enclosed_fraction > 0.1 else 2.0

        return min(correction, 3.0)  # limitar corrección máxima


# Función de utilidad para testing rápido
def optimal_aperture_photometry_example():
    """
    Ejemplo rápido de uso del servicio de fotometría de apertura óptima
    """
    print("=== Ejemplo de Servicio de Fotometría de Apertura Óptima ===\n")

    # Generar imagen sintética con fuentes
    np.random.seed(42)
    image_size = 100
    image = np.random.normal(100, 10, (image_size, image_size))  # fondo con ruido

    # Agregar fuentes sintéticas (gaussianas)
    sources_true = [
        {'x': 30, 'y': 25, 'flux': 5000, 'fwhm': 3.0},
        {'x': 70, 'y': 45, 'flux': 8000, 'fwhm': 2.5},
        {'x': 50, 'y': 75, 'flux': 3000, 'fwhm': 4.0}
    ]

    # Agregar fuentes gaussianas a la imagen
    y_grid, x_grid = np.mgrid[0:image_size, 0:image_size]

    for source in sources_true:
        gaussian = source['flux'] * np.exp(
            -((x_grid - source['x'])**2 + (y_grid - source['y'])**2) /
            (2 * (source['fwhm'] / 2.355)**2)
        )
        image += gaussian

    service = OptimalAperturePhotometryService()

    try:
        print("1. Detección automática de fuentes...")
        detected_sources = service.detect_sources_automatically(image)
        print(f"   Detectadas {len(detected_sources)} fuentes")

        print("\n2. Estimación de seeing...")
        seeing = service.estimate_seeing(image, detected_sources)
        print(f"   Seeing estimado: {seeing:.2f} píxeles")

        print("\n3. Optimización de apertura para primera fuente...")
        if detected_sources:
            first_source = detected_sources[0]
            optimization = service.optimize_aperture_radius(
                image, first_source['x'], first_source['y']
            )
            print(f"   Radio óptimo: {optimization.optimal_radius:.2f} píxeles")
            print(f"   SNR máximo: {max(optimization.snr_values):.1f}")

        print("\n4. Fotometría optimizada...")
        if detected_sources:
            photometry = service.perform_optimal_photometry(
                image, first_source['x'], first_source['y']
            )
            print(f"   Flujo medido: {photometry.source_flux:.1f} ± {photometry.source_flux_error:.1f}")
            print(f"   SNR: {photometry.snr:.1f}")
            print(f"   Magnitud: {photometry.magnitude:.3f} ± {photometry.magnitude_error:.3f}")

        print("\n5. Fotometría de múltiples fuentes...")
        all_photometry = service.multi_source_photometry(
            image, detected_sources[:3]  # usar solo las 3 primeras
        )
        print(f"   Procesadas {len(all_photometry)} fuentes")
        for i, phot in enumerate(all_photometry):
            print(f"   Fuente {i+1}: SNR = {phot.snr:.1f}, Mag = {phot.magnitude:.3f}")

        print("\n✅ Ejemplo completado exitosamente")

    except BiologyError as e:
        print(f"Error en ejemplo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    optimal_aperture_photometry_example()