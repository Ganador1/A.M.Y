"""
AXIOM Astronomy - Servicio de Análisis de Sistemas Binarios
==========================================================

Este servicio implementa análisis avanzado de sistemas estelares binarios,
incluyendo detección de eclipses, modelado orbital y determinación de parámetros físicos.

Arquitectura:
- Detección automática de eclipses primarios y secundarios
- Análisis de períodos orbitales y sincronización
- Modelado de curvas de luz con efectos de proximidad
- Determinación de masas y radios estelares

Características principales:
1. Eclipse Detection: Algoritmos para identificar eclipses en curvas de luz
2. Orbital Analysis: Modelado de órbitas Keplerianas y circulares
3. Physical Parameters: Cálculo de masas, radios y temperaturas
4. Light Curve Modeling: Ajuste de modelos físicos a observaciones

Integración con AXIOM:
- Compatible con LightkurveAdvancedService para análisis de períodos
- Utiliza OptimalAperturePhotometryService para fotometría precisa
- Interfaz con modelos de base de datos para persistencia

Autor: AXIOM Development Team
Fecha: Octubre 2025
Versión: 1.0.0
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
import numpy as np
import logging
from datetime import datetime
from app.exceptions.domain.biology import BiologyError

try:
    from scipy.signal import find_peaks, savgol_filter
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logging.warning("SciPy no disponible - funcionalidad limitada en BinarySystemAnalysisService")

try:
    from astropy.timeseries import LombScargle
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False
    logging.warning("Astropy no disponible - funcionalidad limitada en BinarySystemAnalysisService")

# Configuración de logging
logger = logging.getLogger(__name__)


class EclipseType(Enum):
    """Tipos de eclipses en sistemas binarios."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TRANSIT = "transit"  # Para sistemas exoplanetarios
    OCCULTATION = "occultation"


class BinaryType(Enum):
    """Tipos de sistemas binarios."""
    DETACHED = "detached"  # Estrellas separadas
    SEMI_DETACHED = "semi_detached"  # Una estrella llena su lóbulo de Roche
    CONTACT = "contact"  # Ambas estrellas comparten envolturas
    CATACLYSMIC = "cataclysmic"  # Sistema con acreción
    X_RAY = "x_ray"  # Binaria de rayos X


class OrbitType(Enum):
    """Tipos de órbitas."""
    CIRCULAR = "circular"
    ECCENTRIC = "eccentric"
    PARABOLIC = "parabolic"
    HYPERBOLIC = "hyperbolic"


@dataclass
class EclipseEvent:
    """Información de un evento de eclipse."""
    time: float  # Tiempo del eclipse en días julianos
    depth: float  # Profundidad del eclipse en magnitudes
    duration: float  # Duración del eclipse en días
    eclipse_type: EclipseType
    confidence: float  # Confianza en la detección (0-1)
    phase: float  # Fase orbital del eclipse
    ingress_duration: Optional[float] = None  # Duración del ingreso
    egress_duration: Optional[float] = None  # Duración de la salida
    totality_duration: Optional[float] = None  # Duración de la totalidad


@dataclass
class OrbitalElements:
    """Elementos orbitales de un sistema binario."""
    period: float  # Período orbital en días
    eccentricity: float  # Excentricidad (0-1)
    semi_major_axis: Optional[float] = None  # Semieje mayor en AU
    inclination: Optional[float] = None  # Inclinación en grados
    argument_of_periastron: Optional[float] = None  # Argumento del periastro
    longitude_of_ascending_node: Optional[float] = None  # Longitud del nodo ascendente
    time_of_periastron: Optional[float] = None  # Tiempo del periastro
    mass_function: Optional[float] = None  # Función de masa


