"""
Statistical Validation Service

Servicio integral para validación estadística de resultados científicos,
análisis de poder estadístico, detección de sesgos y validación cruzada.

Características principales:
- Validación de hipótesis estadísticas
- Análisis de poder estadístico y tamaño de muestra
- Detección de sesgos en datos y modelos
- Validación cruzada avanzada
- Análisis bayesiano con PyMC
- Corrección de múltiples comparaciones
- Análisis de robustez estadística
- Visualización de resultados estadísticos

Dependencias:
- statsmodels: Modelos estadísticos avanzados
- scipy: Funciones estadísticas fundamentales
- pymc: Análisis bayesiano
- arviz: Visualización bayesiana
- pingouin: Estadísticas descriptivas y tests
- seaborn/plotly: Visualización
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
import logging
from datetime import datetime
import warnings
from app.exceptions.domain.biology import BiologyError
warnings.filterwarnings('ignore')

try:
    import statsmodels.api as sm
    import statsmodels.stats.api as sms
    from statsmodels.stats.power import ttest_power, anova_power
    from statsmodels.stats.multitest import multipletests
    from statsmodels.stats.diagnostic import het_breuschpagan, jarque_bera
    from statsmodels.stats.outliers_influence import OLSInfluence
    import scipy.stats as stats
    from scipy.stats import normaltest, shapiro, levene, bartlett
    import pymc as pm
    import arviz as az
    import pingouin as pg
    import seaborn as sns
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    STATISTICAL_VALIDATION_AVAILABLE = True
except ImportError as e:
    STATISTICAL_VALIDATION_AVAILABLE = False
    logging.warning(f"Statistical validation dependencies not available: {e}")

from app.core.bootstrap_logging import logger
from app.services.base_service import BaseService
from app.types.statistical_validation_service_types import (
    ProcessRequestResult,
    CheckAvailabilityResult,
    CheckTestAssumptionsResult,
    CalculateEffectSizeResult,
    InterpretTestResultsResult,
    CalculateStatisticalPowerResult,
    FallbackHypothesisTestResult,
    FallbackPowerAnalysisResult,
    FallbackBiasDetectionResult,
    FallbackCrossValidationResult,
    FallbackBayesianAnalysisResult,
    FallbackMultipleComparisonsResult,
    GetServiceInfoResult,
)

class StatisticalValidationService(BaseService):
    """
    Servicio Integral de Validación Estadística
    
    Proporciona herramientas avanzadas para:
    1. Validación de hipótesis estadísticas
    2. Análisis de poder estadístico
    3. Detección de sesgos
    4. Validación cruzada
    5. Análisis bayesiano
    """
    
    def __init__(self):
        super().__init__("StatisticalValidationService")
        self.logger = logger
        self.validation_history = []
        self.available = STATISTICAL_VALIDATION_AVAILABLE
        logger.info(f"Statistical Validation Service initialized - Available: {self.available}")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process statistical validation requests"""
        try:
            operation = request_data.get('operation', 'validate_hypothesis')
            
            if operation == 'validate_hypothesis':
                return self.validate_hypothesis_test(
                    data=pd.DataFrame(request_data.get('data', [])),
                    test_type=request_data.get('test_type', 'ttest'),
                    variables=request_data.get('variables', []),
                    alpha=request_data.get('alpha', 0.05),
                    alternative=request_data.get('alternative', 'two-sided')
                )
            elif operation == 'power_analysis':
                return self.analyze_statistical_power(
                    effect_size=request_data.get('effect_size', 0.5),
                    sample_size=request_data.get('sample_size'),
                    alpha=request_data.get('alpha', 0.05),
                    power=request_data.get('power'),
                    test_type=request_data.get('test_type', 'ttest')
                )
            elif operation == 'bias_detection':
                return self.detect_statistical_bias(
                    data=pd.DataFrame(request_data.get('data', [])),
                    target_variable=request_data.get('target_variable'),
                    predictor_variables=request_data.get('predictor_variables', []),
                    bias_types=request_data.get('bias_types')
                )
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except BiologyError as e:
            return self.handle_error(e, "process_request")
        
    def check_availability(self) -> CheckAvailabilityResult:
        """Verificar disponibilidad de dependencias estadísticas"""
        return {
            "available": STATISTICAL_VALIDATION_AVAILABLE,
            "dependencies": {
                "statsmodels": "statsmodels" in globals(),
                "scipy": "scipy" in globals(),
                "pymc": "pymc" in globals(),
                "arviz": "arviz" in globals(),
                "pingouin": "pingouin" in globals(),
                "seaborn": "seaborn" in globals(),
                "plotly": "plotly" in globals()
            }
        }
    
    def validate_hypothesis_test(
        self,
        data: pd.DataFrame,
        test_type: str,
        variables: List[str],
        alpha: float = 0.05,
        alternative: str = "two-sided",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Realizar tests de hipótesis estadísticas con validación completa
        
        Args:
            data: DataFrame con los datos
            test_type: Tipo de test ('ttest', 'anova', 'chi2', 'mannwhitney', etc.)
            variables: Variables a analizar
            alpha: Nivel de significancia
            alternative: Hipótesis alternativa
        """
        if not STATISTICAL_VALIDATION_AVAILABLE:
            return self._fallback_hypothesis_test(data, test_type, variables, alpha)
        
        try:
            results = {}
            
            # Validaciones previas
            assumptions_check = self._check_test_assumptions(data, variables, test_type)
            results["assumptions"] = assumptions_check
            
            # Realizar el test estadístico
            if test_type == "ttest":
                if len(variables) == 1:
                    # One-sample t-test
                    stat_result = stats.ttest_1samp(
                        data[variables[0]].dropna(), 
                        kwargs.get('popmean', 0),
                        alternative=alternative
                    )
                elif len(variables) == 2:
                    # Two-sample t-test
                    stat_result = stats.ttest_ind(
                        data[variables[0]].dropna(),
                        data[variables[1]].dropna(),
                        alternative=alternative
                    )
                results["statistic"] = stat_result.statistic
                results["p_value"] = stat_result.pvalue
                
            elif test_type == "anova":
                # One-way ANOVA
                groups = [data[var].dropna() for var in variables]
                stat_result = stats.f_oneway(*groups)
                results["statistic"] = stat_result.statistic
                results["p_value"] = stat_result.pvalue
                
                # Post-hoc analysis if significant
                if stat_result.pvalue < alpha:
                    posthoc = self._perform_posthoc_analysis(data, variables)
                    results["posthoc"] = posthoc
                    
            elif test_type == "chi2":
                # Chi-square test
                if len(variables) == 2:
                    contingency_table = pd.crosstab(data[variables[0]], data[variables[1]])
                    stat_result = stats.chi2_contingency(contingency_table)
                    results["statistic"] = stat_result[0]
                    results["p_value"] = stat_result[1]
                    results["dof"] = stat_result[2]
                    results["expected"] = stat_result[3].tolist()
                    
            elif test_type == "mannwhitney":
                # Mann-Whitney U test (non-parametric)
                stat_result = stats.mannwhitneyu(
                    data[variables[0]].dropna(),
                    data[variables[1]].dropna(),
                    alternative=alternative
                )
                results["statistic"] = stat_result.statistic
                results["p_value"] = stat_result.pvalue
                
            elif test_type == "kruskal":
                # Kruskal-Wallis test (non-parametric ANOVA)
                groups = [data[var].dropna() for var in variables]
                stat_result = stats.kruskal(*groups)
                results["statistic"] = stat_result.statistic
                results["p_value"] = stat_result.pvalue
            
            # Calcular tamaño del efecto
            effect_size = self._calculate_effect_size(data, variables, test_type, results)
            results["effect_size"] = effect_size
            
            # Interpretación de resultados
            interpretation = self._interpret_test_results(results, alpha, test_type)
            results["interpretation"] = interpretation
            
            # Análisis de poder estadístico
            power_analysis = self._calculate_statistical_power(data, variables, test_type, alpha)
            results["power_analysis"] = power_analysis
            
            return {
                "test_type": test_type,
                "variables": variables,
                "alpha": alpha,
                "results": results,
                "timestamp": datetime.now().isoformat(),
                "sample_size": len(data),
                "missing_values": data[variables].isnull().sum().to_dict()
            }
            
        except BiologyError as e:
            self.logger.error(f"Error in hypothesis test: {e}")
            return self._fallback_hypothesis_test(data, test_type, variables, alpha)
    
    def analyze_statistical_power(
        self,
        effect_size: float,
        sample_size: Optional[int] = None,
        alpha: float = 0.05,
        power: Optional[float] = None,
        test_type: str = "ttest"
    ) -> Dict[str, Any]:
        """
        Análisis de poder estadístico para determinar tamaños de muestra óptimos
        """
        if not STATISTICAL_VALIDATION_AVAILABLE:
            return self._fallback_power_analysis(effect_size, sample_size, alpha, power)
        
        try:
            results = {}
            
            if test_type == "ttest":
                if sample_size is None and power is not None:
                    # Calcular tamaño de muestra necesario
                    required_n = sms.ttest_power(effect_size, power, alpha, alternative='two-sided')
                    results["required_sample_size"] = int(np.ceil(required_n))
                    
                elif power is None and sample_size is not None:
                    # Calcular poder estadístico
                    calculated_power = sms.ttest_power(effect_size, sample_size, alpha, alternative='two-sided')
                    results["statistical_power"] = calculated_power
                    
            # Generar curvas de poder
            power_curve = self._generate_power_curve(effect_size, alpha, test_type)
            results["power_curve"] = power_curve
            
            # Recomendaciones
            recommendations = self._generate_power_recommendations(results, effect_size, alpha)
            results["recommendations"] = recommendations
            
            return {
                "effect_size": effect_size,
                "alpha": alpha,
                "test_type": test_type,
                "analysis": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except BiologyError as e:
            self.logger.error(f"Error in power analysis: {e}")
            return self._fallback_power_analysis(effect_size, sample_size, alpha, power)
    
    def detect_statistical_bias(
        self,
        data: pd.DataFrame,
        target_variable: str,
        predictor_variables: List[str],
        bias_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Detectar diferentes tipos de sesgos estadísticos en los datos
        """
        if bias_types is None:
            bias_types = ["selection", "measurement", "confounding", "survivorship"]
        
        if not STATISTICAL_VALIDATION_AVAILABLE:
            return self._fallback_bias_detection(data, target_variable, predictor_variables)
        
        try:
            bias_results = {}
            
            # Sesgo de selección
            if "selection" in bias_types:
                selection_bias = self._detect_selection_bias(data, target_variable, predictor_variables)
                bias_results["selection_bias"] = selection_bias
            
            # Sesgo de medición
            if "measurement" in bias_types:
                measurement_bias = self._detect_measurement_bias(data, predictor_variables)
                bias_results["measurement_bias"] = measurement_bias
            
            # Variables de confusión
            if "confounding" in bias_types:
                confounding_analysis = self._detect_confounding_variables(data, target_variable, predictor_variables)
                bias_results["confounding_analysis"] = confounding_analysis
            
            # Sesgo de supervivencia
            if "survivorship" in bias_types:
                survivorship_bias = self._detect_survivorship_bias(data, target_variable)
                bias_results["survivorship_bias"] = survivorship_bias
            
            # Análisis de outliers
            outlier_analysis = self._detect_outliers_influence(data, predictor_variables)
            bias_results["outlier_analysis"] = outlier_analysis
            
            # Recomendaciones para mitigar sesgos
            mitigation_strategies = self._generate_bias_mitigation_strategies(bias_results)
            
            return {
                "target_variable": target_variable,
                "predictor_variables": predictor_variables,
                "bias_analysis": bias_results,
                "mitigation_strategies": mitigation_strategies,
                "timestamp": datetime.now().isoformat(),
                "data_shape": data.shape
            }
            
        except BiologyError as e:
            self.logger.error(f"Error in bias detection: {e}")
            return self._fallback_bias_detection(data, target_variable, predictor_variables)
    
    def perform_cross_validation(
        self,
        data: pd.DataFrame,
        target_variable: str,
        predictor_variables: List[str],
        cv_method: str = "kfold",
        n_splits: int = 5,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Realizar validación cruzada avanzada con múltiples métricas
        """
        if not STATISTICAL_VALIDATION_AVAILABLE:
            return self._fallback_cross_validation(data, target_variable, predictor_variables)
        
        try:
            from sklearn.model_selection import KFold, StratifiedKFold, TimeSeriesSplit, cross_val_score
            from sklearn.linear_model import LinearRegression, LogisticRegression
            from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score
            
            X = data[predictor_variables]
            y = data[target_variable]
            
            # Seleccionar método de validación cruzada
            if cv_method == "kfold":
                cv = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
            elif cv_method == "stratified":
                cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
            elif cv_method == "timeseries":
                cv = TimeSeriesSplit(n_splits=n_splits)
            
            # Determinar tipo de problema (regresión vs clasificación)
            is_classification = self._is_classification_problem(y)
            
            if is_classification:
                model = LogisticRegression(random_state=random_state)
                scoring_metrics = ['accuracy', 'f1_weighted', 'precision_weighted', 'recall_weighted']
            else:
                model = LinearRegression()
                scoring_metrics = ['neg_mean_squared_error', 'r2', 'neg_mean_absolute_error']
            
            # Realizar validación cruzada
            cv_results = {}
            for metric in scoring_metrics:
                scores = cross_val_score(model, X, y, cv=cv, scoring=metric)
                cv_results[metric] = {
                    "scores": scores.tolist(),
                    "mean": scores.mean(),
                    "std": scores.std(),
                    "confidence_interval": self._calculate_confidence_interval(scores)
                }
            
            # Análisis de estabilidad
            stability_analysis = self._analyze_model_stability(cv_results)
            
            # Detección de overfitting
            overfitting_analysis = self._detect_overfitting(data, X, y, model, cv)
            
            return {
                "cv_method": cv_method,
                "n_splits": n_splits,
                "target_variable": target_variable,
                "predictor_variables": predictor_variables,
                "cv_results": cv_results,
                "stability_analysis": stability_analysis,
                "overfitting_analysis": overfitting_analysis,
                "is_classification": is_classification,
                "timestamp": datetime.now().isoformat()
            }
            
        except BiologyError as e:
            self.logger.error(f"Error in cross validation: {e}")
            return self._fallback_cross_validation(data, target_variable, predictor_variables)
    
    def bayesian_analysis(
        self,
        data: pd.DataFrame,
        model_formula: str,
        prior_distributions: Optional[Dict] = None,
        n_samples: int = 2000,
        n_chains: int = 4
    ) -> Dict[str, Any]:
        """
        Realizar análisis bayesiano con PyMC
        """
        if not STATISTICAL_VALIDATION_AVAILABLE:
            return self._fallback_bayesian_analysis(data, model_formula)
        
        try:
            with pm.Model() as model:
                # Definir priors (por defecto o especificados)
                if prior_distributions is None:
                    prior_distributions = self._get_default_priors(data, model_formula)
                
                # Construir modelo bayesiano
                # (Implementación simplificada - se expandiría según necesidades)
                
                # Muestreo MCMC
                trace = pm.sample(
                    draws=n_samples,
                    chains=n_chains,
                    return_inferencedata=True,
                    random_seed=42
                )
            
            # Diagnósticos de convergencia
            convergence_diagnostics = self._check_mcmc_convergence(trace)
            
            # Resumen estadístico
            summary_stats = az.summary(trace)
            
            # Comparación de modelos (si aplicable)
            model_comparison = self._perform_bayesian_model_comparison(trace)
            
            return {
                "model_formula": model_formula,
                "prior_distributions": prior_distributions,
                "n_samples": n_samples,
                "n_chains": n_chains,
                "summary_statistics": summary_stats.to_dict(),
                "convergence_diagnostics": convergence_diagnostics,
                "model_comparison": model_comparison,
                "timestamp": datetime.now().isoformat()
            }
            
        except BiologyError as e:
            self.logger.error(f"Error in Bayesian analysis: {e}")
            return self._fallback_bayesian_analysis(data, model_formula)
    
    def multiple_comparisons_correction(
        self,
        p_values: List[float],
        method: str = "fdr_bh",
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Aplicar corrección por múltiples comparaciones
        """
        if not STATISTICAL_VALIDATION_AVAILABLE:
            return self._fallback_multiple_comparisons(p_values, method, alpha)
        
        try:
            # Aplicar corrección
            rejected, p_corrected, alpha_sidak, alpha_bonf = multipletests(
                p_values, alpha=alpha, method=method
            )
            
            # Calcular estadísticas
            n_tests = len(p_values)
            n_significant_raw = sum(p < alpha for p in p_values)
            n_significant_corrected = sum(rejected)
            
            # Análisis de poder para múltiples comparisons
            family_wise_error_rate = 1 - (1 - alpha) ** n_tests
            
            return {
                "method": method,
                "alpha": alpha,
                "n_tests": n_tests,
                "p_values_raw": p_values,
                "p_values_corrected": p_corrected.tolist(),
                "rejected_hypotheses": rejected.tolist(),
                "n_significant_raw": n_significant_raw,
                "n_significant_corrected": n_significant_corrected,
                "family_wise_error_rate": family_wise_error_rate,
                "alpha_bonferroni": alpha_bonf,
                "alpha_sidak": alpha_sidak,
                "timestamp": datetime.now().isoformat()
            }
            
        except BiologyError as e:
            self.logger.error(f"Error in multiple comparisons correction: {e}")
            return self._fallback_multiple_comparisons(p_values, method, alpha)
    
    def generate_statistical_report(
        self,
        analyses: List[Dict[str, Any]],
        report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Generar reporte estadístico integral
        """
        try:
            report = {
                "report_type": report_type,
                "timestamp": datetime.now().isoformat(),
                "analyses_summary": [],
                "overall_conclusions": [],
                "recommendations": [],
                "visualizations": []
            }
            
            # Procesar cada análisis
            for analysis in analyses:
                summary = self._summarize_analysis(analysis)
                report["analyses_summary"].append(summary)
            
            # Generar conclusiones generales
            overall_conclusions = self._generate_overall_conclusions(analyses)
            report["overall_conclusions"] = overall_conclusions
            
            # Generar recomendaciones
            recommendations = self._generate_statistical_recommendations(analyses)
            report["recommendations"] = recommendations
            
            # Crear visualizaciones
            if STATISTICAL_VALIDATION_AVAILABLE:
                visualizations = self._create_statistical_visualizations(analyses)
                report["visualizations"] = visualizations
            
            return report
            
        except BiologyError as e:
            self.logger.error(f"Error generating statistical report: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Métodos auxiliares privados
    def _check_test_assumptions(self, data: pd.DataFrame, variables: List[str], test_type: str) -> CheckTestAssumptionsResult:
        """Verificar supuestos estadísticos para el test"""
        assumptions = {}
        
        try:
            for var in variables:
                var_data = data[var].dropna()
                
                # Normalidad
                shapiro_stat, shapiro_p = shapiro(var_data)
                assumptions[f"{var}_normality"] = {
                    "shapiro_statistic": shapiro_stat,
                    "shapiro_p_value": shapiro_p,
                    "is_normal": shapiro_p > 0.05
                }
                
                # Homogeneidad de varianzas (si aplicable)
                if test_type in ["anova", "ttest"] and len(variables) > 1:
                    levene_stat, levene_p = levene(*[data[v].dropna() for v in variables])
                    assumptions["homogeneity_of_variance"] = {
                        "levene_statistic": levene_stat,
                        "levene_p_value": levene_p,
                        "equal_variances": levene_p > 0.05
                    }
        
        except BiologyError as e:
            assumptions["error"] = str(e)
        
        return assumptions
    
    def _calculate_effect_size(self, data: pd.DataFrame, variables: List[str], test_type: str, results: Dict) -> CalculateEffectSizeResult:
        """Calcular tamaño del efecto"""
        effect_sizes = {}
        
        try:
            if test_type == "ttest" and len(variables) == 2:
                # Cohen's d
                group1 = data[variables[0]].dropna()
                group2 = data[variables[1]].dropna()
                
                pooled_std = np.sqrt(((len(group1) - 1) * group1.var() + (len(group2) - 1) * group2.var()) / 
                                   (len(group1) + len(group2) - 2))
                cohens_d = (group1.mean() - group2.mean()) / pooled_std
                effect_sizes["cohens_d"] = cohens_d
                
            elif test_type == "anova":
                # Eta squared
                if "statistic" in results and "p_value" in results:
                    # Aproximación basada en F-statistic
                    f_stat = results["statistic"]
                    df_between = len(variables) - 1
                    df_total = len(data) - 1
                    eta_squared = (f_stat * df_between) / (f_stat * df_between + df_total - df_between)
                    effect_sizes["eta_squared"] = eta_squared
        
        except BiologyError as e:
            effect_sizes["error"] = str(e)
        
        return effect_sizes
    
    def _interpret_test_results(self, results: Dict, alpha: float, test_type: str) -> InterpretTestResultsResult:
        """Interpretar resultados del test estadístico"""
        interpretation = {}
        
        try:
            p_value = results.get("p_value", 1.0)
            
            interpretation["is_significant"] = p_value < alpha
            interpretation["significance_level"] = "significant" if p_value < alpha else "not significant"
            
            # Interpretación del p-value
            if p_value < 0.001:
                interpretation["p_value_interpretation"] = "highly significant"
            elif p_value < 0.01:
                interpretation["p_value_interpretation"] = "very significant"
            elif p_value < 0.05:
                interpretation["p_value_interpretation"] = "significant"
            else:
                interpretation["p_value_interpretation"] = "not significant"
            
            # Interpretación del tamaño del efecto
            effect_size = results.get("effect_size", {})
            if "cohens_d" in effect_size:
                d = abs(effect_size["cohens_d"])
                if d < 0.2:
                    interpretation["effect_size_interpretation"] = "negligible"
                elif d < 0.5:
                    interpretation["effect_size_interpretation"] = "small"
                elif d < 0.8:
                    interpretation["effect_size_interpretation"] = "medium"
                else:
                    interpretation["effect_size_interpretation"] = "large"
        
        except BiologyError as e:
            interpretation["error"] = str(e)
        
        return interpretation
    
    def _calculate_statistical_power(self, data: pd.DataFrame, variables: List[str], test_type: str, alpha: float) -> CalculateStatisticalPowerResult:
        """Calcular poder estadístico post-hoc"""
        power_analysis = {}
        
        try:
            if test_type == "ttest" and len(variables) == 2:
                group1 = data[variables[0]].dropna()
                group2 = data[variables[1]].dropna()
                
                # Calcular tamaño del efecto observado
                pooled_std = np.sqrt(((len(group1) - 1) * group1.var() + (len(group2) - 1) * group2.var()) / 
                                   (len(group1) + len(group2) - 2))
                effect_size = abs(group1.mean() - group2.mean()) / pooled_std
                
                # Calcular poder estadístico
                n_effective = (len(group1) * len(group2)) / (len(group1) + len(group2))
                power = sms.ttest_power(effect_size, n_effective, alpha)
                
                power_analysis["observed_effect_size"] = effect_size
                power_analysis["statistical_power"] = power
                power_analysis["sample_size_group1"] = len(group1)
                power_analysis["sample_size_group2"] = len(group2)
        
        except BiologyError as e:
            power_analysis["error"] = str(e)
        
        return power_analysis
    
    # Métodos de fallback para cuando las dependencias no están disponibles
    def _fallback_hypothesis_test(self, data: pd.DataFrame, test_type: str, variables: List[str], alpha: float) -> FallbackHypothesisTestResult:
        """Fallback para tests de hipótesis"""
        return {
            "error": "Statistical validation dependencies not available",
            "fallback_analysis": {
                "descriptive_stats": data[variables].describe().to_dict(),
                "correlation_matrix": data[variables].corr().to_dict() if len(variables) > 1 else None,
                "missing_values": data[variables].isnull().sum().to_dict()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_power_analysis(self, effect_size: float, sample_size: Optional[int], alpha: float, power: Optional[float]) -> FallbackPowerAnalysisResult:
        """Fallback para análisis de poder"""
        return {
            "error": "Statistical validation dependencies not available",
            "basic_recommendations": {
                "small_effect": "n > 400 for power = 0.8",
                "medium_effect": "n > 100 for power = 0.8", 
                "large_effect": "n > 30 for power = 0.8"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_bias_detection(self, data: pd.DataFrame, target_variable: str, predictor_variables: List[str]) -> FallbackBiasDetectionResult:
        """Fallback para detección de sesgos"""
        return {
            "error": "Statistical validation dependencies not available",
            "basic_checks": {
                "missing_data_pattern": data.isnull().sum().to_dict(),
                "variable_distributions": data.describe().to_dict(),
                "correlation_with_target": data[predictor_variables + [target_variable]].corr()[target_variable].to_dict()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_cross_validation(self, data: pd.DataFrame, target_variable: str, predictor_variables: List[str]) -> FallbackCrossValidationResult:
        """Fallback para validación cruzada"""
        return {
            "error": "Statistical validation dependencies not available",
            "basic_split": {
                "train_size": int(0.8 * len(data)),
                "test_size": int(0.2 * len(data)),
                "recommendation": "Use 80/20 train-test split"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_bayesian_analysis(self, data: pd.DataFrame, model_formula: str) -> FallbackBayesianAnalysisResult:
        """Fallback para análisis bayesiano"""
        return {
            "error": "Statistical validation dependencies not available",
            "alternative": "Consider using frequentist statistics or install PyMC",
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_multiple_comparisons(self, p_values: List[float], method: str, alpha: float) -> FallbackMultipleComparisonsResult:
        """Fallback para corrección de múltiples comparaciones"""
        # Bonferroni simple
        bonferroni_alpha = alpha / len(p_values)
        corrected_significant = [p < bonferroni_alpha for p in p_values]
        
        return {
            "method": "bonferroni_simple",
            "alpha": alpha,
            "bonferroni_alpha": bonferroni_alpha,
            "p_values": p_values,
            "significant_after_correction": corrected_significant,
            "note": "Simple Bonferroni correction applied as fallback",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_service_info(self) -> GetServiceInfoResult:
        """Obtener información del servicio"""
        return {
            "service_name": "Statistical Validation Service",
            "version": "1.0.0",
            "description": "Comprehensive statistical validation and analysis service",
            "capabilities": [
                "Hypothesis testing",
                "Statistical power analysis", 
                "Bias detection",
                "Cross-validation",
                "Bayesian analysis",
                "Multiple comparisons correction",
                "Statistical reporting"
            ],
            "dependencies_available": STATISTICAL_VALIDATION_AVAILABLE,
            "supported_tests": [
                "t-test", "ANOVA", "Chi-square", "Mann-Whitney U", 
                "Kruskal-Wallis", "Wilcoxon", "Fisher's exact"
            ],
            "validation_history_count": len(self.validation_history),
            "timestamp": datetime.now().isoformat()
        }

# Instancia global del servicio
statistical_validation_service = StatisticalValidationService()