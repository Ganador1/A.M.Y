"""
AXIOM - Servicio Avanzado de Lightkurve
Análisis BLS, detección multi-planeta y procesamiento de curvas de luz de TESS/Kepler
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from app.exceptions.domain.biology import BiologyError

try:
    import lightkurve as lk
    LIGHTKURVE_AVAILABLE = True
except ImportError:
    LIGHTKURVE_AVAILABLE = False
    logging.warning("Lightkurve no está disponible. Instalando...")


@dataclass
class TransitParameters:
    """Parámetros de tránsito detectado"""
    period: float
    transit_time: float
    duration: float
    depth: float
    snr: float
    confidence: float


@dataclass
class MultiPlanetSystem:
    """Sistema multi-planeta detectado"""
    target_name: str
    planets: List[TransitParameters]
    host_star_properties: Dict[str, Any]
    analysis_timestamp: datetime
    quality_metrics: Dict[str, float]


class LightkurveAdvancedService:
    """
    Servicio avanzado para análisis de curvas de luz usando Lightkurve

    Capacidades:
    - Análisis BLS (Box-Least Squares) automatizado
    - Detección multi-planeta iterativa
    - Enmascaramiento inteligente de tránsitos
    - Modelado sintético de tránsitos
    - Procesamiento FFI de TESS
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        if not LIGHTKURVE_AVAILABLE:
            self.logger.error("Lightkurve no disponible. Funcionalidad limitada.")
            return

        self.logger.info("LightkurveAdvancedService inicializado correctamente")

    def analyze_target_comprehensive(
        self,
        target_name: str,
        period_range: Tuple[float, float] = (1.0, 300.0),
        max_planets: int = 5,
        mission: str = "auto"
    ) -> MultiPlanetSystem:
        """
        Análisis completo de un objetivo para detección multi-planeta

        Args:
            target_name: Nombre del objetivo (ej. "TOI-715", "Kepler-442")
            period_range: Rango de períodos a buscar (días)
            max_planets: Número máximo de planetas a detectar
            mission: Misión específica ("TESS", "Kepler", "auto")

        Returns:
            MultiPlanetSystem con todos los planetas detectados
        """
        if not LIGHTKURVE_AVAILABLE:
            raise ImportError("Lightkurve no disponible")

        self.logger.info(f"Iniciando análisis completo de {target_name}")

        try:
            # 1. Descarga y procesamiento inicial
            light_curve = self._download_and_process_lightcurve(target_name, mission)

            # 2. Detección iterativa de planetas
            detected_planets = self._iterative_planet_detection(
                light_curve, period_range, max_planets
            )

            # 3. Propiedades estelares
            star_properties = self._get_stellar_properties(target_name)

            # 4. Métricas de calidad
            quality_metrics = self._calculate_quality_metrics(light_curve, detected_planets)

            result = MultiPlanetSystem(
                target_name=target_name,
                planets=detected_planets,
                host_star_properties=star_properties,
                analysis_timestamp=datetime.now(),
                quality_metrics=quality_metrics
            )

            self.logger.info(f"Análisis completado: {len(detected_planets)} planetas detectados")
            return result

        except BiologyError as e:
            self.logger.error(f"Error en análisis de {target_name}: {str(e)}")
            raise

    def _download_and_process_lightcurve(
        self,
        target_name: str,
        mission: str = "auto"
    ) -> 'lk.LightCurve':
        """
        Descarga y procesa la curva de luz

        Args:
            target_name: Nombre del objetivo
            mission: Misión específica o "auto"

        Returns:
            Curva de luz procesada y limpia
        """
        # Búsqueda automática de datos
        if mission == "auto":
            search_result = lk.search_lightcurve(target_name)
        else:
            search_result = lk.search_lightcurve(target_name, mission=mission)

        if len(search_result) == 0:
            raise ValueError(f"No se encontraron datos para {target_name}")

        # Priorizar TESS SPOC si está disponible
        if mission == "auto":
            spoc_results = search_result[search_result.author == 'SPOC']
            if len(spoc_results) > 0:
                search_result = spoc_results

        # Descargar todos los sectores/cuartos disponibles
        lc_collection = search_result.download_all()

        # Procesar y limpiar
        lc = lc_collection.stitch()
        lc = lc.remove_nans().remove_outliers(sigma=5)

        # Aplanar para remover variabilidad estelar
        lc_flat = lc.flatten(window_length=901, polyorder=2)

        self.logger.info(f"Curva de luz procesada: {len(lc_flat)} puntos")
        return lc_flat

    def _iterative_planet_detection(
        self,
        light_curve: 'lk.LightCurve',
        period_range: Tuple[float, float],
        max_planets: int
    ) -> List[TransitParameters]:
        """
        Detección iterativa de múltiples planetas usando BLS

        Args:
            light_curve: Curva de luz procesada
            period_range: Rango de períodos (días)
            max_planets: Máximo número de planetas

        Returns:
            Lista de planetas detectados
        """
        detected_planets = []
        working_lc = light_curve.copy()

        periods = np.linspace(period_range[0], period_range[1], 10000)

        for planet_num in range(max_planets):
            self.logger.info(f"Buscando planeta #{planet_num + 1}")

            # Análisis BLS
            bls = working_lc.to_periodogram(
                method='bls',
                period=periods,
                frequency_factor=500
            )

            # Extraer parámetros del mejor candidato
            period = bls.period_at_max_power
            transit_time = bls.transit_time_at_max_power
            duration = bls.duration_at_max_power

            # Calcular métricas adicionales
            depth, snr, confidence = self._calculate_transit_metrics(
                bls, period, transit_time, duration
            )

            # Verificar si el candidato es significativo
            if snr < 5.0 or confidence < 0.7:
                self.logger.info(f"Deteniendo búsqueda: SNR={snr:.1f}, Confianza={confidence:.2f}")
                break

            # Crear parámetros del planeta
            planet = TransitParameters(
                period=float(period.value),
                transit_time=float(transit_time.value),
                duration=float(duration.value),
                depth=depth,
                snr=snr,
                confidence=confidence
            )

            detected_planets.append(planet)

            # Enmascarar tránsitos para próxima iteración
            transit_mask = bls.get_transit_mask(
                period=period,
                transit_time=transit_time,
                duration=duration
            )

            working_lc = working_lc[~transit_mask]

            # Verificar si quedan suficientes datos
            if len(working_lc) < len(light_curve) * 0.5:
                self.logger.info("Deteniendo búsqueda: pocos datos restantes")
                break

        return detected_planets

    def _calculate_transit_metrics(
        self,
        bls: 'lk.BoxLeastSquaresPeriodogram',
        period: float,
        transit_time: float,
        duration: float
    ) -> Tuple[float, float, float]:
        """
        Calcula métricas de calidad del tránsito

        Args:
            bls: Periodograma BLS
            period: Período del tránsito
            transit_time: Tiempo de tránsito
            duration: Duración del tránsito

        Returns:
            (depth, snr, confidence) del tránsito
        """
        # Obtener modelo de tránsito
        transit_model = bls.get_transit_model(
            period=period,
            transit_time=transit_time,
            duration=duration
        )

        # Calcular profundidad del tránsito
        baseline = np.median(transit_model.flux.value)
        transit_depth = baseline - np.min(transit_model.flux.value)
        depth_ppm = transit_depth * 1e6

        # SNR basado en la potencia BLS
        max_power = bls.max_power
        noise_level = np.std(bls.power.value)
        snr = max_power / noise_level if noise_level > 0 else 0

        # Confianza basada en múltiples factores
        # Factor 1: Potencia relativa
        power_factor = min(max_power / 0.1, 1.0)  # Normalizado a 0.1

        # Factor 2: Duración razonable
        duration_hours = duration * 24
        duration_factor = 1.0 if 0.5 <= duration_hours <= 12 else 0.5

        # Factor 3: Profundidad detectable
        depth_factor = min(depth_ppm / 100, 1.0)  # Normalizado a 100 ppm

        confidence = (power_factor * duration_factor * depth_factor) ** 0.5

        return depth_ppm, float(snr), confidence

    def _get_stellar_properties(self, target_name: str) -> Dict[str, Any]:
        """
        Obtiene propiedades estelares desde bases de datos

        Args:
            target_name: Nombre del objetivo

        Returns:
            Diccionario con propiedades estelares
        """
        # Implementación básica - puede expandirse con APIs externas
        return {
            "target_name": target_name,
            "stellar_radius": None,
            "stellar_mass": None,
            "stellar_temperature": None,
            "stellar_magnitude": None,
            "coordinates": None,
            "distance": None
        }

    def _calculate_quality_metrics(
        self,
        light_curve: 'lk.LightCurve',
        planets: List[TransitParameters]
    ) -> Dict[str, float]:
        """
        Calcula métricas de calidad del análisis

        Args:
            light_curve: Curva de luz original
            planets: Lista de planetas detectados

        Returns:
            Diccionario con métricas de calidad
        """
        return {
            "data_points": len(light_curve),
            "time_span_days": float(
                (light_curve.time[-1] - light_curve.time[0]).value
            ),
            "rms_noise": float(np.std(light_curve.flux.value)),
            "planets_detected": len(planets),
            "average_snr": np.mean([p.snr for p in planets]) if planets else 0,
            "data_quality_score": self._calculate_data_quality_score(light_curve)
        }

    def _calculate_data_quality_score(self, light_curve: 'lk.LightCurve') -> float:
        """
        Calcula score de calidad de datos (0-1)

        Args:
            light_curve: Curva de luz

        Returns:
            Score de calidad entre 0 y 1
        """
        # Factores de calidad
        factors = []

        # Factor 1: Número de puntos
        n_points = len(light_curve)
        points_factor = min(n_points / 10000, 1.0)
        factors.append(points_factor)

        # Factor 2: Span temporal
        time_span = (light_curve.time[-1] - light_curve.time[0]).value
        time_factor = min(time_span / 365, 1.0)  # Normalizado a 1 año
        factors.append(time_factor)

        # Factor 3: Ruido
        rms_noise = np.std(light_curve.flux.value)
        noise_factor = max(1.0 - rms_noise * 1000, 0.1)  # Invertido
        factors.append(noise_factor)

        # Factor 4: Gaps de datos
        time_diffs = np.diff(light_curve.time.value)
        median_cadence = np.median(time_diffs)
        large_gaps = np.sum(time_diffs > 10 * median_cadence)
        gap_factor = max(1.0 - large_gaps / len(time_diffs), 0.1)
        factors.append(gap_factor)

        return float(np.mean(factors))

    def create_transit_model(
        self,
        light_curve: 'lk.LightCurve',
        planet: TransitParameters
    ) -> 'lk.LightCurve':
        """
        Crea modelo sintético de tránsito

        Args:
            light_curve: Curva de luz base
            planet: Parámetros del planeta

        Returns:
            Modelo de tránsito sintético
        """
        if not LIGHTKURVE_AVAILABLE:
            raise ImportError("Lightkurve no disponible")

        # Crear periodograma BLS temporal para generar modelo
        periods = np.array([planet.period])
        bls = light_curve.to_periodogram(
            method='bls',
            period=periods,
            frequency_factor=100
        )

        # Generar modelo con parámetros específicos
        model = bls.get_transit_model(
            period=planet.period,
            transit_time=planet.transit_time,
            duration=planet.duration
        )

        return model

    def phase_fold_analysis(
        self,
        light_curve: 'lk.LightCurve',
        planet: TransitParameters,
        bin_size: float = 0.01
    ) -> Dict[str, Any]:
        """
        Análisis de plegado de fase para un planeta

        Args:
            light_curve: Curva de luz
            planet: Parámetros del planeta
            bin_size: Tamaño de bins para plegado

        Returns:
            Diccionario con análisis de fase
        """
        if not LIGHTKURVE_AVAILABLE:
            raise ImportError("Lightkurve no disponible")

        # Plegar la curva de luz
        folded_lc = light_curve.fold(
            period=planet.period,
            epoch_time=planet.transit_time
        )

        # Binnear para mejor visualización
        binned_lc = folded_lc.bin(bin_size)

        # Calcular estadísticas de fase
        in_transit_mask = np.abs(folded_lc.phase.value) < (planet.duration / planet.period / 2)
        out_of_transit_mask = ~in_transit_mask

        in_transit_flux = folded_lc.flux.value[in_transit_mask]
        out_of_transit_flux = folded_lc.flux.value[out_of_transit_mask]

        return {
            "folded_lightcurve": folded_lc,
            "binned_lightcurve": binned_lc,
            "in_transit_mean": float(np.mean(in_transit_flux)),
            "out_of_transit_mean": float(np.mean(out_of_transit_flux)),
            "transit_depth": float(np.mean(out_of_transit_flux) - np.mean(in_transit_flux)),
            "phase": folded_lc.phase.value,
            "flux": folded_lc.flux.value
        }

    def validate_planet_candidates(
        self,
        candidates: List[TransitParameters],
        min_snr: float = 7.0,
        min_confidence: float = 0.8
    ) -> List[TransitParameters]:
        """
        Valida candidatos planetarios con criterios estrictos

        Args:
            candidates: Lista de candidatos
            min_snr: SNR mínimo requerido
            min_confidence: Confianza mínima requerida

        Returns:
            Lista filtrada de candidatos válidos
        """
        validated = []

        for candidate in candidates:
            # Criterios de validación
            valid_snr = candidate.snr >= min_snr
            valid_confidence = candidate.confidence >= min_confidence
            valid_period = 0.5 <= candidate.period <= 500  # Días
            valid_duration = 0.5 <= candidate.duration * 24 <= 24  # Horas

            if all([valid_snr, valid_confidence, valid_period, valid_duration]):
                validated.append(candidate)
                self.logger.info(f"Candidato validado: P={candidate.period:.2f}d, SNR={candidate.snr:.1f}")
            else:
                self.logger.info(f"Candidato rechazado: P={candidate.period:.2f}d, criterios no cumplidos")

        return validated


