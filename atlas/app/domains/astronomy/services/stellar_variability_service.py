"""
AXIOM - Servicio de Variabilidad Estelar
Detección automática de estrellas variables, análisis de periodicidad y clasificación
"""

import numpy as np
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from app.exceptions.domain.biology import BiologyError

try:
    from scipy import signal
    from scipy.optimize import curve_fit
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy no está disponible. Funcionalidad limitada.")

try:
    from astropy.timeseries import LombScargle
    ASTROPY_AVAILABLE = True
except ImportError:
    ASTROPY_AVAILABLE = False
    logging.warning("Astropy no está disponible para análisis de periodicidad.")


class VariableStarType(Enum):
    """Tipos de estrellas variables"""
    UNKNOWN = "unknown"
    DELTA_SCUTI = "delta_scuti"
    RR_LYRAE = "rr_lyrae"
    CEPHEID = "cepheid"
    ECLIPSING_BINARY = "eclipsing_binary"
    FLARE_STAR = "flare_star"
    ROTATING_VARIABLE = "rotating_variable"
    PULSATING = "pulsating"
    ERUPTIVE = "eruptive"
    CATACLYSMIC = "cataclysmic"


@dataclass
class PeriodicityResult:
    """Resultado del análisis de periodicidad"""
    period_days: float
    period_error_days: float
    amplitude: float
    amplitude_error: float
    phase_zero: float
    significance: float
    method: str
    harmonics: List[float]


@dataclass
class FlareEvent:
    """Evento de fulguración estelar detectado"""
    start_time: float
    peak_time: float
    end_time: float
    duration_minutes: float
    amplitude: float
    energy_equivalent: float
    rise_time: float
    decay_time: float
    confidence: float


@dataclass
class VariabilityClassification:
    """Clasificación de variabilidad estelar"""
    star_type: VariableStarType
    confidence: float
    period_days: float
    amplitude_range: List[float]
    characteristics: Dict[str, Any]
    alternative_classifications: List[Dict[str, Any]]


