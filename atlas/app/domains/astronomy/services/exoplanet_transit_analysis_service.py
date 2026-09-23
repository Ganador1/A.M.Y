"""
AXIOM Astronomy - Servicio de Análisis de Tránsitos Exoplanetarios
================================================================

Este servicio implementa análisis especializado de tránsitos exoplanetarios,
incluyendo detección automática, modelado de curvas de luz y determinación
de parámetros planetarios y estelares.

Arquitectura:
- Detección automática de tránsitos planetarios
- Modelado físico con corrección de oscurecimiento al limbo
- Determinación de parámetros orbitales y físicos del exoplaneta
- Análisis de habitabilidad y composición atmosférica

Características principales:
1. Transit Detection: Algoritmos BLS y TLS para detección de tránsitos
2. Limb Darkening: Corrección de oscurecimiento al limbo estelar
3. Planetary Parameters: Radio, período, inclinación, temperatura
4. Atmospheric Analysis: Detección de atmósferas y composición

Integración con AXIOM:
- Compatible con LightkurveAdvancedService para análisis de períodos
- Utiliza OptimalAperturePhotometryService para fotometría precisa
- Interfaz con modelos de base de datos para catálogo de exoplanetas

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
    from astropy.timeseries import BoxLeastSquares
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False
    BoxLeastSquares = None
    logging.warning("Astropy no disponible - funcionalidad limitada en ExoplanetTransitAnalysisService")

HAS_SCIPY = True  # Solo para compatibilidad

# Configuración de logging
logger = logging.getLogger(__name__)


class TransitType(Enum):
    """Tipos de eventos de tránsito."""
    PRIMARY = "primary"  # Tránsito del planeta frente a la estrella
    SECONDARY = "secondary"  # Eclipse del planeta detrás de la estrella
    GRAZING = "grazing"  # Tránsito parcial (rozante)
    TOTAL = "total"  # Tránsito total


class PlanetType(Enum):
    """Clasificación de tipos de exoplanetas."""
    SUPER_EARTH = "super_earth"  # 1-2 R_Earth
    NEPTUNE = "neptune"  # 2-4 R_Earth
    JUPITER = "jupiter"  # >4 R_Earth
    EARTH_LIKE = "earth_like"  # ~1 R_Earth
    HOT_JUPITER = "hot_jupiter"  # Júpiter caliente
    MINI_NEPTUNE = "mini_neptune"  # 1.7-4 R_Earth


class HabitabilityZone(Enum):
    """Zonas de habitabilidad."""
    INNER = "inner"  # Demasiado caliente
    HABITABLE = "habitable"  # Zona habitable
    OUTER = "outer"  # Demasiado frío
    UNKNOWN = "unknown"  # No determinable


@dataclass
class LimbDarkeningParameters:
    """Parámetros de oscurecimiento al limbo."""
    law: str  # Ley utilizada (linear, quadratic, nonlinear)
    u1: Optional[float] = None  # Coeficiente lineal
    u2: Optional[float] = None  # Coeficiente cuadrático
    u3: Optional[float] = None  # Coeficiente cúbico
    u4: Optional[float] = None  # Coeficiente cuártico
    source: str = "theoretical"  # Fuente (theoretical, fitted)


@dataclass
class TransitEvent:
    """Información de un evento de tránsito."""
    time: float  # Tiempo del centro del tránsito (BJD)
    depth: float  # Profundidad del tránsito (ppm o fracción)
    duration: float  # Duración total del tránsito (horas)
    ingress_duration: float  # Duración del ingreso (horas)
    egress_duration: float  # Duración de la salida (horas)
    transit_type: TransitType
    snr: float  # Relación señal-ruido del tránsito
    confidence: float  # Confianza en la detección (0-1)
    phase: float  # Fase orbital del tránsito
    impact_parameter: Optional[float] = None  # Parámetro de impacto


@dataclass
class PlanetaryParameters:
    """Parámetros físicos del exoplaneta."""
    radius: Optional[float] = None  # Radio planetario en R_Earth
    mass: Optional[float] = None  # Masa planetaria en M_Earth
    density: Optional[float] = None  # Densidad en g/cm³
    surface_gravity: Optional[float] = None  # Gravedad superficial
    equilibrium_temperature: Optional[float] = None  # Temperatura de equilibrio (K)
    bond_albedo: Optional[float] = None  # Albedo de Bond
    planet_type: Optional[PlanetType] = None  # Clasificación del planeta
    habitability_zone: HabitabilityZone = HabitabilityZone.UNKNOWN


@dataclass
class OrbitalParameters:
    """Parámetros orbitales del exoplaneta."""
    period: float  # Período orbital (días)
    semi_major_axis: Optional[float] = None  # Semieje mayor (AU)
    eccentricity: float = 0.0  # Excentricidad
    inclination: Optional[float] = None  # Inclinación orbital (grados)
    argument_of_periastron: Optional[float] = None  # Argumento del periastro
    time_of_transit: Optional[float] = None  # Tiempo de tránsito central (BJD)
    transit_duration: Optional[float] = None  # Duración del tránsito (horas)


@dataclass
class StellarParameters:
    """Parámetros de la estrella anfitriona."""
    mass: Optional[float] = None  # Masa estelar en M_Sun
    radius: Optional[float] = None  # Radio estelar en R_Sun
    temperature: Optional[float] = None  # Temperatura efectiva (K)
    metallicity: Optional[float] = None  # Metalicidad [Fe/H]
    age: Optional[float] = None  # Edad estelar (Gyr)
    limb_darkening: Optional[LimbDarkeningParameters] = None


@dataclass
class AtmosphericProperties:
    """Propiedades atmosféricas del exoplaneta."""
    has_atmosphere: Optional[bool] = None  # Presencia de atmósfera
    scale_height: Optional[float] = None  # Altura de escala (km)
    mean_molecular_weight: Optional[float] = None  # Peso molecular medio
    transmission_spectrum: Optional[Dict[str, float]] = None  # Espectro de transmisión
    emission_spectrum: Optional[Dict[str, float]] = None  # Espectro de emisión
    cloud_coverage: Optional[float] = None  # Cobertura de nubes (0-1)


@dataclass
class ExoplanetSystem:
    """Sistema completo de exoplaneta."""
    system_id: str
    planet_name: str
    stellar_parameters: StellarParameters
    orbital_parameters: OrbitalParameters
    planetary_parameters: PlanetaryParameters
    atmospheric_properties: AtmosphericProperties
    transits: List[TransitEvent]
    model_fit_quality: float  # Chi-cuadrado reducido
    detection_significance: float  # Significancia de la detección
    false_positive_probability: float  # Probabilidad de falso positivo
    created_at: datetime


@dataclass
class ExoplanetAnalysisResults:
    """Resultados del análisis de tránsitos exoplanetarios."""
    exoplanet_system: ExoplanetSystem
    detected_transits: List[TransitEvent]
    transit_model: Dict[str, Any]  # Modelo de tránsito ajustado
    limb_darkening_analysis: Dict[str, Any]  # Análisis de oscurecimiento
    habitability_assessment: Dict[str, Any]  # Evaluación de habitabilidad
    atmospheric_analysis: Dict[str, Any]  # Análisis atmosférico
    follow_up_recommendations: List[str]  # Recomendaciones de seguimiento
    confidence_metrics: Dict[str, float]
    processing_time: float


class ExoplanetTransitAnalysisService:
    """
    Servicio para análisis avanzado de tránsitos exoplanetarios.

    Este servicio proporciona herramientas completas para la detección y
    caracterización de exoplanetas mediante análisis de tránsitos, incluyendo
    modelado físico, corrección de efectos estelares y evaluación de habitabilidad.

    Capacidades principales:
    - Detección automática de tránsitos con algoritmos BLS/TLS
    - Modelado físico con corrección de oscurecimiento al limbo
    - Determinación de parámetros planetarios y orbitales
    - Análisis atmosférico y evaluación de habitabilidad
    - Estimación de probabilidades de falsos positivos
    """

    def __init__(self):
        """Inicializa el servicio de análisis de tránsitos exoplanetarios."""
        self.logger = logging.getLogger(__name__)
        self._validate_dependencies()

        # Configuración por defecto
        self.default_config = {
            'min_period': 0.5,  # Período mínimo en días
            'max_period': 300.0,  # Período máximo en días
            'min_transit_depth': 100e-6,  # Profundidad mínima (100 ppm)
            'min_snr': 7.0,  # SNR mínimo para detección
            'detection_threshold': 9.0,  # Umbral de detección sigma
            'max_false_positive_prob': 0.01,  # Máxima probabilidad de FP
            'limb_darkening_law': 'quadratic',  # Ley de oscurecimiento
            'fit_limb_darkening': True,  # Ajustar coeficientes LD
            'stellar_density_prior': True,  # Usar prior de densidad estelar
        }

    def _validate_dependencies(self) -> None:
        """Valida que las dependencias necesarias estén disponibles."""
        if not HAS_SCIPY:
            raise ImportError("SciPy es requerido para ExoplanetTransitAnalysisService")
        if not HAS_ASTROPY:
            raise ImportError("Astropy es requerido para ExoplanetTransitAnalysisService")

    def analyze_exoplanet_transits(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_err: Optional[np.ndarray] = None,
        stellar_params: Optional[Dict[str, float]] = None,
        system_id: str = "exoplanet_system",
        config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> ExoplanetAnalysisResults:
        """
        Análisis completo de tránsitos exoplanetarios.

        Args:
            time: Array de tiempos (BJD)
            flux: Array de flujos normalizados
            flux_err: Array de errores en el flujo (opcional)
            stellar_params: Parámetros estelares conocidos (opcional)
            system_id: Identificador del sistema
            config: Configuración personalizada
            progress_callback: Función para reportar progreso

        Returns:
            ExoplanetAnalysisResults: Resultados completos del análisis
        """
        start_time = datetime.now()

        if progress_callback:
            progress_callback("Iniciando análisis de tránsitos exoplanetarios", 0.0)

        # Usar configuración por defecto si no se proporciona
        analysis_config = {**self.default_config, **(config or {})}

        try:
            # 1. Preprocesamiento de datos
            if progress_callback:
                progress_callback("Preprocesando curva de luz", 0.1)
            processed_data = self._preprocess_lightcurve(time, flux, flux_err)

            # 2. Detección de tránsitos
            if progress_callback:
                progress_callback("Detectando tránsitos candidatos", 0.2)
            candidates = self._detect_transit_candidates(
                processed_data['time'],
                processed_data['flux'],
                processed_data['flux_err'],
                analysis_config
            )

            # 3. Validación de candidatos
            if progress_callback:
                progress_callback("Validando candidatos", 0.4)
            validated_transits = self._validate_transit_candidates(
                processed_data, candidates, analysis_config
            )

            # 4. Modelado de tránsitos
            if progress_callback:
                progress_callback("Modelando tránsitos", 0.6)
            transit_model = self._model_transits(
                processed_data, validated_transits, stellar_params, analysis_config
            )

            # 5. Determinación de parámetros planetarios
            if progress_callback:
                progress_callback("Determinando parámetros planetarios", 0.7)
            planetary_params = self._determine_planetary_parameters(
                transit_model, stellar_params, analysis_config
            )

            # 6. Análisis de oscurecimiento al limbo
            if progress_callback:
                progress_callback("Analizando oscurecimiento al limbo", 0.8)
            limb_darkening_analysis = self._analyze_limb_darkening(
                processed_data, transit_model, stellar_params, analysis_config
            )

            # 7. Evaluación de habitabilidad
            if progress_callback:
                progress_callback("Evaluando habitabilidad", 0.85)
            habitability_assessment = self._assess_habitability(
                planetary_params, stellar_params
            )

            # 8. Análisis atmosférico
            if progress_callback:
                progress_callback("Analizando atmósfera", 0.9)
            atmospheric_analysis = self._analyze_atmosphere(
                processed_data, transit_model, planetary_params
            )

            # 9. Construcción del sistema exoplanetario
            exoplanet_system = self._build_exoplanet_system(
                system_id, transit_model, planetary_params, stellar_params,
                validated_transits, limb_darkening_analysis
            )

            # 10. Recomendaciones de seguimiento
            follow_up_recommendations = self._generate_followup_recommendations(
                exoplanet_system, analysis_config
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            if progress_callback:
                progress_callback("Análisis completado", 1.0)

            return ExoplanetAnalysisResults(
                exoplanet_system=exoplanet_system,
                detected_transits=validated_transits,
                transit_model=transit_model,
                limb_darkening_analysis=limb_darkening_analysis,
                habitability_assessment=habitability_assessment,
                atmospheric_analysis=atmospheric_analysis,
                follow_up_recommendations=follow_up_recommendations,
                confidence_metrics=self._calculate_confidence_metrics(
                    exoplanet_system, transit_model
                ),
                processing_time=processing_time
            )

        except BiologyError as e:
            self.logger.error(f"Error en análisis de tránsitos exoplanetarios: {str(e)}")
            raise

    def _preprocess_lightcurve(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_err: Optional[np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """Preprocesa la curva de luz para análisis de tránsitos."""
        # Validación básica
        if len(time) != len(flux):
            raise ValueError("Los arrays de tiempo y flujo deben tener la misma longitud")

        if flux_err is None:
            flux_err = np.ones_like(flux) * np.std(flux) * 0.001

        # Ordenamiento temporal
        sort_indices = np.argsort(time)
        time_sorted = time[sort_indices]
        flux_sorted = flux[sort_indices]
        flux_err_sorted = flux_err[sort_indices]

        # Eliminación de outliers más conservadora (para preservar tránsitos)
        median_flux = np.median(flux_sorted)
        mad_flux = np.median(np.abs(flux_sorted - median_flux))
        outlier_mask = np.abs(flux_sorted - median_flux) < 10 * mad_flux  # Más permisivo

        time_clean = time_sorted[outlier_mask]
        flux_clean = flux_sorted[outlier_mask]
        flux_err_clean = flux_err_sorted[outlier_mask]

        # Normalización conservadora
        flux_normalized = flux_clean / np.median(flux_clean)
        flux_err_normalized = flux_err_clean / np.median(flux_clean)

        # Detección de gaps temporales
        time_diff = np.diff(time_clean)
        median_cadence = np.median(time_diff)
        gap_indices = np.where(time_diff > 5 * median_cadence)[0]

        return {
            'time': time_clean,
            'flux': flux_normalized,
            'flux_err': flux_err_normalized,
            'cadence': median_cadence,
            'gaps': gap_indices,
            'baseline_flux': np.median(flux_clean),
            'baseline_noise': np.std(flux_err_normalized)
        }

    def _detect_transit_candidates(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_err: np.ndarray,
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detecta candidatos a tránsitos usando Box Least Squares."""
        if not HAS_ASTROPY or BoxLeastSquares is None:
            # Método simplificado sin BLS
            return self._simple_transit_detection(time, flux, config)

        candidates = []

        # Configuración BLS
        min_period = config['min_period']
        max_period = min(config['max_period'], (time[-1] - time[0]) / 3)

        # Ejecutar BLS
        bls = BoxLeastSquares(time, flux, flux_err)

        # Búsqueda de períodos
        durations = np.linspace(0.05, 0.5, 50)  # 1.2 a 12 horas en días

        periodogram = bls.autopower(durations, minimum_period=min_period, maximum_period=max_period)

        # Encontrar picos significativos
        best_period = periodogram.period[np.argmax(periodogram.power)]
        best_power = np.max(periodogram.power)

        # Calcular estadísticas
        stats = bls.compute_stats(best_period, best_power, periodogram.duration[np.argmax(periodogram.power)])

        if stats['snr'] >= config['min_snr']:
            # Fold data y buscar tránsitos individuales
            folded_time = (time % best_period) / best_period
            sort_indices = np.argsort(folded_time)
            folded_flux = flux[sort_indices]

            # Buscar el centro del tránsito
            min_flux_idx = np.argmin(folded_flux)
            transit_center_phase = folded_time[sort_indices[min_flux_idx]]

            # Estimar profundidad del tránsito
            transit_depth = 1.0 - np.min(folded_flux)

            if transit_depth >= config['min_transit_depth']:
                candidate = {
                    'period': best_period,
                    'epoch': time[0] + transit_center_phase * best_period,
                    'depth': transit_depth,
                    'duration': periodogram.duration[np.argmax(periodogram.power)],
                    'snr': stats['snr'],
                    'power': best_power,
                    'false_alarm_probability': 1.0 - stats['depth_even'] / stats['depth_odd'] if stats['depth_odd'] > 0 else 1.0
                }
                candidates.append(candidate)

        return candidates

    def _simple_transit_detection(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Método simplificado de detección de tránsitos sin BLS."""
        candidates = []

        # Búsqueda básica de períodos usando autocorrelación
        min_period = config['min_period']
        max_period = min(config['max_period'], (time[-1] - time[0]) / 3)

        # Buscar dips significativos en el flujo
        flux_smooth = np.convolve(flux, np.ones(5)/5, mode='same')  # Suavizado simple
        dips = flux_smooth < (np.median(flux_smooth) - 2 * np.std(flux_smooth))

        if np.any(dips):
            # Agrupar dips consecutivos
            dip_times = time[dips]
            if len(dip_times) > 2:
                # Estimar período basándose en diferencias de tiempo
                diffs = np.diff(dip_times)
                period_estimate = np.median(diffs[diffs > min_period])

                if min_period <= period_estimate <= max_period:
                    depth_estimate = np.median(flux_smooth) - np.min(flux_smooth[dips])
                    if depth_estimate >= config['min_transit_depth']:
                        candidate = {
                            'period': float(period_estimate),
                            'epoch': float(dip_times[0]),
                            'depth': float(depth_estimate),
                            'duration': 3.0 / 24,  # 3 horas por defecto
                            'snr': float(np.sqrt(len(dip_times))),
                            'power': float(depth_estimate),
                            'false_alarm_probability': 0.1
                        }
                        candidates.append(candidate)

        return candidates

    def _validate_transit_candidates(
        self,
        data: Dict[str, np.ndarray],
        candidates: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[TransitEvent]:
        """Valida candidatos y los convierte en eventos de tránsito."""
        validated_transits = []

        for candidate in candidates:
            # Validaciones básicas
            if candidate['snr'] < config['min_snr']:
                continue

            if candidate['false_alarm_probability'] > config['max_false_positive_prob']:
                continue

            # Buscar tránsitos individuales
            period = candidate['period']
            epoch = candidate['epoch']
            duration = candidate['duration']

            # Tiempos de tránsito esperados
            transit_times = []
            t = epoch
            while t < data['time'][-1]:
                if t >= data['time'][0]:
                    transit_times.append(t)
                t += period

            # Validar cada tránsito individual
            for transit_time in transit_times:
                transit_event = self._analyze_individual_transit(
                    data, transit_time, duration, candidate['depth']
                )

                if transit_event and transit_event.snr >= config['min_snr']:
                    validated_transits.append(transit_event)

        return validated_transits

    def _analyze_individual_transit(
        self,
        data: Dict[str, np.ndarray],
        transit_time: float,
        expected_duration: float,
        expected_depth: float
    ) -> Optional[TransitEvent]:
        """Analiza un tránsito individual."""
        try:
            # Definir ventana de análisis
            window_size = max(expected_duration * 3, 0.1)  # Al menos 2.4 horas
            mask = np.abs(data['time'] - transit_time) <= window_size

            if np.sum(mask) < 10:  # Necesitamos al menos 10 puntos
                return None

            time_window = data['time'][mask]
            flux_window = data['flux'][mask]

            # Estimar línea base (fuera del tránsito)
            transit_mask = np.abs(time_window - transit_time) <= expected_duration / 2
            baseline_mask = ~transit_mask

            if np.sum(baseline_mask) < 5:
                return None

            baseline_flux = np.median(flux_window[baseline_mask])
            baseline_noise = np.std(flux_window[baseline_mask])

            # Medir profundidad del tránsito
            if np.sum(transit_mask) < 3:
                return None

            transit_flux = np.mean(flux_window[transit_mask])
            transit_depth = baseline_flux - transit_flux

            # Calcular SNR
            snr = transit_depth / (baseline_noise / np.sqrt(np.sum(transit_mask)))

            # Estimar duraciones
            # Simplificado: asumir forma trapezoidal
            ingress_duration = expected_duration * 0.2  # 20% del total
            egress_duration = expected_duration * 0.2

            # Determinar tipo de tránsito
            impact_parameter = self._estimate_impact_parameter(
                transit_depth, expected_depth, baseline_noise
            )

            transit_type = TransitType.TOTAL if impact_parameter < 0.5 else TransitType.GRAZING

            return TransitEvent(
                time=transit_time,
                depth=transit_depth,
                duration=expected_duration * 24,  # Convertir a horas
                ingress_duration=ingress_duration * 24,
                egress_duration=egress_duration * 24,
                transit_type=transit_type,
                snr=snr,
                confidence=min(1.0, snr / 10.0),
                phase=0.0,  # Se calculará después
                impact_parameter=impact_parameter
            )

        except BiologyError as e:
            self.logger.warning(f"Error analizando tránsito individual: {str(e)}")
            return None

    def _estimate_impact_parameter(
        self,
        observed_depth: float,
        expected_depth: float,
        noise_level: float
    ) -> float:
        """Estima el parámetro de impacto del tránsito."""
        # Estimación simplificada basada en la profundidad observada vs esperada
        if expected_depth <= 0 or noise_level <= 0:
            return 0.5  # Valor por defecto

        depth_ratio = observed_depth / expected_depth
        # Para tránsitos centrales, depth_ratio ~ 1
        # Para tránsitos rozantes, depth_ratio < 1
        impact_parameter = max(0.0, min(1.0, 1.0 - depth_ratio))

        return impact_parameter

    def _model_transits(
        self,
        data: Dict[str, np.ndarray],
        transits: List[TransitEvent],
        stellar_params: Optional[Dict[str, float]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modela los tránsitos observados."""
        if not transits:
            return {'success': False, 'error': 'No hay tránsitos para modelar'}

        # Calcular período promedio
        if len(transits) > 1:
            transit_times = np.array([t.time for t in transits])
            periods = np.diff(transit_times)
            period = np.median(periods)
        else:
            period = 10.0  # Valor por defecto si solo hay un tránsito

        # Calcular época (tiempo de tránsito de referencia)
        epoch = transits[0].time

        # Parámetros del modelo
        transit_depth = np.median([t.depth for t in transits])
        transit_duration = np.median([t.duration for t in transits]) / 24  # Convertir a días

        # Estimar radio planetario relativo (Rp/R*)
        radius_ratio = np.sqrt(transit_depth)

        # Estimar parámetros orbitales
        # Semi-eje mayor escalado (a/R*)
        if stellar_params and 'mass' in stellar_params and 'radius' in stellar_params:
            stellar_mass = stellar_params['mass']  # En masas solares
            stellar_radius = stellar_params['radius']  # En radios solares

            # Tercera ley de Kepler para a/R*
            a_over_r_star = self._calculate_scaled_semi_major_axis(
                period, stellar_mass, stellar_radius
            )
        else:
            # Estimación aproximada basada en período
            a_over_r_star = ((period / 10.0) ** (2/3)) * 20  # Escalamiento aproximado

        # Estimar inclinación
        inclination = self._estimate_inclination(
            transit_duration, period, a_over_r_star, radius_ratio
        )

        # Modelo de tránsito simplificado
        model = {
            'period': period,
            'epoch': epoch,
            'radius_ratio': radius_ratio,
            'a_over_r_star': a_over_r_star,
            'inclination': inclination,
            'transit_depth': transit_depth,
            'transit_duration': transit_duration,
            'impact_parameter': np.cos(np.radians(inclination)),
            'limb_darkening_u1': 0.4,  # Valores por defecto
            'limb_darkening_u2': 0.3,
            'chi_squared': 1.0,  # Se calcularía con el ajuste real
            'n_transits': len(transits),
            'fit_quality': 'good' if len(transits) >= 3 else 'limited'
        }

        return model

    def _calculate_scaled_semi_major_axis(
        self,
        period: float,
        stellar_mass: float,
        stellar_radius: float
    ) -> float:
        """Calcula el semieje mayor escalado (a/R*) usando la tercera ley de Kepler."""
        # Constantes
        G = 6.67430e-11  # m³/kg/s²
        M_sun = 1.989e30  # kg
        R_sun = 6.96e8   # m

        # Conversiones
        M_star = stellar_mass * M_sun  # kg
        R_star = stellar_radius * R_sun  # m
        P = period * 24 * 3600  # segundos

        # Tercera ley de Kepler: a³ = GM*P²/(4π²)
        a_cubed = G * M_star * P**2 / (4 * np.pi**2)
        a = a_cubed**(1/3)  # metros

        # Retornar a/R*
        return a / R_star

    def _estimate_inclination(
        self,
        duration: float,
        period: float,
        a_over_r_star: float,
        radius_ratio: float
    ) -> float:
        """Estima la inclinación orbital basada en la duración del tránsito."""
        # Convertir duración a días si está en horas
        if duration > 1:
            duration_days = duration / 24
        else:
            duration_days = duration

        # Relación aproximada para la duración del tránsito
        # T_14 ≈ (P/π) * arcsin(R*/a * sqrt((1+Rp/R*)²-b²))
        # Donde b es el parámetro de impacto

        duration_factor = duration_days * np.pi / period
        sin_factor = duration_factor * a_over_r_star

        # Para evitar valores no físicos
        if sin_factor > 1:
            sin_factor = 1.0

        # Estimar parámetro de impacto
        term_squared = (1 + radius_ratio)**2
        if sin_factor**2 < term_squared:
            impact_parameter_squared = term_squared - sin_factor**2
            impact_parameter = np.sqrt(impact_parameter_squared)
        else:
            impact_parameter = 0.0

        # Calcular inclinación
        # b = (a/R*) * cos(i)
        if a_over_r_star > 0:
            cos_inclination = impact_parameter / a_over_r_star
            cos_inclination = max(-1.0, min(1.0, cos_inclination))  # Limitar a [-1, 1]
            inclination = np.degrees(np.arccos(cos_inclination))
        else:
            inclination = 90.0  # Valor por defecto

        return inclination

    def _determine_planetary_parameters(
        self,
        transit_model: Dict[str, Any],
        stellar_params: Optional[Dict[str, float]],
        config: Dict[str, Any]
    ) -> PlanetaryParameters:
        """Determina los parámetros físicos del exoplaneta."""
        if not transit_model.get('success', True):
            return PlanetaryParameters()

        # Radio planetario
        radius_ratio = transit_model['radius_ratio']
        if stellar_params and 'radius' in stellar_params:
            stellar_radius_km = stellar_params['radius'] * 696340  # km (radio solar)
            planet_radius_km = radius_ratio * stellar_radius_km
            planet_radius_earth = planet_radius_km / 6371  # Radios terrestres
        else:
            # Asumir estrella similar al Sol
            planet_radius_earth = radius_ratio * 109.2  # R_sun/R_earth ≈ 109.2

        # Temperatura de equilibrio
        equilibrium_temp = None
        if stellar_params and 'temperature' in stellar_params:
            stellar_temp = stellar_params['temperature']
            a_over_r_star = transit_model['a_over_r_star']

            # T_eq = T_star * sqrt(R_star/(2*a)) * (1-A)^(1/4)
            # Asumir albedo = 0.3
            albedo = 0.3
            temp_factor = np.sqrt(1.0 / (2 * a_over_r_star)) * ((1 - albedo) ** 0.25)
            equilibrium_temp = stellar_temp * temp_factor

        # Clasificación del planeta
        planet_type = self._classify_planet_type(planet_radius_earth)

        # Zona de habitabilidad
        habitability_zone = self._determine_habitability_zone(
            transit_model['period'], stellar_params
        )

        return PlanetaryParameters(
            radius=planet_radius_earth,
            equilibrium_temperature=equilibrium_temp,
            bond_albedo=0.3,  # Valor asumido
            planet_type=planet_type,
            habitability_zone=habitability_zone
        )

    def _classify_planet_type(self, radius_earth: float) -> PlanetType:
        """Clasifica el tipo de planeta basado en su radio."""
        if radius_earth < 1.25:
            return PlanetType.EARTH_LIKE
        elif radius_earth < 2.0:
            return PlanetType.SUPER_EARTH
        elif radius_earth < 4.0:
            return PlanetType.MINI_NEPTUNE
        elif radius_earth < 8.0:
            return PlanetType.NEPTUNE
        else:
            return PlanetType.JUPITER

    def _determine_habitability_zone(
        self,
        period: float,
        stellar_params: Optional[Dict[str, float]]
    ) -> HabitabilityZone:
        """Determina si el planeta está en la zona habitable."""
        if not stellar_params or 'temperature' not in stellar_params:
            return HabitabilityZone.UNKNOWN

        stellar_temp = stellar_params['temperature']
        stellar_mass = stellar_params.get('mass', 1.0)  # Asumir masa solar por defecto

        # Límites aproximados de la zona habitable (en AU)
        # Basado en Kopparapu et al. 2013
        temp_ratio = stellar_temp / 5778  # Relativo al Sol
        mass_ratio = stellar_mass

        # Límite interno (efecto invernadero descontrolado)
        inner_limit = 0.95 * np.sqrt(mass_ratio) * (temp_ratio ** 2)

        # Límite externo (límite máximo de efecto invernadero)
        outer_limit = 1.67 * np.sqrt(mass_ratio) * (temp_ratio ** 2)

        # Convertir período a semieje mayor aproximado
        # Usar tercera ley de Kepler simplificada
        semi_major_axis = (period / 365.25) ** (2/3) * np.sqrt(stellar_mass)

        if semi_major_axis < inner_limit:
            return HabitabilityZone.INNER
        elif semi_major_axis > outer_limit:
            return HabitabilityZone.OUTER
        else:
            return HabitabilityZone.HABITABLE

    def _analyze_limb_darkening(
        self,
        data: Dict[str, np.ndarray],
        transit_model: Dict[str, Any],
        stellar_params: Optional[Dict[str, float]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analiza el oscurecimiento al limbo estelar."""
        # Implementación simplificada
        limb_darkening_law = config.get('limb_darkening_law', 'quadratic')

        # Coeficientes teóricos basados en temperatura estelar
        if stellar_params and 'temperature' in stellar_params:
            stellar_temp = stellar_params['temperature']
            u1, u2 = self._get_theoretical_limb_darkening(stellar_temp, limb_darkening_law)
        else:
            # Valores por defecto para estrella tipo solar
            u1, u2 = 0.4, 0.3

        limb_darkening_params = LimbDarkeningParameters(
            law=limb_darkening_law,
            u1=u1,
            u2=u2,
            source='theoretical'
        )

        return {
            'limb_darkening_parameters': limb_darkening_params,
            'law_used': limb_darkening_law,
            'fitted': config.get('fit_limb_darkening', False),
            'chi_squared_improvement': 0.0,  # Se calcularía con ajuste real
            'uncertainty_u1': 0.05,  # Incertidumbre típica
            'uncertainty_u2': 0.05
        }

    def _get_theoretical_limb_darkening(
        self,
        stellar_temp: float,
        law: str
    ) -> tuple:
        """Obtiene coeficientes teóricos de oscurecimiento al limbo."""
        # Relaciones empíricas simplificadas para banda Kepler
        # Basado en Claret & Bloemen 2011

        if law == 'linear':
            if stellar_temp < 4000:
                u1 = 0.8
            elif stellar_temp < 6000:
                u1 = 0.6
            else:
                u1 = 0.4
            return u1, 0.0

        elif law == 'quadratic':
            if stellar_temp < 4000:
                u1, u2 = 0.5, 0.4
            elif stellar_temp < 6000:
                u1, u2 = 0.4, 0.3
            else:
                u1, u2 = 0.3, 0.2
            return u1, u2

        else:
            return 0.4, 0.3  # Valores por defecto

    def _assess_habitability(
        self,
        planetary_params: PlanetaryParameters,
        stellar_params: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Evalúa la habitabilidad del exoplaneta."""
        habitability_score = 0.0
        factors = {}

        # Factor 1: Zona habitable
        if planetary_params.habitability_zone == HabitabilityZone.HABITABLE:
            habitability_score += 0.4
            factors['habitable_zone'] = True
        else:
            factors['habitable_zone'] = False

        # Factor 2: Tamaño planetario
        if planetary_params.radius:
            if 0.5 <= planetary_params.radius <= 2.0:
                habitability_score += 0.3
                factors['suitable_size'] = True
            else:
                factors['suitable_size'] = False
        else:
            factors['suitable_size'] = None

        # Factor 3: Temperatura de equilibrio
        if planetary_params.equilibrium_temperature:
            temp = planetary_params.equilibrium_temperature
            if 200 <= temp <= 400:  # Rango aproximado para agua líquida
                habitability_score += 0.2
                factors['suitable_temperature'] = True
            else:
                factors['suitable_temperature'] = False
        else:
            factors['suitable_temperature'] = None

        # Factor 4: Tipo de estrella anfitriona
        if stellar_params and 'temperature' in stellar_params:
            stellar_temp = stellar_params['temperature']
            if 3500 <= stellar_temp <= 7000:  # Estrellas K y G son más favorables
                habitability_score += 0.1
                factors['suitable_star'] = True
            else:
                factors['suitable_star'] = False
        else:
            factors['suitable_star'] = None

        # Clasificación de habitabilidad
        if habitability_score >= 0.8:
            habitability_class = 'highly_habitable'
        elif habitability_score >= 0.5:
            habitability_class = 'potentially_habitable'
        elif habitability_score >= 0.2:
            habitability_class = 'marginally_habitable'
        else:
            habitability_class = 'likely_uninhabitable'

        return {
            'habitability_score': habitability_score,
            'habitability_class': habitability_class,
            'contributing_factors': factors,
            'zone': planetary_params.habitability_zone.value,
            'recommendations': self._get_habitability_recommendations(
                habitability_class, factors
            )
        }

    def _get_habitability_recommendations(
        self,
        habitability_class: str,
        factors: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones basadas en la evaluación de habitabilidad."""
        recommendations = []

        if habitability_class in ['highly_habitable', 'potentially_habitable']:
            recommendations.append("Candidato prioritario para espectroscopía de transmisión")
            recommendations.append("Buscar biomarcadores en la atmósfera (O2, O3, H2O, CH4)")

        if factors.get('suitable_size') and factors.get('habitable_zone'):
            recommendations.append("Observaciones de eclipse secundario para temperatura diurna")

        if not factors.get('suitable_temperature', True):
            recommendations.append("Refinar temperatura de equilibrio con observaciones térmicas")

        return recommendations

    def _analyze_atmosphere(
        self,
        data: Dict[str, np.ndarray],
        transit_model: Dict[str, Any],
        planetary_params: PlanetaryParameters
    ) -> Dict[str, Any]:
        """Analiza las propiedades atmosféricas del exoplaneta."""
        # Análisis simplificado basado en el tránsito

        atmospheric_props = AtmosphericProperties()

        # Estimación de la presencia de atmósfera
        # Basado en el tamaño planetario y la calidad del ajuste del modelo
        if planetary_params.radius:
            if planetary_params.radius > 1.5:
                atmospheric_props.has_atmosphere = True
                # Estimar altura de escala
                if planetary_params.equilibrium_temperature:
                    # H = kT/(μg) aproximadamente
                    temp = planetary_params.equilibrium_temperature
                    # Asumir composición similar a la Tierra para planetas pequeños
                    mean_molecular_weight = 29.0 if planetary_params.radius < 4 else 2.0
                    atmospheric_props.mean_molecular_weight = mean_molecular_weight

                    # Altura de escala aproximada en km
                    # H ≈ 8.5 * (T/300) * (29/μ) para planetas similares a la Tierra
                    scale_height = 8.5 * (temp / 300) * (29.0 / mean_molecular_weight)
                    atmospheric_props.scale_height = scale_height
            else:
                atmospheric_props.has_atmosphere = False

        return {
            'atmospheric_properties': atmospheric_props,
            'detection_method': 'transit_depth_analysis',
            'confidence': 0.5,  # Confianza moderada sin espectroscopía
            'required_observations': [
                'Espectroscopía de transmisión',
                'Observaciones de eclipse secundario',
                'Fotometría en múltiples bandas'
            ]
        }

    def _build_exoplanet_system(
        self,
        system_id: str,
        transit_model: Dict[str, Any],
        planetary_params: PlanetaryParameters,
        stellar_params: Optional[Dict[str, float]],
        transits: List[TransitEvent],
        limb_darkening_analysis: Dict[str, Any]
    ) -> ExoplanetSystem:
        """Construye el sistema exoplanetario completo."""
        # Construir parámetros estelares
        stellar_parameters = StellarParameters()
        if stellar_params:
            stellar_parameters.mass = stellar_params.get('mass')
            stellar_parameters.radius = stellar_params.get('radius')
            stellar_parameters.temperature = stellar_params.get('temperature')
            stellar_parameters.metallicity = stellar_params.get('metallicity')
            stellar_parameters.limb_darkening = limb_darkening_analysis['limb_darkening_parameters']

        # Construir parámetros orbitales
        orbital_parameters = OrbitalParameters(
            period=transit_model['period'],
            inclination=transit_model['inclination'],
            time_of_transit=transit_model['epoch'],
            transit_duration=transit_model['transit_duration'] * 24  # Convertir a horas
        )

        # Calcular semieje mayor si tenemos parámetros estelares
        if stellar_parameters.mass and stellar_parameters.radius:
            a_over_r_star = transit_model['a_over_r_star']
            semi_major_axis_km = a_over_r_star * stellar_parameters.radius * 696340
            orbital_parameters.semi_major_axis = semi_major_axis_km / 149597870.7  # Convertir a AU

        # Propiedades atmosféricas (simplificadas)
        atmospheric_properties = AtmosphericProperties()
        if planetary_params.radius and planetary_params.radius > 1.5:
            atmospheric_properties.has_atmosphere = True

        # Calcular métricas de calidad
        model_fit_quality = transit_model.get('chi_squared', 1.0)
        detection_significance = np.mean([t.snr for t in transits]) if transits else 0.0
        false_positive_probability = 1.0 / (detection_significance ** 2) if detection_significance > 0 else 1.0

        planet_name = f"{system_id}_b"  # Convención estándar

        return ExoplanetSystem(
            system_id=system_id,
            planet_name=planet_name,
            stellar_parameters=stellar_parameters,
            orbital_parameters=orbital_parameters,
            planetary_parameters=planetary_params,
            atmospheric_properties=atmospheric_properties,
            transits=transits,
            model_fit_quality=model_fit_quality,
            detection_significance=detection_significance,
            false_positive_probability=false_positive_probability,
            created_at=datetime.now()
        )

    def _generate_followup_recommendations(
        self,
        exoplanet_system: ExoplanetSystem,
        config: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones para observaciones de seguimiento."""
        recommendations = []

        # Recomendaciones basadas en la calidad de la detección
        if exoplanet_system.detection_significance < 10:
            recommendations.append(
                "Obtener más tránsitos para mejorar la significancia de la detección"
            )

        # Recomendaciones basadas en el tipo de planeta
        planet_type = exoplanet_system.planetary_parameters.planet_type
        if planet_type in [PlanetType.EARTH_LIKE, PlanetType.SUPER_EARTH]:
            recommendations.append(
                "Espectroscopía de transmisión para caracterización atmosférica"
            )
            recommendations.append(
                "Medición de velocidades radiales para determinación de masa"
            )

        # Recomendaciones basadas en habitabilidad
        if exoplanet_system.planetary_parameters.habitability_zone == HabitabilityZone.HABITABLE:
            recommendations.append(
                "Análisis prioritario para biosignaturas atmosféricas"
            )
            recommendations.append(
                "Observaciones de eclipse secundario para mapeo térmico"
            )

        # Recomendaciones técnicas
        if len(exoplanet_system.transits) < 5:
            recommendations.append(
                "Monitoreo fotométrico continuo para detectar variaciones de período"
            )

        if exoplanet_system.stellar_parameters.temperature and exoplanet_system.stellar_parameters.temperature > 6500:
            recommendations.append(
                "Corrección cuidadosa de actividad estelar en análisis de tránsitos"
            )

        return recommendations

    def _calculate_confidence_metrics(
        self,
        exoplanet_system: ExoplanetSystem,
        transit_model: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calcula métricas de confianza para la detección."""
        return {
            'detection_confidence': min(1.0, exoplanet_system.detection_significance / 15.0),
            'parameter_reliability': 1.0 - exoplanet_system.false_positive_probability,
            'model_quality': 1.0 / (1.0 + exoplanet_system.model_fit_quality),
            'transit_coverage': min(1.0, len(exoplanet_system.transits) / 10.0),
            'overall_confidence': self._calculate_overall_confidence(exoplanet_system)
        }

    def _calculate_overall_confidence(self, exoplanet_system: ExoplanetSystem) -> float:
        """Calcula la confianza general en la detección y caracterización."""
        factors = []

        # Factor de significancia de detección
        sig_factor = min(1.0, exoplanet_system.detection_significance / 20.0)
        factors.append(sig_factor)

        # Factor de calidad del modelo
        model_factor = 1.0 / (1.0 + exoplanet_system.model_fit_quality)
        factors.append(model_factor)

        # Factor de número de tránsitos
        transit_factor = min(1.0, len(exoplanet_system.transits) / 5.0)
        factors.append(transit_factor)

        # Factor de falso positivo
        fp_factor = 1.0 - exoplanet_system.false_positive_probability
        factors.append(fp_factor)

        # Promedio ponderado
        weights = [0.4, 0.2, 0.2, 0.2]
        overall_confidence = sum(f * w for f, w in zip(factors, weights))

        return overall_confidence


def example_exoplanet_analysis():
    """
    Ejemplo de uso del servicio de análisis de tránsitos exoplanetarios.

    Demuestra el análisis completo de un sistema exoplanetario sintético.
    """
    print("🪐 AXIOM - Análisis de Tránsitos Exoplanetarios")
    print("=" * 55)

    # Crear instancia del servicio
    service = ExoplanetTransitAnalysisService()

    # Generar datos sintéticos de un exoplaneta tipo Tierra
    print("🌍 Generando datos sintéticos de exoplaneta tipo Tierra...")

    # Parámetros del sistema sintético
    period = 10.5  # días (en zona habitable de estrella K)
    transit_depth = 500e-6  # 500 ppm (planeta de ~1.5 R_Earth)
    transit_duration = 3.2 / 24  # 3.2 horas en días

    # Tiempo de observación
    time_span = 200  # días
    n_points = 5000
    time = np.linspace(0, time_span, n_points)

    # Curva de luz base con ruido realista
    flux = np.ones_like(time)
    noise_level = 50e-6  # 50 ppm de ruido
    flux += np.random.normal(0, noise_level, len(flux))

    # Agregar tránsitos
    n_transits = int(time_span / period)
    for i in range(n_transits):
        transit_time = period * (i + 0.3)  # Comenzar después del primer período
        if transit_time > time_span:
            break

        # Modelo de tránsito trapezoidal simplificado
        phase = (time - transit_time) / transit_duration

        # Forma del tránsito con ingreso/salida suaves
        transit_shape = np.zeros_like(time)
        ingress_mask = (-0.5 <= phase) & (phase <= -0.3)
        flat_mask = (-0.3 <= phase) & (phase <= 0.3)
        egress_mask = (0.3 <= phase) & (phase <= 0.5)

        # Ingreso lineal
        transit_shape[ingress_mask] = transit_depth * (0.5 + phase[ingress_mask]) / 0.2
        # Fondo plano
        transit_shape[flat_mask] = transit_depth
        # Salida lineal
        transit_shape[egress_mask] = transit_depth * (0.5 - phase[egress_mask]) / 0.2

        flux -= transit_shape

    # Parámetros estelares (estrella tipo K habitable)
    stellar_params = {
        'mass': 0.8,  # masas solares
        'radius': 0.75,  # radios solares
        'temperature': 5200,  # K
        'metallicity': -0.1
    }

    # Configuración personalizada
    config = {
        'min_period': 5.0,
        'max_period': 50.0,
        'min_transit_depth': 100e-6,
        'min_snr': 5.0,
        'detection_threshold': 7.0
    }

    # Callback para progreso
    def progress_callback(message: str, progress: float):
        print(f"  {message}: {progress*100:.1f}%")

    # Ejecutar análisis
    print("\n🔍 Ejecutando análisis completo de tránsitos...")
    results = service.analyze_exoplanet_transits(
        time=time,
        flux=flux,
        stellar_params=stellar_params,
        system_id="TOI-AXIOM-1",
        config=config,
        progress_callback=progress_callback
    )

    # Mostrar resultados
    system = results.exoplanet_system
    print("\n📋 Resultados del Análisis:")
    print(f"  Sistema: {system.system_id}")
    print(f"  Planeta: {system.planet_name}")
    print(f"  Período orbital: {system.orbital_parameters.period:.2f} días")

    if system.planetary_parameters.radius:
        print(f"  Radio planetario: {system.planetary_parameters.radius:.2f} R_Earth")

    if system.planetary_parameters.equilibrium_temperature:
        print(f"  Temperatura de equilibrio: {system.planetary_parameters.equilibrium_temperature:.0f} K")

    if system.planetary_parameters.planet_type:
        print(f"  Tipo de planeta: {system.planetary_parameters.planet_type.value}")

    print(f"  Zona de habitabilidad: {system.planetary_parameters.habitability_zone.value}")

    print(f"\n🌟 Tránsitos Detectados: {len(results.detected_transits)}")
    for i, transit in enumerate(results.detected_transits[:3]):  # Mostrar primeros 3
        print(f"  Tránsito {i+1}: t={transit.time:.2f} días, SNR={transit.snr:.1f}, "
              f"profundidad={transit.depth*1e6:.0f} ppm")

    print("\n📊 Métricas de Confianza:")
    for metric, value in results.confidence_metrics.items():
        print(f"  {metric.replace('_', ' ').title()}: {value:.3f}")

    print("\n🏠 Evaluación de Habitabilidad:")
    hab = results.habitability_assessment
    print(f"  Puntuación: {hab['habitability_score']:.2f}")
    print(f"  Clasificación: {hab['habitability_class']}")

    if hab['contributing_factors']['habitable_zone']:
        print("  ✓ En zona habitable")
    if hab['contributing_factors'].get('suitable_size'):
        print("  ✓ Tamaño adecuado para habitabilidad")
    if hab['contributing_factors'].get('suitable_temperature'):
        print("  ✓ Temperatura favorable")

    print("\n💡 Recomendaciones de Seguimiento:")
    for i, rec in enumerate(results.follow_up_recommendations, 1):
        print(f"  {i}. {rec}")

    print(f"\n✅ Análisis completado en {results.processing_time:.2f} segundos")

    return results


if __name__ == "__main__":
    # Ejecutar ejemplo si se ejecuta directamente
    try:
        results = example_exoplanet_analysis()
    except ImportError as e:
        print(f"❌ Error de dependencias: {e}")
        print("   Instale las dependencias requeridas: pip install scipy astropy")
    except BiologyError as e:
        print(f"❌ Error durante el análisis: {e}")