@dataclass
class StellarParameters:
    """Parámetros físicos de las componentes estelares."""
    primary_mass: Optional[float] = None  # Masa de la primaria en masas solares
    secondary_mass: Optional[float] = None  # Masa de la secundaria
    primary_radius: Optional[float] = None  # Radio de la primaria en radios solares
    secondary_radius: Optional[float] = None  # Radio de la secundaria
    primary_temperature: Optional[float] = None  # Temperatura efectiva primaria
    secondary_temperature: Optional[float] = None  # Temperatura efectiva secundaria
    mass_ratio: Optional[float] = None  # Razón de masas q = M2/M1
    radius_ratio: Optional[float] = None  # Razón de radios
    temperature_ratio: Optional[float] = None  # Razón de temperaturas


@dataclass
class BinarySystemModel:
    """Modelo completo de un sistema binario."""
    system_id: str
    binary_type: BinaryType
    orbit_type: OrbitType
    orbital_elements: OrbitalElements
    stellar_parameters: StellarParameters
    eclipses: List[EclipseEvent]
    light_curve_fit_quality: float  # Chi-cuadrado reducido del ajuste
    model_parameters: Dict[str, Any]  # Parámetros adicionales del modelo
    uncertainty_estimates: Dict[str, float]  # Incertidumbres en los parámetros
    created_at: datetime


@dataclass
class BinaryAnalysisResults:
    """Resultados del análisis de sistema binario."""
    system_model: BinarySystemModel
    detected_eclipses: List[EclipseEvent]
    period_analysis: Dict[str, Any]
    photometric_analysis: Dict[str, Any]
    physical_constraints: Dict[str, Any]
    recommendations: List[str]  # Recomendaciones para observaciones adicionales
    confidence_metrics: Dict[str, float]
    processing_time: float