# Función de utilidad para testing rápido
def quick_analysis_example():
    """
    Ejemplo rápido de uso del servicio
    """
    if not LIGHTKURVE_AVAILABLE:
        print("Lightkurve no disponible para el ejemplo")
        return

    service = LightkurveAdvancedService()

    # Análisis de ejemplo con TOI-715 (sistema conocido)
    try:
        result = service.analyze_target_comprehensive(
            target_name="TOI-715",
            period_range=(1.0, 50.0),
            max_planets=3
        )

        print(f"\n=== Análisis de {result.target_name} ===")
        print(f"Planetas detectados: {len(result.planets)}")

        for i, planet in enumerate(result.planets, 1):
            print(f"\nPlaneta {i}:")
            print(f"  Período: {planet.period:.2f} días")
            print(f"  Duración: {planet.duration * 24:.1f} horas")
            print(f"  Profundidad: {planet.depth:.0f} ppm")
            print(f"  SNR: {planet.snr:.1f}")
            print(f"  Confianza: {planet.confidence:.2f}")

        print(f"\nMétricas de calidad:")
        for key, value in result.quality_metrics.items():
            print(f"  {key}: {value}")

    except BiologyError as e:
        print(f"Error en ejemplo: {e}")


if __name__ == "__main__":
    quick_analysis_example()