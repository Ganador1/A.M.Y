"""
Astronomy Light Curve Analysis Service - AXIOM Advanced
=======================================================

Servicio especializado para análisis de curvas de luz astronómicas con
algoritmos avanzados de detección de exoplanetas y análisis temporal.

Características:
- Box Least Squares (BLS) para detección de tránsitos planetarios
- Análisis de periodicidad con Lomb-Scargle periodogram
- Detección automática de características estelares
- Análisis de variabilidad y clasificación de estrellas variables
- Filtrado de ruido y outliers
- Estimación de parámetros físicos planetarios

Algoritmos implementados:
- BLS (Box Least Squares) para tránsitos
- Lomb-Scargle periodogram para periodicidad
- Phase folding y binning inteligente
- Análisis de profundidad y duración de tránsitos
- Estimación de radio planetario relativo

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import scipy.signal
from scipy.optimize import minimize
from scipy.stats import chi2

from app.services.base_service import BaseService

logger = logging.getLogger(__name__)

# Lomb-Scargle disponible en scipy
try:
    from scipy.signal import lombscargle
    LOMBSCARGLE_AVAILABLE = True
except ImportError:
    LOMBSCARGLE_AVAILABLE = False


@dataclass
class LightCurveData:
    """Datos de curva de luz"""
    time: np.ndarray  # Tiempo en días julianos o relativos
    flux: np.ndarray  # Flujo normalizado o magnitud
    flux_err: Optional[np.ndarray] = None  # Errores del flujo
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BLSResult:
    """Resultado del análisis BLS"""
    best_period: float
    best_epoch: float  # Tiempo del primer tránsito
    best_duration: float  # Duración del tránsito
    best_depth: float  # Profundidad del tránsito
    best_power: float  # Poder estadístico del BLS
    
    # Estadísticas
    signal_to_noise: float
    false_alarm_probability: float
    
    # Arrays completos
    periods: np.ndarray
    powers: np.ndarray
    
    # Parámetros físicos estimados
    planet_radius_ratio: float  # Rp/R*
    impact_parameter: float
    
    # Curva de luz plegada
    phase: np.ndarray
    folded_flux: np.ndarray


@dataclass
class PeriodicityResult:
    """Resultado del análisis de periodicidad"""
    best_period: float
    best_power: float
    significance: float
    
    periods: np.ndarray
    powers: np.ndarray
    
    # Clasificación de tipo de variabilidad
    variability_type: str
    confidence: float


class AstronomyLightCurveService(BaseService):
    """
    Servicio de análisis de curvas de luz astronómicas
    """
    
    def __init__(self):
        super().__init__("AstronomyLightCurve")
        
        # Configuración de BLS
        self.bls_config = {
            'min_period': 0.5,  # días
            'max_period': 50.0,  # días
            'period_resolution': 10000,
            'duration_grid_factor': 0.1,
            'min_duration_hours': 1.0,
            'max_duration_hours': 24.0
        }
        
        # Configuración de Lomb-Scargle
        self.ls_config = {
            'min_frequency': 0.1,  # 1/días
            'max_frequency': 10.0,  # 1/días
            'samples_per_peak': 5
        }
        
        logger.info("🌟 AstronomyLightCurveService inicializado")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process astronomy light curve analysis request
        
        Args:
            request_data: Request containing light curve data and analysis parameters
            
        Returns:
            Analysis results
        """
        try:
            self.log_request(request_data)
            
            # Validate input
            validation = self.validate_scientific_input(request_data)
            if not validation["valid"]:
                return self.handle_error(ValueError(validation["error"]), "input_validation")
            
            # Extract parameters
            operation = request_data.get("operation", "bls_analysis")
            time_data = request_data.get("time", [])
            flux_data = request_data.get("flux", [])
            flux_err = request_data.get("flux_err")
            target_name = request_data.get("target_name", "Unknown")
            
            # Route to appropriate analysis method
            if operation == "bls_analysis":
                result = await self.analyze_light_curve_bls(
                    time=time_data,
                    flux=flux_data,
                    flux_err=flux_err,
                    target_name=target_name
                )
            elif operation == "variability_detection":
                result = await self.detect_stellar_variability(
                    time=time_data,
                    flux=flux_data,
                    flux_err=flux_err,
                    classification_mode=request_data.get("classification_mode", "comprehensive")
                )
            else:
                return self.handle_error(ValueError(f"Unknown operation: {operation}"), "operation_routing")
            
            # Format output
            response = self.format_scientific_output(result)
            self.log_response(response)
            
            return response
            
        except Exception as e:
            return self.handle_error(e, "process_request")
    
    async def analyze_light_curve_bls(
        self,
        time: List[float],
        flux: List[float],
        flux_err: Optional[List[float]] = None,
        target_name: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Análisis completo de curva de luz con BLS para detección de exoplanetas
        
        Args:
            time: Tiempos de observación (días)
            flux: Flujo normalizado
            flux_err: Errores del flujo (opcional)
            target_name: Nombre del objetivo
            
        Returns:
            Resultado completo del análisis BLS
        """
        try:
            logger.info(f"🔍 Analizando curva de luz con BLS: {target_name}")
            
            # Validar y preparar datos
            lc_data = self._prepare_light_curve_data(time, flux, flux_err)
            
            # Pre-procesamiento
            lc_processed = await self._preprocess_light_curve(lc_data)
            
            # Ejecutar BLS
            bls_result = await self._run_bls_analysis(lc_processed)
            
            # Análisis de significancia
            significance = await self._assess_bls_significance(lc_processed, bls_result)
            
            # Estimación de parámetros físicos
            physical_params = await self._estimate_physical_parameters(lc_processed, bls_result)
            
            # Análisis de periodicidad complementario
            periodicity = await self._analyze_periodicity_lombscargle(lc_processed)
            
            return {
                "target_name": target_name,
                "bls_analysis": {
                    "best_period_days": bls_result.best_period,
                    "transit_epoch": bls_result.best_epoch,
                    "transit_duration_hours": bls_result.best_duration * 24,
                    "transit_depth_ppm": bls_result.best_depth * 1e6,
                    "bls_power": bls_result.best_power,
                    "signal_to_noise": bls_result.signal_to_noise,
                    "false_alarm_probability": bls_result.false_alarm_probability
                },
                "physical_parameters": {
                    "planet_radius_ratio": bls_result.planet_radius_ratio,
                    "planet_radius_earth_radii": physical_params.get("planet_radius_earth", 0.0),
                    "impact_parameter": bls_result.impact_parameter,
                    "stellar_density_solar": physical_params.get("stellar_density", 1.0)
                },
                "periodicity_analysis": {
                    "primary_period": periodicity.best_period,
                    "periodicity_power": periodicity.best_power,
                    "variability_type": periodicity.variability_type,
                    "confidence": periodicity.confidence
                },
                "data_quality": {
                    "n_observations": len(lc_processed.time),
                    "time_span_days": np.ptp(lc_processed.time),
                    "median_uncertainty": np.median(lc_processed.flux_err) if lc_processed.flux_err is not None else 0.0,
                    "outlier_fraction": self._calculate_outlier_fraction(lc_processed)
                },
                "significance_assessment": significance,
                "folded_light_curve": {
                    "phase": bls_result.phase.tolist(),
                    "flux": bls_result.folded_flux.tolist(),
                    "period_used": bls_result.best_period
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error en análisis BLS: {str(e)}")
            raise
    
    async def detect_stellar_variability(
        self,
        time: List[float],
        flux: List[float],
        flux_err: Optional[List[float]] = None,
        classification_mode: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Detección y clasificación de variabilidad estelar
        
        Args:
            time: Tiempos de observación
            flux: Flujo observado
            flux_err: Errores del flujo
            classification_mode: Modo de clasificación ('fast', 'comprehensive')
            
        Returns:
            Análisis de variabilidad estelar
        """
        try:
            logger.info("🌟 Detectando variabilidad estelar")
            
            # Preparar datos
            lc_data = self._prepare_light_curve_data(time, flux, flux_err)
            lc_processed = await self._preprocess_light_curve(lc_data)
            
            # Análisis de periodicidad
            periodicity = await self._analyze_periodicity_lombscargle(lc_processed)
            
            # Estadísticas de variabilidad
            variability_stats = self._calculate_variability_statistics(lc_processed)
            
            # Clasificación de tipo de estrella variable
            classification = await self._classify_variable_star(
                lc_processed, periodicity, variability_stats, classification_mode
            )
            
            # Análisis de armónicos
            harmonics = await self._analyze_harmonics(lc_processed, periodicity.best_period)
            
            return {
                "variability_detected": variability_stats["is_variable"],
                "variability_amplitude": variability_stats["amplitude"],
                "variability_index": variability_stats["variability_index"],
                "primary_period": periodicity.best_period,
                "period_confidence": periodicity.confidence,
                "variable_star_type": classification["type"],
                "classification_confidence": classification["confidence"],
                "classification_features": classification["features"],
                "harmonics_detected": harmonics["n_harmonics"],
                "fundamental_frequency": harmonics["fundamental_freq"],
                "frequency_ratios": harmonics["frequency_ratios"],
                "periodicity_strength": periodicity.best_power,
                "data_statistics": variability_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error en detección de variabilidad: {str(e)}")
            raise
    
    # ========== MÉTODOS DE ANÁLISIS BLS ==========
    
    def _prepare_light_curve_data(
        self,
        time: List[float],
        flux: List[float],
        flux_err: Optional[List[float]] = None
    ) -> LightCurveData:
        """Prepara y valida datos de curva de luz"""
        
        time_arr = np.array(time)
        flux_arr = np.array(flux)
        flux_err_arr = np.array(flux_err) if flux_err else None
        
        # Validación básica
        if len(time_arr) != len(flux_arr):
            raise ValueError("Tiempo y flujo deben tener la misma longitud")
        
        if len(time_arr) < 50:
            raise ValueError("Se requieren al menos 50 puntos para análisis BLS")
        
        # Ordenar por tiempo
        sort_idx = np.argsort(time_arr)
        time_arr = time_arr[sort_idx]
        flux_arr = flux_arr[sort_idx]
        if flux_err_arr is not None:
            flux_err_arr = flux_err_arr[sort_idx]
        
        return LightCurveData(
            time=time_arr,
            flux=flux_arr,
            flux_err=flux_err_arr,
            metadata={"n_points": len(time_arr), "time_span": np.ptp(time_arr)}
        )
    
    async def _preprocess_light_curve(self, lc_data: LightCurveData) -> LightCurveData:
        """Pre-procesamiento de curva de luz"""
        
        # Normalización del flujo
        flux_normalized = lc_data.flux / np.median(lc_data.flux)
        
        # Detección y filtrado de outliers
        flux_clean, mask = self._remove_outliers_sigma_clip(flux_normalized, sigma=3.0)
        
        time_clean = lc_data.time[mask]
        flux_err_clean = None
        if lc_data.flux_err is not None:
            flux_err_clean = lc_data.flux_err[mask] / np.median(lc_data.flux)
        
        # Detrending básico (remover tendencias de largo período)
        flux_detrended = self._detrend_light_curve(time_clean, flux_clean)
        
        return LightCurveData(
            time=time_clean,
            flux=flux_detrended,
            flux_err=flux_err_clean,
            metadata={**lc_data.metadata, "preprocessing_applied": True}
        )
    
    async def _run_bls_analysis(self, lc_data: LightCurveData) -> BLSResult:
        """Ejecuta análisis Box Least Squares"""
        
        # Grid de períodos
        periods = np.linspace(
            self.bls_config['min_period'],
            self.bls_config['max_period'],
            self.bls_config['period_resolution']
        )
        
        powers = []
        epochs = []
        durations = []
        depths = []
        
        # Ejecutar BLS para cada período
        for period in periods:
            result = self._bls_single_period(lc_data, period)
            powers.append(result['power'])
            epochs.append(result['epoch'])
            durations.append(result['duration'])
            depths.append(result['depth'])
        
        powers = np.array(powers)
        epochs = np.array(epochs)
        durations = np.array(durations)
        depths = np.array(depths)
        
        # Encontrar mejor resultado
        best_idx = np.argmax(powers)
        best_period = periods[best_idx]
        best_power = powers[best_idx]
        best_epoch = epochs[best_idx]
        best_duration = durations[best_idx]
        best_depth = depths[best_idx]
        
        # Calcular signal-to-noise y significancia
        snr = self._calculate_bls_snr(lc_data, best_period, best_depth, best_duration)
        fap = self._calculate_false_alarm_probability(powers, best_power)
        
        # Estimar parámetros físicos
        planet_radius_ratio = np.sqrt(best_depth)
        impact_parameter = self._estimate_impact_parameter(best_duration, best_period)
        
        # Generar curva plegada
        phase, folded_flux = self._fold_light_curve(lc_data, best_period, best_epoch)
        
        return BLSResult(
            best_period=best_period,
            best_epoch=best_epoch,
            best_duration=best_duration,
            best_depth=best_depth,
            best_power=best_power,
            signal_to_noise=snr,
            false_alarm_probability=fap,
            periods=periods,
            powers=powers,
            planet_radius_ratio=planet_radius_ratio,
            impact_parameter=impact_parameter,
            phase=phase,
            folded_flux=folded_flux
        )
    
    def _bls_single_period(self, lc_data: LightCurveData, period: float) -> Dict[str, float]:
        """BLS para un período específico"""
        
        # Grid de duraciones de tránsito
        min_duration = self.bls_config['min_duration_hours'] / 24  # días
        max_duration = min(
            self.bls_config['max_duration_hours'] / 24,
            period * 0.2  # Máximo 20% del período
        )
        
        duration_grid = np.linspace(min_duration, max_duration, 20)
        
        best_power = 0
        best_epoch = 0
        best_duration = min_duration
        best_depth = 0
        
        # Buscar mejor época de tránsito
        epoch_grid = np.linspace(lc_data.time[0], lc_data.time[0] + period, 100)
        
        for epoch in epoch_grid:
            for duration in duration_grid:
                # Calcular estadística BLS
                power, depth = self._calculate_bls_statistic(
                    lc_data, period, epoch, duration
                )
                
                if power > best_power:
                    best_power = power
                    best_epoch = epoch
                    best_duration = duration
                    best_depth = depth
        
        return {
            'power': best_power,
            'epoch': best_epoch,
            'duration': best_duration,
            'depth': best_depth
        }
    
    def _calculate_bls_statistic(
        self,
        lc_data: LightCurveData,
        period: float,
        epoch: float,
        duration: float
    ) -> Tuple[float, float]:
        """Calcula estadística BLS para parámetros dados"""
        
        # Fase de cada observación
        phase = ((lc_data.time - epoch) % period) / period
        
        # Máscara de tránsito
        in_transit = (phase < duration / period) | (phase > (1 - duration / period))
        
        if np.sum(in_transit) < 3:  # Necesitamos al menos 3 puntos en tránsito
            return 0.0, 0.0
        
        # Flujos dentro y fuera del tránsito
        flux_in = lc_data.flux[in_transit]
        flux_out = lc_data.flux[~in_transit]
        
        if len(flux_out) < 3:
            return 0.0, 0.0
        
        # Estadísticas
        mean_in = np.mean(flux_in)
        mean_out = np.mean(flux_out)
        
        # Profundidad del tránsito
        depth = mean_out - mean_in
        
        if depth <= 0:
            return 0.0, 0.0
        
        # Calcular varianzas
        var_in = np.var(flux_in) if len(flux_in) > 1 else 1e-6
        var_out = np.var(flux_out) if len(flux_out) > 1 else 1e-6
        
        # Estadística BLS (aproximación de chi-cuadrado)
        n_in = len(flux_in)
        n_out = len(flux_out)
        
        # Ponderación por número de puntos y varianzas
        weight = (n_in * n_out) / (n_in + n_out)
        power = weight * (depth ** 2) / (var_in / n_in + var_out / n_out + 1e-10)
        
        return power, depth
    
    # ========== MÉTODOS DE ANÁLISIS DE PERIODICIDAD ==========
    
    async def _analyze_periodicity_lombscargle(self, lc_data: LightCurveData) -> PeriodicityResult:
        """Análisis de periodicidad con Lomb-Scargle"""
        
        if not LOMBSCARGLE_AVAILABLE:
            # Implementación alternativa simplificada
            return self._simple_periodicity_analysis(lc_data)
        
        # Grid de frecuencias
        frequencies = np.linspace(
            self.ls_config['min_frequency'],
            self.ls_config['max_frequency'],
            5000
        )
        
        # Calcular periodograma de Lomb-Scargle
        powers = lombscargle(lc_data.time, lc_data.flux, frequencies, normalize=True)
        
        # Encontrar mejor período
        best_idx = np.argmax(powers)
        best_frequency = frequencies[best_idx]
        best_period = 1.0 / best_frequency
        best_power = powers[best_idx]
        
        # Calcular significancia
        significance = self._calculate_ls_significance(powers, best_power)
        
        # Clasificar tipo de variabilidad
        variability_type, confidence = self._classify_periodicity(
            best_period, best_power, significance
        )
        
        return PeriodicityResult(
            best_period=best_period,
            best_power=best_power,
            significance=significance,
            periods=1.0 / frequencies,
            powers=powers,
            variability_type=variability_type,
            confidence=confidence
        )
    
    def _simple_periodicity_analysis(self, lc_data: LightCurveData) -> PeriodicityResult:
        """Análisis de periodicidad simplificado sin Lomb-Scargle"""
        
        # Grid de períodos para análisis directo
        periods = np.linspace(0.1, 20.0, 1000)
        powers = []
        
        for period in periods:
            # Phase folding simple
            phase = (lc_data.time % period) / period
            
            # Binning en fase
            n_bins = 20
            bin_edges = np.linspace(0, 1, n_bins + 1)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            binned_flux = []
            for i in range(n_bins):
                mask = (phase >= bin_edges[i]) & (phase < bin_edges[i + 1])
                if np.sum(mask) > 0:
                    binned_flux.append(np.mean(lc_data.flux[mask]))
                else:
                    binned_flux.append(np.nan)
            
            # Calcular varianza de los bins (power proxy)
            valid_bins = ~np.isnan(binned_flux)
            if np.sum(valid_bins) > 5:
                power = np.var([f for f in binned_flux if not np.isnan(f)])
            else:
                power = 0.0
            
            powers.append(power)
        
        powers = np.array(powers)
        best_idx = np.argmax(powers)
        best_period = periods[best_idx]
        best_power = powers[best_idx]
        
        # Significancia simplificada
        significance = best_power / np.median(powers) if np.median(powers) > 0 else 1.0
        
        variability_type, confidence = self._classify_periodicity(
            best_period, best_power, significance
        )
        
        return PeriodicityResult(
            best_period=best_period,
            best_power=best_power,
            significance=significance,
            periods=periods,
            powers=powers,
            variability_type=variability_type,
            confidence=confidence
        )
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _remove_outliers_sigma_clip(
        self,
        flux: np.ndarray,
        sigma: float = 3.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Remoción de outliers con sigma clipping"""
        
        median_flux = np.median(flux)
        mad = np.median(np.abs(flux - median_flux))
        
        # Usar MAD como estimador robusto de dispersión
        sigma_est = 1.4826 * mad
        
        # Máscara de puntos válidos
        mask = np.abs(flux - median_flux) < sigma * sigma_est
        
        return flux[mask], mask
    
    def _detrend_light_curve(self, time: np.ndarray, flux: np.ndarray) -> np.ndarray:
        """Detrending básico de curva de luz"""
        
        # Ajuste polinomial de orden bajo para remover tendencias
        if len(time) > 100:
            # Para curvas largas, usar polinomio de orden 2
            coeffs = np.polyfit(time, flux, 2)
            trend = np.polyval(coeffs, time)
        else:
            # Para curvas cortas, solo remover offset
            trend = np.median(flux)
        
        return flux - trend + 1.0  # Normalizar a 1
    
    def _calculate_bls_snr(
        self,
        lc_data: LightCurveData,
        period: float,
        depth: float,
        duration: float
    ) -> float:
        """Calcula signal-to-noise ratio del BLS"""
        
        # Estimación simple del SNR
        n_transits = lc_data.metadata["time_span"] / period
        n_points_per_transit = len(lc_data.time) * (duration / period)
        
        # SNR aproximado
        if lc_data.flux_err is not None:
            noise_level = np.median(lc_data.flux_err)
        else:
            noise_level = np.std(lc_data.flux) / np.sqrt(len(lc_data.flux))
        
        snr = depth * np.sqrt(n_transits * n_points_per_transit) / noise_level
        
        return snr
    
    def _calculate_false_alarm_probability(
        self,
        powers: np.ndarray,
        best_power: float
    ) -> float:
        """Calcula probabilidad de falsa alarma"""
        
        # Estimación simple basada en distribución de powers
        n_trials = len(powers)
        rank = np.sum(powers >= best_power)
        
        # FAP aproximada
        fap = rank / n_trials
        
        return max(fap, 1e-6)  # Mínimo FAP
    
    def _estimate_impact_parameter(self, duration: float, period: float) -> float:
        """Estima parámetro de impacto del tránsito"""
        
        # Estimación simplificada asumiendo órbita circular
        # y relación entre duración y parámetro de impacto
        
        # Duración normalizada
        duration_norm = duration / period
        
        # Parámetro de impacto aproximado (0 = central, 1 = grazing)
        if duration_norm > 0.02:  # Tránsito detectable
            impact_param = max(0.0, 1.0 - duration_norm / 0.1)
        else:
            impact_param = 0.5  # Valor por defecto
        
        return min(impact_param, 1.0)
    
    def _fold_light_curve(
        self,
        lc_data: LightCurveData,
        period: float,
        epoch: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Pliega curva de luz con período dado"""
        
        # Calcular fases
        phase = ((lc_data.time - epoch) % period) / period
        
        # Ordenar por fase
        sort_idx = np.argsort(phase)
        
        return phase[sort_idx], lc_data.flux[sort_idx]
    
    async def _assess_bls_significance(
        self,
        lc_data: LightCurveData,
        bls_result: BLSResult
    ) -> Dict[str, Any]:
        """Evalúa significancia del resultado BLS"""
        
        return {
            "detection_confidence": "high" if bls_result.signal_to_noise > 7 else 
                                  "medium" if bls_result.signal_to_noise > 5 else "low",
            "statistical_significance": bls_result.signal_to_noise,
            "false_alarm_probability": bls_result.false_alarm_probability,
            "recommendation": "Planet candidate" if bls_result.signal_to_noise > 7 and 
                            bls_result.false_alarm_probability < 0.01 else "Requires follow-up"
        }
    
    async def _estimate_physical_parameters(
        self,
        lc_data: LightCurveData,
        bls_result: BLSResult
    ) -> Dict[str, float]:
        """Estima parámetros físicos del sistema"""
        
        # Estimaciones simplificadas asumiendo estrella tipo solar
        stellar_radius_solar = 1.0  # R_sun
        stellar_mass_solar = 1.0    # M_sun
        
        # Radio planetario en radios terrestres
        planet_radius_earth = bls_result.planet_radius_ratio * stellar_radius_solar * 109.2  # R_earth
        
        # Densidad estelar aproximada
        stellar_density = self._estimate_stellar_density(bls_result.best_period, bls_result.best_duration)
        
        return {
            "planet_radius_earth": planet_radius_earth,
            "stellar_density": stellar_density,
            "orbital_period_days": bls_result.best_period,
            "semi_major_axis_au": self._estimate_semimajor_axis(bls_result.best_period, stellar_mass_solar)
        }
    
    def _estimate_stellar_density(self, period: float, duration: float) -> float:
        """Estima densidad estelar usando ley de Kepler"""
        
        # Relación aproximada entre duración de tránsito y densidad estelar
        # Asumiendo órbita circular e impacto central
        
        if duration > 0 and period > 0:
            # Densidad en unidades solares
            density_solar = (period / (duration * 24)) ** 2 / 100  # Aproximación simple
            return max(0.1, min(10.0, density_solar))  # Límites físicos razonables
        
        return 1.0  # Valor por defecto (densidad solar)
    
    def _estimate_semimajor_axis(self, period_days: float, stellar_mass_solar: float) -> float:
        """Estima semi-eje mayor usando tercera ley de Kepler"""
        
        # Tercera ley de Kepler: a^3 = G*M*P^2/(4*pi^2)
        # En unidades de AU, M_solar, días
        
        period_years = period_days / 365.25
        a_au = (stellar_mass_solar * period_years ** 2) ** (1/3)
        
        return a_au
    
    def _calculate_variability_statistics(self, lc_data: LightCurveData) -> Dict[str, Any]:
        """Calcula estadísticas de variabilidad"""
        
        flux = lc_data.flux
        
        # Amplitud de variabilidad
        amplitude = np.ptp(flux)  # Peak-to-peak
        
        # Índice de variabilidad (normalized)
        median_flux = np.median(flux)
        mad = np.median(np.abs(flux - median_flux))
        variability_index = mad / median_flux if median_flux > 0 else 0
        
        # Test estadístico de variabilidad
        # Chi-cuadrado reducido si tenemos errores
        if lc_data.flux_err is not None:
            chi2_red = np.sum(((flux - median_flux) / lc_data.flux_err) ** 2) / len(flux)
            is_variable = chi2_red > 2.0
        else:
            # Usar test simple basado en dispersión
            rms = np.std(flux)
            expected_rms = 0.001  # 0.1% para estrella quieta
            is_variable = rms > 3 * expected_rms
        
        return {
            "amplitude": amplitude,
            "variability_index": variability_index,
            "rms_flux": np.std(flux),
            "is_variable": is_variable,
            "skewness": float(scipy.stats.skew(flux)),
            "kurtosis": float(scipy.stats.kurtosis(flux))
        }
    
    async def _classify_variable_star(
        self,
        lc_data: LightCurveData,
        periodicity: PeriodicityResult,
        variability_stats: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """Clasifica tipo de estrella variable"""
        
        # Clasificación básica basada en período y amplitud
        period = periodicity.best_period
        amplitude = variability_stats["amplitude"]
        
        if not variability_stats["is_variable"]:
            return {
                "type": "Constant",
                "confidence": 0.9,
                "features": ["Low amplitude", "No significant periodicity"]
            }
        
        # Clasificación por período y amplitud
        if 0.2 <= period <= 1.0 and amplitude > 0.01:
            star_type = "Delta Scuti"
            confidence = 0.7
        elif 1.0 <= period <= 50.0 and amplitude > 0.05:
            star_type = "Cepheid"
            confidence = 0.6
        elif period > 50.0 and amplitude > 0.1:
            star_type = "Long Period Variable"
            confidence = 0.5
        elif amplitude < 0.01:
            star_type = "Micro-variable"
            confidence = 0.8
        else:
            star_type = "Unclassified Variable"
            confidence = 0.3
        
        features = [
            f"Period: {period:.2f} days",
            f"Amplitude: {amplitude:.4f}",
            f"Variability index: {variability_stats['variability_index']:.4f}"
        ]
        
        return {
            "type": star_type,
            "confidence": confidence,
            "features": features
        }
    
    async def _analyze_harmonics(
        self,
        lc_data: LightCurveData,
        fundamental_period: float
    ) -> Dict[str, Any]:
        """Analiza armónicos del período fundamental"""
        
        # Buscar armónicos (múltiplos y submúltiplos)
        harmonic_ratios = [0.5, 2.0, 3.0, 1.5, 2/3]
        detected_harmonics = []
        
        for ratio in harmonic_ratios:
            test_period = fundamental_period * ratio
            
            # Test simple de periodicidad para este armónico
            phase = (lc_data.time % test_period) / test_period
            
            # Binning y varianza
            n_bins = 10
            bin_flux = []
            for i in range(n_bins):
                mask = (phase >= i/n_bins) & (phase < (i+1)/n_bins)
                if np.sum(mask) > 0:
                    bin_flux.append(np.mean(lc_data.flux[mask]))
            
            if len(bin_flux) > 5:
                power = np.var(bin_flux)
                if power > 0.0001:  # Threshold simple
                    detected_harmonics.append({
                        "ratio": ratio,
                        "period": test_period,
                        "power": power
                    })
        
        return {
            "n_harmonics": len(detected_harmonics),
            "fundamental_freq": 1.0 / fundamental_period,
            "frequency_ratios": [h["ratio"] for h in detected_harmonics],
            "harmonic_powers": [h["power"] for h in detected_harmonics]
        }
    
    def _calculate_outlier_fraction(self, lc_data: LightCurveData) -> float:
        """Calcula fracción de outliers en los datos"""
        
        median_flux = np.median(lc_data.flux)
        mad = np.median(np.abs(lc_data.flux - median_flux))
        
        # Outliers como puntos > 3*MAD
        outliers = np.abs(lc_data.flux - median_flux) > 3 * 1.4826 * mad
        
        return np.sum(outliers) / len(lc_data.flux)
    
    def _calculate_ls_significance(self, powers: np.ndarray, best_power: float) -> float:
        """Calcula significancia de Lomb-Scargle"""
        
        # Significancia basada en distribución de powers
        mean_power = np.mean(powers)
        std_power = np.std(powers)
        
        if std_power > 0:
            significance = (best_power - mean_power) / std_power
        else:
            significance = 1.0
        
        return significance
    
    def _classify_periodicity(
        self,
        period: float,
        power: float,
        significance: float
    ) -> Tuple[str, float]:
        """Clasifica tipo de periodicidad"""
        
        if significance < 3.0:
            return "Non-periodic", 0.2
        elif 0.1 <= period <= 1.0:
            return "Short-period variable", 0.8
        elif 1.0 <= period <= 100.0:
            return "Long-period variable", 0.7
        else:
            return "Ultra-long period", 0.5


# Instancia global del servicio
astronomy_light_curve_service = AstronomyLightCurveService()