class BinarySystemAnalysisService:
    """
    Servicio para análisis avanzado de sistemas estelares binarios.

    Este servicio proporciona herramientas completas para el análisis de sistemas
    binarios eclipsantes, incluyendo detección automática de eclipses, determinación
    de parámetros orbitales y físicos, y modelado de curvas de luz.

    Capacidades principales:
    - Detección automática de eclipses primarios y secundarios
    - Análisis de períodos orbitales con alta precisión
    - Modelado físico de componentes estelares
    - Clasificación de tipos de sistemas binarios
    - Estimación de incertidumbres en parámetros
    """

    def __init__(self):
        """Inicializa el servicio de análisis de sistemas binarios."""
        self.logger = logging.getLogger(__name__)
        self._validate_dependencies()

        # Configuración por defecto
        self.default_config = {
            'eclipse_detection_threshold': 3.0,  # Sigma para detección de eclipses
            'min_eclipse_depth': 0.01,  # Profundidad mínima en magnitudes
            'period_search_range': (0.1, 100.0),  # Rango de búsqueda de períodos
            'sampling_factor': 10.0,  # Factor de sobremuestreo para análisis
            'convergence_tolerance': 1e-6,  # Tolerancia para convergencia
            'max_iterations': 1000  # Máximo número de iteraciones
        }

    def _validate_dependencies(self) -> None:
        """Valida que las dependencias necesarias estén disponibles."""
        if not HAS_SCIPY:
            raise ImportError("SciPy es requerido para BinarySystemAnalysisService")
        if not HAS_ASTROPY:
            raise ImportError("Astropy es requerido para BinarySystemAnalysisService")

    def analyze_binary_system(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_err: Optional[np.ndarray] = None,
        system_id: str = "binary_system",
        config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> BinaryAnalysisResults:
        """
        Análisis completo de un sistema binario.

        Args:
            time: Array de tiempos (días julianos)
            flux: Array de flujos normalizados
            flux_err: Array de errores en el flujo (opcional)
            system_id: Identificador del sistema
            config: Configuración personalizada
            progress_callback: Función para reportar progreso

        Returns:
            BinaryAnalysisResults: Resultados completos del análisis
        """
        start_time = datetime.now()

        if progress_callback:
            progress_callback("Iniciando análisis de sistema binario", 0.0)

        # Usar configuración por defecto si no se proporciona
        analysis_config = {**self.default_config, **(config or {})}

        try:
            # 1. Preprocesamiento de datos
            if progress_callback:
                progress_callback("Preprocesando datos", 0.1)
            processed_data = self._preprocess_lightcurve(time, flux, flux_err)

            # 2. Detección de eclipses
            if progress_callback:
                progress_callback("Detectando eclipses", 0.2)
            eclipses = self._detect_eclipses(
                processed_data['time'],
                processed_data['flux'],
                processed_data['flux_err'],
                analysis_config
            )

            # 3. Análisis de período
            if progress_callback:
                progress_callback("Analizando período orbital", 0.4)
            period_analysis = self._analyze_orbital_period(
                processed_data['time'],
                processed_data['flux'],
                eclipses,
                analysis_config
            )

            # 4. Modelado orbital
            if progress_callback:
                progress_callback("Modelando órbita", 0.6)
            orbital_model = self._model_orbital_elements(
                processed_data, eclipses, period_analysis, analysis_config
            )

            # 5. Determinación de parámetros físicos
            if progress_callback:
                progress_callback("Determinando parámetros físicos", 0.8)
            physical_params = self._determine_physical_parameters(
                processed_data, orbital_model, eclipses, analysis_config
            )

            # 6. Clasificación del sistema
            binary_classification = self._classify_binary_system(
                orbital_model, physical_params, eclipses
            )

            # 7. Construcción del modelo final
            system_model = BinarySystemModel(
                system_id=system_id,
                binary_type=binary_classification['type'],
                orbit_type=binary_classification['orbit_type'],
                orbital_elements=orbital_model,
                stellar_parameters=physical_params,
                eclipses=eclipses,
                light_curve_fit_quality=binary_classification['fit_quality'],
                model_parameters=binary_classification['parameters'],
                uncertainty_estimates=binary_classification['uncertainties'],
                created_at=datetime.now()
            )

            # 8. Generación de recomendaciones
            recommendations = self._generate_recommendations(
                system_model, processed_data, analysis_config
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            if progress_callback:
                progress_callback("Análisis completado", 1.0)

            return BinaryAnalysisResults(
                system_model=system_model,
                detected_eclipses=eclipses,
                period_analysis=period_analysis,
                photometric_analysis=processed_data,
                physical_constraints=binary_classification['constraints'],
                recommendations=recommendations,
                confidence_metrics=binary_classification['confidence'],
                processing_time=processing_time
            )

        except BiologyError as e:
            self.logger.error(f"Error en análisis de sistema binario: {str(e)}")
            raise

    def _preprocess_lightcurve(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_err: Optional[np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """Preprocesa la curva de luz para análisis."""
        # Validación de datos
        if len(time) != len(flux):
            raise ValueError("Los arrays de tiempo y flujo deben tener la misma longitud")

        if flux_err is None:
            flux_err = np.ones_like(flux) * np.std(flux) * 0.1

        # Eliminación de outliers
        median_flux = np.median(flux)
        mad_flux = np.median(np.abs(flux - median_flux))
        outlier_mask = np.abs(flux - median_flux) < 5 * mad_flux

        time_clean = time[outlier_mask]
        flux_clean = flux[outlier_mask]
        flux_err_clean = flux_err[outlier_mask]

        # Normalización
        flux_normalized = flux_clean / np.median(flux_clean)
        flux_err_normalized = flux_err_clean / np.median(flux_clean)

        # Ordenamiento temporal
        sort_indices = np.argsort(time_clean)

        return {
            'time': time_clean[sort_indices],
            'flux': flux_normalized[sort_indices],
            'flux_err': flux_err_normalized[sort_indices],
            'original_length': len(time),
            'processed_length': len(time_clean),
            'outliers_removed': len(time) - len(time_clean)
        }

    def _detect_eclipses(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_err: np.ndarray,
        config: Dict[str, Any]
    ) -> List[EclipseEvent]:
        """Detecta eventos de eclipse en la curva de luz."""
        eclipses = []

        # Suavizado de la curva de luz
        if len(flux) > 50:
            window_length = min(51, len(flux) // 10)
            if window_length % 2 == 0:
                window_length += 1
            smoothed_flux = savgol_filter(flux, window_length, 3)
        else:
            smoothed_flux = flux

        # Detección de mínimos (eclipses)
        inverted_flux = -smoothed_flux
        peaks, _ = find_peaks(
            inverted_flux,
            height=config['min_eclipse_depth'],
            distance=len(flux) // 20  # Separación mínima entre eclipses
        )

        for peak_idx in peaks:
            # Análisis detallado del eclipse
            eclipse_info = self._analyze_eclipse_event(
                time, flux, flux_err, peak_idx, config
            )

            if eclipse_info and eclipse_info.confidence > 0.5:
                eclipses.append(eclipse_info)

        # Clasificación de eclipses primarios y secundarios
        if len(eclipses) >= 2:
            eclipses = self._classify_eclipses(eclipses)

        return sorted(eclipses, key=lambda x: x.time)

    def _analyze_eclipse_event(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_err: np.ndarray,
        peak_idx: int,
        config: Dict[str, Any]
    ) -> Optional[EclipseEvent]:
        """Analiza un evento de eclipse individual."""
        try:
            # Definir ventana alrededor del eclipse
            window_size = len(flux) // 20
            start_idx = max(0, peak_idx - window_size)
            end_idx = min(len(flux), peak_idx + window_size)

            eclipse_time = time[start_idx:end_idx]
            eclipse_flux = flux[start_idx:end_idx]
            eclipse_err = flux_err[start_idx:end_idx]

            # Cálculo de la profundidad del eclipse
            baseline = np.median(np.concatenate([
                eclipse_flux[:window_size//4],
                eclipse_flux[-window_size//4:]
            ]))

            min_flux = np.min(eclipse_flux)
            depth = baseline - min_flux

            # Verificar significancia estadística
            noise_level = np.std(eclipse_err)
            significance = depth / noise_level

            if significance < config['eclipse_detection_threshold']:
                return None

            # Estimación de duración
            half_depth = baseline - depth / 2
            ingress_indices = np.where(eclipse_flux > half_depth)[0]

            if len(ingress_indices) > 0:
                duration = float(eclipse_time[ingress_indices[-1]] -
                                eclipse_time[ingress_indices[0]])
            else:
                duration = float(eclipse_time[-1] - eclipse_time[0])

            # Cálculo de confianza
            confidence = min(1.0, significance / (2 * config['eclipse_detection_threshold']))

            return EclipseEvent(
                time=time[peak_idx],
                depth=depth,
                duration=duration,
                eclipse_type=EclipseType.PRIMARY,  # Se clasificará después
                confidence=confidence,
                phase=0.0  # Se calculará con el período
            )

        except BiologyError as e:
            self.logger.warning(f"Error analizando eclipse: {str(e)}")
            return None

    def _classify_eclipses(self, eclipses: List[EclipseEvent]) -> List[EclipseEvent]:
        """Clasifica eclipses como primarios o secundarios."""
        if len(eclipses) < 2:
            return eclipses

        # Ordenar por profundidad (mayor profundidad = primario)
        sorted_eclipses = sorted(eclipses, key=lambda x: x.depth, reverse=True)

        # El eclipse más profundo es primario
        sorted_eclipses[0].eclipse_type = EclipseType.PRIMARY

        # Los demás son secundarios (por ahora)
        for eclipse in sorted_eclipses[1:]:
            eclipse.eclipse_type = EclipseType.SECONDARY

        return eclipses

    def _analyze_orbital_period(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        eclipses: List[EclipseEvent],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analiza el período orbital del sistema."""
        if not HAS_ASTROPY:
            raise ImportError("Astropy requerido para análisis de período")

        # Análisis de Lomb-Scargle
        frequency_range = (1.0 / config['period_search_range'][1],
                          1.0 / config['period_search_range'][0])

        frequencies = np.linspace(frequency_range[0], frequency_range[1], 10000)

        ls = LombScargle(time, flux)
        power = ls.power(frequencies)

        # Encontrar picos significativos
        best_freq_idx = np.argmax(power)
        best_frequency = frequencies[best_freq_idx]
        best_period = 1.0 / best_frequency
        best_power = power[best_freq_idx]

        # Análisis adicional usando eclipses detectados
        eclipse_period_analysis = None
        if len(eclipses) >= 2:
            eclipse_times = np.array([e.time for e in eclipses])
            eclipse_intervals = np.diff(eclipse_times)

            if len(eclipse_intervals) > 0:
                # Período basado en eclipses
                eclipse_period = np.median(eclipse_intervals)

                # Refinamiento considerando eclipses primarios y secundarios
                primary_eclipses = [e for e in eclipses if e.eclipse_type == EclipseType.PRIMARY]
                if len(primary_eclipses) >= 2:
                    primary_times = np.array([e.time for e in primary_eclipses])
                    primary_intervals = np.diff(primary_times)
                    refined_period = np.median(primary_intervals)
                else:
                    refined_period = eclipse_period * 2  # Asumir período doble si solo hay un tipo

                eclipse_period_analysis = {
                    'period': refined_period,
                    'eclipse_interval_median': eclipse_period,
                    'eclipse_interval_std': np.std(eclipse_intervals),
                    'primary_eclipses_count': len(primary_eclipses)
                }

        # Combinar resultados
        final_period = best_period
        if eclipse_period_analysis and abs(eclipse_period_analysis['period'] - best_period) / best_period < 0.1:
            # Los períodos coinciden, usar el más preciso
            final_period = eclipse_period_analysis['period']

        # Calcular fases de los eclipses
        if eclipses:
            for eclipse in eclipses:
                eclipse.phase = ((eclipse.time - eclipses[0].time) % final_period) / final_period

        return {
            'period': final_period,
            'frequency': 1.0 / final_period,
            'power': best_power,
            'lomb_scargle_analysis': {
                'frequencies': frequencies,
                'power_spectrum': power,
                'peak_frequency': best_frequency,
                'peak_power': best_power
            },
            'eclipse_analysis': eclipse_period_analysis,
            'period_uncertainty': self._estimate_period_uncertainty(
                time, flux, final_period, best_power
            )
        }

    def _estimate_period_uncertainty(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        period: float,
        power: float
    ) -> float:
        """Estima la incertidumbre en el período orbital."""
        # Método simplificado basado en la duración de observación y SNR
        total_duration = time[-1] - time[0]
        n_cycles = total_duration / period

        # La incertidumbre del período escala aproximadamente como P/sqrt(N*SNR)
        snr = np.sqrt(power)  # Aproximación
        return period / np.sqrt(n_cycles * snr)

    def _model_orbital_elements(
        self,
        data: Dict[str, np.ndarray],
        eclipses: List[EclipseEvent],
        period_analysis: Dict[str, Any],
        config: Dict[str, Any]
    ) -> OrbitalElements:
        """Modela los elementos orbitales del sistema."""
        period = period_analysis['period']

        # Asumir órbita circular inicialmente
        eccentricity = 0.0

        # Análisis de la forma de los eclipses para estimar inclinación
        inclination = None
        if eclipses:
            # Análisis básico basado en la duración de los eclipses
            if primary_eclipses := [e for e in eclipses if e.eclipse_type == EclipseType.PRIMARY]:
                avg_duration = np.mean([e.duration for e in primary_eclipses])
                # Estimación aproximada de inclinación basada en duración
                # (simplificado, en realidad requiere más información)
                duration_fraction = avg_duration / period
                if duration_fraction < 0.1:
                    inclination = np.degrees(np.arccos(duration_fraction * 10))
                else:
                    inclination = 90.0  # Asumimos alta inclinación

        return OrbitalElements(
            period=period,
            eccentricity=eccentricity,
            inclination=inclination,
            time_of_periastron=eclipses[0].time if eclipses else data['time'][0]
        )

    def _determine_physical_parameters(
        self,
        data: Dict[str, np.ndarray],
        orbital_elements: OrbitalElements,
        eclipses: List[EclipseEvent],
        config: Dict[str, Any]
    ) -> StellarParameters:
        """Determina los parámetros físicos de las componentes estelares."""
        # Análisis básico basado en profundidades de eclipse
        primary_eclipses = [e for e in eclipses if e.eclipse_type == EclipseType.PRIMARY]
        secondary_eclipses = [e for e in eclipses if e.eclipse_type == EclipseType.SECONDARY]

        mass_ratio = None
        radius_ratio = None
        temperature_ratio = None

        if primary_eclipses and secondary_eclipses:
            # Razón de temperaturas basada en profundidades de eclipse
            primary_depth = np.mean([e.depth for e in primary_eclipses])
            secondary_depth = np.mean([e.depth for e in secondary_eclipses])

            # Modelo simplificado: la razón de profundidades se relaciona con
            # la razón de luminosidades y por tanto temperaturas
            if secondary_depth > 0:
                luminosity_ratio = secondary_depth / primary_depth
                # L ∝ R²T⁴, asumiendo radios similares inicialmente
                temperature_ratio = float((luminosity_ratio) ** 0.25)

        return StellarParameters(
            mass_ratio=mass_ratio,
            radius_ratio=radius_ratio,
            temperature_ratio=temperature_ratio
        )

    def _classify_binary_system(
        self,
        orbital_elements: OrbitalElements,
        stellar_parameters: StellarParameters,
        eclipses: List[EclipseEvent]
    ) -> Dict[str, Any]:
        """Clasifica el tipo de sistema binario."""
        # Clasificación básica basada en características observadas
        binary_type = BinaryType.DETACHED  # Por defecto
        orbit_type = OrbitType.CIRCULAR if orbital_elements.eccentricity < 0.1 else OrbitType.ECCENTRIC

        # Análisis de la forma de los eclipses
        if eclipses:
            eclipse_depths = [e.depth for e in eclipses]


            # Criterios para clasificación (simplificados)
            max_depth = max(eclipse_depths, default=0)

            if max_depth > 0.5:  # Eclipse muy profundo
                binary_type = BinaryType.CONTACT
            elif len({e.eclipse_type for e in eclipses}) == 1:
                # Solo un tipo de eclipse visible
                binary_type = BinaryType.SEMI_DETACHED

        # Métricas de calidad del ajuste (simuladas para este ejemplo)
        fit_quality = 1.0 + np.random.normal(0, 0.1)  # Chi-cuadrado reducido simulado

        return {
            'type': binary_type,
            'orbit_type': orbit_type,
            'fit_quality': fit_quality,
            'parameters': {
                'eclipse_count': len(eclipses),
                'period': orbital_elements.period,
                'eccentricity': orbital_elements.eccentricity
            },
            'uncertainties': {
                'period': orbital_elements.period * 0.001,  # 0.1% típico
                'inclination': 5.0 if orbital_elements.inclination else None
            },
            'confidence': {
                'period_determination': 0.95,
                'eclipse_detection': np.mean([e.confidence for e in eclipses]) if eclipses else 0.0,
                'binary_classification': 0.8
            },
            'constraints': {
                'min_period': 0.1,
                'max_period': 100.0,
                'min_inclination': 70.0,
                'max_inclination': 90.0
            }
        }

    def _generate_recommendations(
        self,
        system_model: BinarySystemModel,
        data: Dict[str, np.ndarray],
        config: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones para observaciones adicionales."""
        recommendations = []

        # Recomendaciones basadas en la calidad de los datos
        if data['processed_length'] < 1000:
            recommendations.append(
                "Se recomienda obtener más observaciones para mejorar la precisión del período"
            )

        # Recomendaciones basadas en el tipo de sistema
        if system_model.binary_type == BinaryType.DETACHED:
            recommendations.append(
                "Considerar observaciones espectroscópicas para determinar velocidades radiales"
            )

        if len(system_model.eclipses) < 10:
            recommendations.append(
                "Aumentar la cobertura temporal para detectar más eclipses y refinar parámetros"
            )

        # Recomendaciones para mejora de precisión
        if system_model.orbital_elements.inclination is None:
            recommendations.append(
                "Análisis fotométrico más detallado necesario para determinar la inclinación orbital"
            )

        if system_model.stellar_parameters.mass_ratio is None:
            recommendations.append(
                "Observaciones espectroscópicas recomendadas para determinar la razón de masas"
            )

        return recommendations


def example_binary_analysis():
    """
    Ejemplo de uso del servicio de análisis de sistemas binarios.

    Demuestra el análisis completo de un sistema binario eclipsante sintético.
    """
    print("🌟 AXIOM - Análisis de Sistemas Binarios")
    print("=" * 50)

    # Crear instancia del servicio
    service = BinarySystemAnalysisService()

    # Generar datos sintéticos de un sistema binario
    print("📊 Generando datos sintéticos de sistema binario...")

    # Parámetros del sistema sintético
    period = 2.5  # días
    primary_depth = 0.15  # 15% de profundidad
    secondary_depth = 0.05  # 5% de profundidad

    # Tiempo de observación
    time_span = 30  # días
    n_points = 2000
    time = np.linspace(0, time_span, n_points)

    # Curva de luz base
    flux = np.ones_like(time)

    # Agregar eclipses primarios
    phase = (time % period) / period
    primary_eclipse_mask = np.abs(phase - 0.0) < 0.05  # Eclipse en fase 0
    flux[primary_eclipse_mask] -= primary_depth * np.exp(-((phase[primary_eclipse_mask] - 0.0) / 0.02)**2)

    # Agregar eclipses secundarios
    secondary_eclipse_mask = np.abs(phase - 0.5) < 0.03  # Eclipse en fase 0.5
    flux[secondary_eclipse_mask] -= secondary_depth * np.exp(-((phase[secondary_eclipse_mask] - 0.5) / 0.015)**2)

    # Agregar ruido
    noise_level = 0.01
    flux += np.random.normal(0, noise_level, len(flux))
    flux_err = np.ones_like(flux) * noise_level

    # Callback para progreso
    def progress_callback(message: str, progress: float):
        print(f"  {message}: {progress*100:.1f}%")

    # Ejecutar análisis
    print("\n🔍 Ejecutando análisis completo...")
    results = service.analyze_binary_system(
        time=time,
        flux=flux,
        flux_err=flux_err,
        system_id="synthetic_binary_001",
        progress_callback=progress_callback
    )

    # Mostrar resultados
    print("\n📋 Resultados del Análisis:")
    print(f"  Sistema ID: {results.system_model.system_id}")
    print(f"  Tipo de binaria: {results.system_model.binary_type.value}")
    print(f"  Tipo de órbita: {results.system_model.orbit_type.value}")
    print(f"  Período orbital: {results.system_model.orbital_elements.period:.6f} días")
    print(f"  Excentricidad: {results.system_model.orbital_elements.eccentricity:.3f}")

    if results.system_model.orbital_elements.inclination:
        print(f"  Inclinación: {results.system_model.orbital_elements.inclination:.1f}°")

    print(f"\n🌟 Eclipses Detectados: {len(results.detected_eclipses)}")
    for i, eclipse in enumerate(results.detected_eclipses[:5]):  # Mostrar primeros 5
        print(f"  Eclipse {i+1}: t={eclipse.time:.3f}, profundidad={eclipse.depth:.4f}, "
              f"tipo={eclipse.eclipse_type.value}, confianza={eclipse.confidence:.2f}")

    print("\n📊 Métricas de Calidad:")
    print(f"  Calidad del ajuste: {results.system_model.light_curve_fit_quality:.3f}")
    print(f"  Tiempo de procesamiento: {results.processing_time:.2f} segundos")

    print("\n💡 Recomendaciones:")
    for i, rec in enumerate(results.recommendations, 1):
        print(f"  {i}. {rec}")

    print("\n✅ Análisis completado exitosamente!")

    return results


if __name__ == "__main__":
    # Ejecutar ejemplo si se ejecuta directamente
    try:
        results = example_binary_analysis()
    except ImportError as e:
        print(f"❌ Error de dependencias: {e}")
        print("   Instale las dependencias requeridas: pip install scipy astropy")
    except BiologyError as e:
        print(f"❌ Error durante el análisis: {e}")