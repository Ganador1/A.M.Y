"""
Servicio de Validación Estadística Rigurosa para AXIOM
======================================================

Implementa herramientas avanzadas de validación estadística para garantizar
el rigor científico de hipótesis y resultados experimentales en AXIOM.

Características:
- Power analysis para determinar tamaños de muestra adecuados
- Corrección por múltiples comparaciones (Bonferroni, FDR, Holm)
- Análisis bayesiano con PyMC
- Bootstrap confidence intervals
- Effect size calculation
- Validación de supuestos estadísticos

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from app.exceptions.domain.biology import BiologyError

# Importaciones con manejo de errores
try:
    import scipy.stats as stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    stats = None

try:
    from statsmodels.stats.power import TTestPower
    from statsmodels.stats.multitest import multipletests
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    TTestPower = None
    multipletests = None

try:
    import pymc as pm
    import arviz as az
    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False
    pm = None
    az = None

try:
    import pingouin as pg
    PINGOUIN_AVAILABLE = True
except ImportError:
    PINGOUIN_AVAILABLE = False
    pg = None

from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


@dataclass
class ValidationConfig:
    """Configuración para validación estadística"""
    confidence_level: float = 0.95
    alpha: float = 0.05
    power: float = 0.8
    effect_size: Optional[float] = None
    multiple_comparisons_method: str = "bonferroni"  # bonferroni, fdr_bh, holm
    bootstrap_iterations: int = 1000
    bayesian_samples: int = 2000


@dataclass
class ValidationReport:
    """Reporte de validación estadística"""
    is_valid: bool
    power_analysis: Dict[str, Any]
    multiple_testing: Dict[str, Any]
    bayesian_analysis: Dict[str, Any]
    bootstrap_ci: Dict[str, Any]
    effect_sizes: Dict[str, Any]
    assumptions_check: Dict[str, Any]
    recommendations: List[str]


class StatisticalValidationService(BaseService):
    """
    Servicio de validación estadística rigurosa para hipótesis científicas
    """

    def __init__(self):
        super().__init__("StatisticalValidationService")
        self.logger = logging.getLogger(__name__)

    async def validate_hypothesis_rigorously(
        self,
        data: np.ndarray,
        hypothesis_type: str = "one_sample_ttest",
        config: Optional[ValidationConfig] = None,
        **kwargs
    ) -> ValidationReport:
        """
        Validación multi-nivel de hipótesis científicas

        Args:
            data: Datos experimentales
            hypothesis_type: Tipo de prueba estadística
            config: Configuración de validación
            **kwargs: Parámetros adicionales específicos de la prueba

        Returns:
            Reporte completo de validación estadística
        """
        if config is None:
            config = ValidationConfig()

        validations = {}
        recommendations = []

        try:
            # 1. POWER ANALYSIS
            self.logger.info("Realizando power analysis...")
            power_analysis = await self._power_analysis(data, hypothesis_type, config, **kwargs)
            validations['power_analysis'] = power_analysis

            if power_analysis.get('achieved_power', 0) < config.power:
                recommendations.append(
                    f"Aumentar tamaño de muestra. Power actual: {power_analysis.get('achieved_power', 0):.3f}, "
                    f"requerido: {config.power}"
                )

            # 2. MULTIPLE TESTING CORRECTION
            if 'p_values' in kwargs and len(kwargs['p_values']) > 1:
                self.logger.info("Aplicando corrección por múltiples comparaciones...")
                multiple_testing = await self._multiple_testing_correction(
                    kwargs['p_values'], config.multiple_comparisons_method
                )
                validations['multiple_testing'] = multiple_testing
            else:
                validations['multiple_testing'] = {"applied": False, "reason": "Una sola comparación"}

            # 3. BAYESIAN ANALYSIS
            if PYMC_AVAILABLE and len(data) >= 10:
                self.logger.info("Realizando análisis bayesiano...")
                bayesian_analysis = await self._bayesian_analysis(data, config)
                validations['bayesian_analysis'] = bayesian_analysis
            else:
                validations['bayesian_analysis'] = {
                    "applied": False, 
                    "reason": "PyMC no disponible o datos insuficientes"
                }

            # 4. BOOTSTRAP CONFIDENCE INTERVALS
            if len(data) >= 10:
                self.logger.info("Calculando intervalos de confianza bootstrap...")
                bootstrap_ci = await self._bootstrap_confidence_intervals(data, config)
                validations['bootstrap_ci'] = bootstrap_ci
            else:
                validations['bootstrap_ci'] = {"applied": False, "reason": "Datos insuficientes"}

            # 5. EFFECT SIZE CALCULATION
            self.logger.info("Calculando tamaños de efecto...")
            effect_sizes = await self._calculate_effect_sizes(data, hypothesis_type, **kwargs)
            validations['effect_sizes'] = effect_sizes

            # 6. ASSUMPTIONS TESTING
            self.logger.info("Verificando supuestos estadísticos...")
            assumptions = await self._test_assumptions(data, hypothesis_type)
            validations['assumptions_check'] = assumptions

            for assumption, result in assumptions.items():
                if not result.get('passed', True):
                    recommendations.append(f"Supuesto violado: {assumption}. {result.get('recommendation', '')}")

            # EVALUACIÓN FINAL
            is_valid = self._evaluate_overall_validity(validations, config)

            return ValidationReport(
                is_valid=is_valid,
                power_analysis=validations.get('power_analysis', {}),
                multiple_testing=validations.get('multiple_testing', {}),
                bayesian_analysis=validations.get('bayesian_analysis', {}),
                bootstrap_ci=validations.get('bootstrap_ci', {}),
                effect_sizes=validations.get('effect_sizes', {}),
                assumptions_check=validations.get('assumptions_check', {}),
                recommendations=recommendations
            )

        except BiologyError as e:
            self.logger.error(f"Error en validación estadística: {str(e)}")
            return ValidationReport(
                is_valid=False,
                power_analysis={},
                multiple_testing={},
                bayesian_analysis={},
                bootstrap_ci={},
                effect_sizes={},
                assumptions_check={},
                recommendations=[f"Error en validación: {str(e)}"]
            )

    async def _power_analysis(
        self, 
        data: np.ndarray, 
        hypothesis_type: str, 
        config: ValidationConfig,
        **kwargs
    ) -> Dict[str, Any]:
        """Análisis de poder estadístico"""
        if not STATSMODELS_AVAILABLE:
            return {"error": "statsmodels no disponible"}

        try:
            power_calc = TTestPower()
            n_obs = len(data)

            # Estimar effect size si no se proporciona
            if config.effect_size is None:
                if hypothesis_type == "one_sample_ttest":
                    mu = kwargs.get("mu", 0)
                    effect_size = (np.mean(data) - mu) / np.std(data, ddof=1)
                else:
                    effect_size = 0.5  # Efecto mediano por defecto

            else:
                effect_size = config.effect_size

            # Calcular poder actual
            achieved_power = power_calc.solve_power(
                effect_size=abs(effect_size),
                nobs=n_obs,
                alpha=config.alpha
            )

            # Calcular tamaño de muestra requerido
            required_n = power_calc.solve_power(
                effect_size=abs(effect_size),
                power=config.power,
                alpha=config.alpha
            )

            return {
                "effect_size": float(effect_size),
                "achieved_power": float(achieved_power),
                "required_sample_size": int(np.ceil(required_n)),
                "current_sample_size": n_obs,
                "power_adequate": achieved_power >= config.power,
                "alpha": config.alpha
            }

        except BiologyError as e:
            return {"error": f"Error en power analysis: {str(e)}"}

    async def _multiple_testing_correction(
        self, 
        p_values: List[float], 
        method: str
    ) -> Dict[str, Any]:
        """Corrección por múltiples comparaciones"""
        if not STATSMODELS_AVAILABLE:
            return {"error": "statsmodels no disponible"}

        try:
            p_values_array = np.array(p_values)
            
            corrected = multipletests(
                p_values_array,
                alpha=0.05,
                method=method
            )

            return {
                "method": method,
                "original_p_values": p_values,
                "corrected_p_values": corrected[1].tolist(),
                "rejected_hypotheses": corrected[0].tolist(),
                "alpha_corrected": float(corrected[3]) if len(corrected) > 3 else 0.05,
                "significant_after_correction": int(np.sum(corrected[0]))
            }

        except BiologyError as e:
            return {"error": f"Error en corrección múltiple: {str(e)}"}

    async def _bayesian_analysis(
        self, 
        data: np.ndarray, 
        config: ValidationConfig
    ) -> Dict[str, Any]:
        """Análisis bayesiano básico"""
        if not PYMC_AVAILABLE:
            return {"error": "PyMC no disponible"}

        try:
            with pm.Model() as model:
                # Prior para la media
                mu = pm.Normal('mu', mu=0, sigma=10)
                
                # Prior para la desviación estándar
                sigma = pm.HalfNormal('sigma', sigma=1)
                
                # Likelihood
                obs = pm.Normal('obs', mu=mu, sigma=sigma, observed=data)
                
                # Sampling
                trace = pm.sample(
                    config.bayesian_samples, 
                    return_inferencedata=True,
                    progressbar=False
                )

            # Calcular HDI (Highest Density Interval)
            hdi = az.hdi(trace, hdi_prob=config.confidence_level)
            
            # Posterior statistics
            posterior_mu = trace.posterior['mu'].values.flatten()
            posterior_sigma = trace.posterior['sigma'].values.flatten()

            return {
                "posterior_mean_mu": float(np.mean(posterior_mu)),
                "posterior_std_mu": float(np.std(posterior_mu)),
                "posterior_mean_sigma": float(np.mean(posterior_sigma)),
                "hdi_mu": [float(hdi['mu'].values[0]), float(hdi['mu'].values[1])],
                "hdi_sigma": [float(hdi['sigma'].values[0]), float(hdi['sigma'].values[1])],
                "effective_sample_size": int(az.ess(trace)['mu'].values),
                "rhat": float(az.rhat(trace)['mu'].values)
            }

        except BiologyError as e:
            return {"error": f"Error en análisis bayesiano: {str(e)}"}

    async def _bootstrap_confidence_intervals(
        self, 
        data: np.ndarray, 
        config: ValidationConfig
    ) -> Dict[str, Any]:
        """Intervalos de confianza bootstrap"""
        if not SCIPY_AVAILABLE:
            return {"error": "scipy no disponible"}

        try:
            # Bootstrap para la media
            bootstrap_means = []
            n = len(data)
            
            for _ in range(config.bootstrap_iterations):
                sample = np.random.choice(data, size=n, replace=True)
                bootstrap_means.append(np.mean(sample))
            
            bootstrap_means = np.array(bootstrap_means)
            
            # Calcular percentiles para intervalo de confianza
            alpha = 1 - config.confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            ci_lower = np.percentile(bootstrap_means, lower_percentile)
            ci_upper = np.percentile(bootstrap_means, upper_percentile)

            return {
                "confidence_level": config.confidence_level,
                "confidence_interval": [float(ci_lower), float(ci_upper)],
                "bootstrap_mean": float(np.mean(bootstrap_means)),
                "bootstrap_std": float(np.std(bootstrap_means)),
                "iterations": config.bootstrap_iterations
            }

        except BiologyError as e:
            return {"error": f"Error en bootstrap: {str(e)}"}

    async def _calculate_effect_sizes(
        self, 
        data: np.ndarray, 
        hypothesis_type: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Cálculo de tamaños de efecto"""
        try:
            effect_sizes = {}

            if hypothesis_type == "one_sample_ttest":
                mu = kwargs.get("mu", 0)
                # Cohen's d para una muestra
                cohens_d = (np.mean(data) - mu) / np.std(data, ddof=1)
                effect_sizes["cohens_d"] = float(cohens_d)
                
                # Interpretación
                abs_d = abs(cohens_d)
                if abs_d < 0.2:
                    interpretation = "Efecto trivial"
                elif abs_d < 0.5:
                    interpretation = "Efecto pequeño"
                elif abs_d < 0.8:
                    interpretation = "Efecto mediano"
                else:
                    interpretation = "Efecto grande"
                
                effect_sizes["interpretation"] = interpretation

            elif hypothesis_type == "two_sample_ttest" and "data2" in kwargs:
                data2 = np.array(kwargs["data2"])
                
                # Cohen's d para dos muestras
                pooled_std = np.sqrt(
                    ((len(data) - 1) * np.var(data, ddof=1) + 
                     (len(data2) - 1) * np.var(data2, ddof=1)) /
                    (len(data) + len(data2) - 2)
                )
                
                cohens_d = (np.mean(data) - np.mean(data2)) / pooled_std
                effect_sizes["cohens_d"] = float(cohens_d)
                
                # Glass's delta
                glass_delta = (np.mean(data) - np.mean(data2)) / np.std(data2, ddof=1)
                effect_sizes["glass_delta"] = float(glass_delta)

            # Calcular r² si se puede
            if PINGOUIN_AVAILABLE and hypothesis_type in ["one_sample_ttest", "two_sample_ttest"]:
                try:
                    r_squared = cohens_d ** 2 / (cohens_d ** 2 + 4)
                    effect_sizes["r_squared"] = float(r_squared)
                except BiologyError as e:
                    logger.debug(f"Failed to compute r_squared from Cohen's d: {e}")

            return effect_sizes

        except BiologyError as e:
            return {"error": f"Error calculando effect sizes: {str(e)}"}

    async def _test_assumptions(
        self, 
        data: np.ndarray, 
        hypothesis_type: str
    ) -> Dict[str, Any]:
        """Pruebas de supuestos estadísticos"""
        if not SCIPY_AVAILABLE:
            return {"error": "scipy no disponible"}

        assumptions = {}

        try:
            # Test de normalidad (Shapiro-Wilk)
            if len(data) >= 3 and len(data) <= 5000:
                shapiro_stat, shapiro_p = stats.shapiro(data)
                assumptions["normality"] = {
                    "test": "Shapiro-Wilk",
                    "statistic": float(shapiro_stat),
                    "p_value": float(shapiro_p),
                    "passed": shapiro_p > 0.05,
                    "recommendation": "Usar pruebas no paramétricas" if shapiro_p <= 0.05 else "OK"
                }

            # Test de outliers (IQR method)
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = np.sum((data < lower_bound) | (data > upper_bound))
            outlier_percentage = (outliers / len(data)) * 100
            
            assumptions["outliers"] = {
                "count": int(outliers),
                "percentage": float(outlier_percentage),
                "passed": outlier_percentage < 5,  # Menos del 5% de outliers
                "recommendation": "Investigar outliers" if outlier_percentage >= 5 else "OK"
            }

            # Verificar tamaño de muestra mínimo
            min_sample_sizes = {
                "one_sample_ttest": 20,
                "two_sample_ttest": 30,
                "anova": 30
            }
            
            min_required = min_sample_sizes.get(hypothesis_type, 20)
            assumptions["sample_size"] = {
                "current": len(data),
                "minimum_recommended": min_required,
                "passed": len(data) >= min_required,
                "recommendation": f"Aumentar a {min_required} observaciones" if len(data) < min_required else "OK"
            }

            return assumptions

        except BiologyError as e:
            return {"error": f"Error verificando supuestos: {str(e)}"}

    def _evaluate_overall_validity(
        self, 
        validations: Dict[str, Any], 
        config: ValidationConfig
    ) -> bool:
        """Evaluación general de validez"""
        validity_checks = []

        # Check power analysis
        power_analysis = validations.get('power_analysis', {})
        if 'achieved_power' in power_analysis:
            validity_checks.append(power_analysis['achieved_power'] >= config.power)

        # Check assumptions
        assumptions = validations.get('assumptions_check', {})
        for assumption, result in assumptions.items():
            if isinstance(result, dict) and 'passed' in result:
                validity_checks.append(result['passed'])

        # Check multiple testing if applied
        multiple_testing = validations.get('multiple_testing', {})
        if multiple_testing.get('applied', True):  # Si se aplicó corrección
            validity_checks.append(
                multiple_testing.get('significant_after_correction', 0) > 0
            )

        # Al menos 70% de las verificaciones deben pasar
        if validity_checks:
            validity_rate = sum(validity_checks) / len(validity_checks)
            return validity_rate >= 0.7
        
        return False  # Por defecto, no válido si no se pueden hacer verificaciones