class StellarVariabilityService:
    """
    Servicio para análisis de variabilidad estelar

    Capacidades:
    - Detección automática de estrellas variables
    - Análisis de periodicidad Lomb-Scargle
    - Clasificación automática de tipos de variables
    - Detección de fulguraciones estelares
    - Análisis de pulsaciones
    - Caracterización de curvas de rotación
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        if not SCIPY_AVAILABLE:
            self.logger.error("SciPy no disponible. Funcionalidad limitada.")

        if not ASTROPY_AVAILABLE:
            self.logger.error("Astropy no disponible. Análisis periodicidad limitado.")

        # Configurar parámetros de clasificación
        self._setup_classification_parameters()

        self.logger.info("StellarVariabilityService inicializado correctamente")

    def _setup_classification_parameters(self):
        """Configura parámetros para clasificación de tipos estelares"""
        self.classification_params = {
            VariableStarType.DELTA_SCUTI: {
                'period_range': (0.02, 0.3),  # días
                'amplitude_range': (0.003, 0.9),  # magnitudes
                'period_ratios': [0.77, 0.80],  # ratios típicos
                'shape_factor': 'sinusoidal'
            },
            VariableStarType.RR_LYRAE: {
                'period_range': (0.2, 1.0),
                'amplitude_range': (0.2, 2.0),
                'period_ratios': [0.745],
                'shape_factor': 'asymmetric'
            },
            VariableStarType.CEPHEID: {
                'period_range': (1.0, 135.0),
                'amplitude_range': (0.1, 2.0),
                'period_ratios': [0.71],
                'shape_factor': 'sawtooth'
            },
            VariableStarType.ECLIPSING_BINARY: {
                'period_range': (0.1, 1000.0),
                'amplitude_range': (0.01, 3.0),
                'period_ratios': [0.5],  # eclipse secundario
                'shape_factor': 'eclipse'
            },
            VariableStarType.ROTATING_VARIABLE: {
                'period_range': (0.1, 100.0),
                'amplitude_range': (0.001, 0.1),
                'period_ratios': [],
                'shape_factor': 'sinusoidal'
            }
        }

    def detect_variability(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_error: np.ndarray = None,
        significance_threshold: float = 3.0
    ) -> Dict[str, Any]:
        """
        Detecta si una estrella es variable

        Args:
            time: Array de tiempos de observación
            flux: Array de flujos
            flux_error: Array de errores de flujo (opcional)
            significance_threshold: Umbral de significancia para detección

        Returns:
            Diccionario con resultado de detección de variabilidad
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("SciPy no disponible")

        # Limpiar datos
        mask = np.isfinite(time) & np.isfinite(flux)
        if flux_error is not None:
            mask &= np.isfinite(flux_error) & (flux_error > 0)

        time_clean = time[mask]
        flux_clean = flux[mask]
        flux_error_clean = flux_error[mask] if flux_error is not None else None

        # Estadísticas básicas
        mean_flux = np.mean(flux_clean)
        std_flux = np.std(flux_clean)
        rms = np.sqrt(np.mean((flux_clean - mean_flux)**2))

        # Calcular chi-cuadrado reducido
        if flux_error_clean is not None:
            chi2_red = np.sum(((flux_clean - mean_flux) / flux_error_clean)**2) / (len(flux_clean) - 1)
            expected_rms = np.sqrt(np.mean(flux_error_clean**2))
        else:
            # Estimar error fotométrico basado en flujo
            expected_rms = np.sqrt(mean_flux) / mean_flux * 0.001  # 0.1% aproximado
            chi2_red = (std_flux / expected_rms)**2

        # Prueba de variabilidad
        variability_significance = rms / expected_rms
        is_variable = variability_significance > significance_threshold

        # Análisis adicional si es variable
        additional_stats = {}
        if is_variable:
            additional_stats = self._calculate_variability_statistics(
                time_clean, flux_clean, flux_error_clean
            )

        return {
            'is_variable': bool(is_variable),
            'variability_significance': float(variability_significance),
            'rms_variation': float(rms),
            'expected_rms': float(expected_rms),
            'chi2_reduced': float(chi2_red),
            'mean_flux': float(mean_flux),
            'amplitude_percent': float(100 * std_flux / mean_flux),
            'data_points': len(flux_clean),
            'time_span_days': float(time_clean[-1] - time_clean[0]),
            **additional_stats
        }

    def lomb_scargle_periodicity(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_error: np.ndarray = None,
        min_period: float = 0.01,
        max_period: float = 100.0,
        samples_per_peak: int = 5
    ) -> PeriodicityResult:
        """
        Análisis de periodicidad usando Lomb-Scargle

        Args:
            time: Array de tiempos (días)
            flux: Array de flujos
            flux_error: Array de errores (opcional)
            min_period: Período mínimo a buscar (días)
            max_period: Período máximo a buscar (días)
            samples_per_peak: Muestras por pico en periodograma

        Returns:
            PeriodicityResult con el período detectado
        """
        if not ASTROPY_AVAILABLE:
            raise ImportError("Astropy no disponible para análisis Lomb-Scargle")

        # Limpiar datos
        mask = np.isfinite(time) & np.isfinite(flux)
        if flux_error is not None:
            mask &= np.isfinite(flux_error) & (flux_error > 0)

        time_clean = time[mask]
        flux_clean = flux[mask]
        flux_error_clean = flux_error[mask] if flux_error is not None else None

        # Calcular frecuencias
        time_span = time_clean[-1] - time_clean[0]
        min_freq = 1.0 / max_period
        max_freq = 1.0 / min_period
        freq_resolution = 1.0 / (samples_per_peak * time_span)

        frequencies = np.arange(min_freq, max_freq, freq_resolution)

        # Ejecutar Lomb-Scargle
        if flux_error_clean is not None:
            ls = LombScargle(time_clean, flux_clean, flux_error_clean)
        else:
            ls = LombScargle(time_clean, flux_clean)

        power = ls.power(frequencies)

        # Encontrar el período más significativo
        best_freq_idx = np.argmax(power)
        best_frequency = frequencies[best_freq_idx]
        best_period = 1.0 / best_frequency
        max_power = power[best_freq_idx]

        # Calcular significancia
        false_alarm_prob = ls.false_alarm_probability(max_power)
        significance = -np.log10(false_alarm_prob) if false_alarm_prob > 0 else 10

        # Ajustar sinusoide para obtener amplitud y fase
        amplitude, phase_zero, amplitude_error = self._fit_sinusoid(
            time_clean, flux_clean, best_period, flux_error_clean
        )

        # Buscar armónicos
        harmonics = self._find_harmonics(frequencies, power, best_frequency)

        # Estimar error del período
        period_error = self._estimate_period_error(
            frequencies, power, best_freq_idx, significance
        )

        return PeriodicityResult(
            period_days=float(best_period),
            period_error_days=float(period_error),
            amplitude=float(amplitude),
            amplitude_error=float(amplitude_error),
            phase_zero=float(phase_zero),
            significance=float(significance),
            method='lomb_scargle',
            harmonics=[float(h) for h in harmonics]
        )

    def detect_flare_events(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_error: np.ndarray = None,
        detection_threshold: float = 3.0,
        min_duration_minutes: float = 1.0,
        max_duration_hours: float = 12.0
    ) -> List[FlareEvent]:
        """
        Detecta eventos de fulguración estelar

        Args:
            time: Array de tiempos (días)
            flux: Array de flujos
            flux_error: Array de errores (opcional)
            detection_threshold: Umbral sigma para detección
            min_duration_minutes: Duración mínima de fulguración
            max_duration_hours: Duración máxima de fulguración

        Returns:
            Lista de eventos de fulguración detectados
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("SciPy no disponible")

        # Limpiar datos
        mask = np.isfinite(time) & np.isfinite(flux)
        if flux_error is not None:
            mask &= np.isfinite(flux_error) & (flux_error > 0)

        time_clean = time[mask]
        flux_clean = flux[mask]
        flux_error_clean = flux_error[mask] if flux_error is not None else None

        # Suavizar curva de luz para establecer línea base
        window_size = max(10, len(flux_clean) // 50)
        if window_size % 2 == 0:
            window_size += 1

        baseline = signal.savgol_filter(flux_clean, window_size, 3)

        # Calcular residuos
        residuals = flux_clean - baseline

        # Estimar ruido
        if flux_error_clean is not None:
            noise_level = np.median(flux_error_clean)
        else:
            # Usar MAD (Median Absolute Deviation) para estimar ruido
            noise_level = np.median(np.abs(residuals - np.median(residuals))) * 1.4826

        # Detectar puntos por encima del umbral
        detection_mask = residuals > detection_threshold * noise_level

        # Agrupar puntos consecutivos en eventos
        flare_events = []
        if np.any(detection_mask):
            event_starts = np.where(np.diff(np.concatenate(([False], detection_mask))))[0]
            event_ends = np.where(np.diff(np.concatenate((detection_mask, [False]))))[0]

            for start_idx, end_idx in zip(event_starts, event_ends):
                # Verificar duración
                duration_days = time_clean[end_idx] - time_clean[start_idx]
                duration_minutes = duration_days * 24 * 60

                if min_duration_minutes <= duration_minutes <= max_duration_hours * 60:
                    # Encontrar pico
                    event_flux = flux_clean[start_idx:end_idx+1]
                    peak_idx = start_idx + np.argmax(event_flux)

                    # Calcular parámetros del flare
                    amplitude = flux_clean[peak_idx] - baseline[peak_idx]

                    # Estimar tiempos de rise y decay
                    rise_time = (time_clean[peak_idx] - time_clean[start_idx]) * 24 * 60  # minutos
                    decay_time = (time_clean[end_idx] - time_clean[peak_idx]) * 24 * 60

                    # Estimar energía equivalente (aproximada)
                    energy_equivalent = amplitude * duration_minutes * baseline[peak_idx]

                    # Calcular confianza basada en SNR
                    snr = amplitude / noise_level
                    confidence = min(snr / 10.0, 1.0)

                    flare_event = FlareEvent(
                        start_time=float(time_clean[start_idx]),
                        peak_time=float(time_clean[peak_idx]),
                        end_time=float(time_clean[end_idx]),
                        duration_minutes=float(duration_minutes),
                        amplitude=float(amplitude),
                        energy_equivalent=float(energy_equivalent),
                        rise_time=float(rise_time),
                        decay_time=float(decay_time),
                        confidence=float(confidence)
                    )

                    flare_events.append(flare_event)

        return flare_events

    def classify_variable_star(
        self,
        periodicity_result: PeriodicityResult,
        variability_stats: Dict[str, Any],
        stellar_properties: Dict[str, Any] = None
    ) -> VariabilityClassification:
        """
        Clasifica el tipo de estrella variable

        Args:
            periodicity_result: Resultado del análisis de periodicidad
            variability_stats: Estadísticas de variabilidade
            stellar_properties: Propiedades estelares (opcional)

        Returns:
            VariabilityClassification con el tipo más probable
        """
        period = periodicity_result.period_days
        amplitude = periodicity_result.amplitude

        # Calcular scores para cada tipo
        type_scores = {}

        for star_type, params in self.classification_params.items():
            score = self._calculate_classification_score(
                period, amplitude, periodicity_result, params
            )
            type_scores[star_type] = score

        # Encontrar el tipo más probable
        best_type = max(type_scores, key=type_scores.get)
        best_confidence = type_scores[best_type]

        # Crear clasificaciones alternativas
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
        alternatives = [
            {'type': str(t.value), 'confidence': float(s)}
            for t, s in sorted_types[1:4]  # Top 3 alternativas
            if s > 0.1
        ]

        # Características específicas del tipo detectado
        characteristics = self._extract_type_characteristics(
            best_type, periodicity_result, variability_stats
        )

        return VariabilityClassification(
            star_type=best_type,
            confidence=float(best_confidence),
            period_days=float(period),
            amplitude_range=[float(amplitude * 0.8), float(amplitude * 1.2)],
            characteristics=characteristics,
            alternative_classifications=alternatives
        )

    def comprehensive_variability_analysis(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_error: np.ndarray = None,
        target_name: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Análisis completo de variabilidad estelar

        Args:
            time: Array de tiempos
            flux: Array de flujos
            flux_error: Array de errores (opcional)
            target_name: Nombre del objetivo

        Returns:
            Diccionario con análisis completo
        """
        self.logger.info(f"Iniciando análisis completo de variabilidad para {target_name}")

        results = {
            'target_name': target_name,
            'analysis_timestamp': datetime.now().isoformat(),
            'data_quality': {
                'points': len(time),
                'time_span_days': float(time[-1] - time[0]),
                'mean_flux': float(np.mean(flux)),
                'completeness': float(len(time) / (time[-1] - time[0]) * np.median(np.diff(time)))
            }
        }

        try:
            # 1. Detección de variabilidad
            variability = self.detect_variability(time, flux, flux_error)
            results['variability_detection'] = variability

            if variability['is_variable']:
                # 2. Análisis de periodicidad
                try:
                    periodicity = self.lomb_scargle_periodicity(time, flux, flux_error)
                    results['periodicity_analysis'] = {
                        'period_days': periodicity.period_days,
                        'period_error_days': periodicity.period_error_days,
                        'amplitude': periodicity.amplitude,
                        'significance': periodicity.significance,
                        'harmonics': periodicity.harmonics
                    }

                    # 3. Clasificación
                    classification = self.classify_variable_star(periodicity, variability)
                    results['classification'] = {
                        'star_type': classification.star_type.value,
                        'confidence': classification.confidence,
                        'characteristics': classification.characteristics,
                        'alternatives': classification.alternative_classifications
                    }

                except BiologyError as e:
                    self.logger.warning(f"Error en análisis de periodicidad: {e}")
                    results['periodicity_analysis'] = {'error': str(e)}

                # 4. Detección de flares
                try:
                    flares = self.detect_flare_events(time, flux, flux_error)
                    results['flare_detection'] = {
                        'events_detected': len(flares),
                        'events': [
                            {
                                'peak_time': f.peak_time,
                                'duration_minutes': f.duration_minutes,
                                'amplitude': f.amplitude,
                                'confidence': f.confidence
                            }
                            for f in flares
                        ]
                    }
                except BiologyError as e:
                    self.logger.warning(f"Error en detección de flares: {e}")
                    results['flare_detection'] = {'error': str(e)}

            else:
                results['message'] = "Estrella no variable detectada"

        except BiologyError as e:
            self.logger.error(f"Error en análisis de {target_name}: {e}")
            results['error'] = str(e)

        self.logger.info(f"Análisis completado para {target_name}")
        return results

    def _calculate_variability_statistics(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_error: np.ndarray = None
    ) -> Dict[str, Any]:
        """Calcula estadísticas adicionales de variabilidad"""
        stats = {}

        # Skewness y kurtosis
        mean_flux = np.mean(flux)
        std_flux = np.std(flux)

        if std_flux > 0:
            skewness = np.mean(((flux - mean_flux) / std_flux)**3)
            kurtosis = np.mean(((flux - mean_flux) / std_flux)**4) - 3
        else:
            skewness = 0
            kurtosis = 0

        stats['skewness'] = float(skewness)
        stats['kurtosis'] = float(kurtosis)

        # Welch-Stetson variability index
        if flux_error is not None and len(flux) > 1:
            normalized_residuals = (flux - mean_flux) / flux_error
            j_index = np.sqrt(len(flux) / (len(flux) - 1)) * np.mean(normalized_residuals**2 - 1)
            stats['welch_stetson_j'] = float(j_index)

        return stats

    def _fit_sinusoid(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        period: float,
        flux_error: np.ndarray = None
    ) -> tuple:
        """Ajusta sinusoide para obtener amplitud y fase"""
        def sinusoid(t, amplitude, phase, offset):
            return amplitude * np.sin(2 * np.pi * t / period + phase) + offset

        # Estimaciones iniciales
        mean_flux = np.mean(flux)
        amplitude_guess = np.std(flux)

        try:
            if flux_error is not None:
                popt, pcov = curve_fit(
                    sinusoid, time, flux,
                    p0=[amplitude_guess, 0, mean_flux],
                    sigma=flux_error,
                    maxfev=1000
                )
            else:
                popt, pcov = curve_fit(
                    sinusoid, time, flux,
                    p0=[amplitude_guess, 0, mean_flux],
                    maxfev=1000
                )

            amplitude = abs(popt[0])
            phase_zero = popt[1] % (2 * np.pi)
            amplitude_error = np.sqrt(pcov[0, 0]) if pcov is not None else amplitude * 0.1

            return amplitude, phase_zero, amplitude_error

        except BiologyError:
            return amplitude_guess, 0.0, amplitude_guess * 0.1

    def _find_harmonics(
        self,
        frequencies: np.ndarray,
        power: np.ndarray,
        fundamental_freq: float,
        num_harmonics: int = 5
    ) -> List[float]:
        """Encuentra armónicos del período fundamental"""
        harmonics = []

        for n in range(2, num_harmonics + 2):
            harmonic_freq = n * fundamental_freq

            # Buscar pico cerca de la frecuencia armónica
            freq_tolerance = fundamental_freq * 0.1
            mask = np.abs(frequencies - harmonic_freq) < freq_tolerance

            if np.any(mask):
                harmonic_power = np.max(power[mask])
                # Solo incluir si tiene potencia significativa
                if harmonic_power > 0.1 * np.max(power):
                    harmonic_period = 1.0 / harmonic_freq
                    harmonics.append(harmonic_period)

        return harmonics

    def _estimate_period_error(
        self,
        frequencies: np.ndarray,
        power: np.ndarray,
        best_idx: int,
        significance: float
    ) -> float:
        """Estima error del período basado en ancho del pico"""
        try:
            # Encontrar FWHM del pico principal
            max_power = power[best_idx]
            half_max = max_power / 2.0

            # Buscar hacia los lados
            left_idx = best_idx
            while left_idx > 0 and power[left_idx] > half_max:
                left_idx -= 1

            right_idx = best_idx
            while right_idx < len(power) - 1 and power[right_idx] > half_max:
                right_idx += 1

            if right_idx > left_idx:
                freq_width = frequencies[right_idx] - frequencies[left_idx]
                best_freq = frequencies[best_idx]
                period_error = freq_width / (best_freq**2)
                return period_error

        except BiologyError:
            pass

        # Error por defecto basado en significancia
        return 1.0 / (frequencies[best_idx]**2 * np.sqrt(significance))

    def _calculate_classification_score(
        self,
        period: float,
        amplitude: float,
        periodicity_result: PeriodicityResult,
        params: Dict[str, Any]
    ) -> float:
        """Calcula score de clasificación para un tipo de estrella"""
        score = 0.0

        # Factor período
        p_min, p_max = params['period_range']
        if p_min <= period <= p_max:
            period_score = 1.0
        elif period < p_min:
            period_score = max(0, 1.0 - (p_min - period) / p_min)
        else:
            period_score = max(0, 1.0 - (period - p_max) / p_max)

        score += period_score * 0.4

        # Factor amplitud
        a_min, a_max = params['amplitude_range']
        if a_min <= amplitude <= a_max:
            amplitude_score = 1.0
        elif amplitude < a_min:
            amplitude_score = max(0, 1.0 - (a_min - amplitude) / a_min)
        else:
            amplitude_score = max(0, 1.0 - (amplitude - a_max) / a_max)

        score += amplitude_score * 0.3

        # Factor significancia
        significance_score = min(periodicity_result.significance / 10.0, 1.0)
        score += significance_score * 0.3

        return score

    def _extract_type_characteristics(
        self,
        star_type: VariableStarType,
        periodicity_result: PeriodicityResult,
        variability_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extrae características específicas del tipo de estrella"""
        characteristics = {
            'period_days': periodicity_result.period_days,
            'amplitude': periodicity_result.amplitude,
            'significance': periodicity_result.significance
        }

        if star_type == VariableStarType.DELTA_SCUTI:
            characteristics.update({
                'pulsation_mode': 'radial' if periodicity_result.amplitude > 0.1 else 'non_radial',
                'harmonics_detected': len(periodicity_result.harmonics) > 0
            })

        elif star_type == VariableStarType.RR_LYRAE:
            characteristics.update({
                'subtype': 'RRab' if periodicity_result.amplitude > 0.5 else 'RRc',
                'asymmetry_factor': variability_stats.get('skewness', 0)
            })

        elif star_type == VariableStarType.ECLIPSING_BINARY:
            characteristics.update({
                'eclipse_depth': periodicity_result.amplitude,
                'secondary_eclipse': 0.5 in [h/periodicity_result.period_days for h in periodicity_result.harmonics]
            })

        return characteristics


# Función de utilidad para testing rápido
def stellar_variability_example():
    """
    Ejemplo rápido de uso del servicio de variabilidad estelar
    """
    print("=== Ejemplo de Servicio de Variabilidad Estelar ===\n")

    # Generar datos sintéticos de una variable Delta Scuti
    np.random.seed(42)
    time = np.linspace(0, 10, 1000)  # 10 días
    period = 0.15  # días
    amplitude = 0.05

    # Señal periódica + ruido
    flux_signal = 1.0 + amplitude * np.sin(2 * np.pi * time / period)
    noise = np.random.normal(0, 0.01, len(time))
    flux = flux_signal + noise
    flux_error = np.full_like(flux, 0.01)

    service = StellarVariabilityService()

    try:
        # Análisis completo
        result = service.comprehensive_variability_analysis(
            time, flux, flux_error, "Synthetic Delta Scuti"
        )

        print(f"Objetivo: {result['target_name']}")
        print(f"Variable: {result['variability_detection']['is_variable']}")

        if 'periodicity_analysis' in result and 'error' not in result['periodicity_analysis']:
            print(f"Período detectado: {result['periodicity_analysis']['period_days']:.4f} días")
            print(f"Amplitud: {result['periodicity_analysis']['amplitude']:.4f}")
            print(f"Significancia: {result['periodicity_analysis']['significance']:.1f}")

        if 'classification' in result:
            print(f"Tipo clasificado: {result['classification']['star_type']}")
            print(f"Confianza: {result['classification']['confidence']:.2f}")

        if 'flare_detection' in result:
            print(f"Flares detectados: {result['flare_detection']['events_detected']}")

        print("\n✅ Ejemplo completado exitosamente")

    except BiologyError as e:
        print(f"Error en ejemplo: {e}")


if __name__ == "__main__":
    stellar_variability_example()