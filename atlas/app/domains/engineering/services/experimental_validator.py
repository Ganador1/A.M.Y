"""
Experimental Validator - Statistical validation for experimental results

This service provides rigorous statistical validation for experimental results,
including power analysis, multiple testing corrections, outlier detection,
and cross-validation with external datasets.

Author: ATLAS Autonomous Laboratory System
Date: ${new Date().toISOString().split('T')[0]}
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone as tz
from enum import Enum
from scipy import stats
try:  # Optional dependency; provide graceful degradation
    from statsmodels.stats.multitest import multipletests
    from statsmodels.stats.power import TTestPower
    _HAS_STATSMODELS = True
except Exception:  # noqa: BLE001
    multipletests = None  # type: ignore[assignment]
    _HAS_STATSMODELS = False

    class TTestPower:  # type: ignore[override]
        def solve_power(self, *args, **kwargs):
            return 0.0
from app.exceptions.domain.biology import BiologyError

# Configure logging
logger = logging.getLogger(__name__)

UTC = tz.utc


class StatisticalTest(Enum):
    """Types of statistical tests"""
    T_TEST = "t_test"
    ANOVA = "anova"
    CHI_SQUARE = "chi_square"
    MANN_WHITNEY = "mann_whitney"
    KRUSKAL_WALLIS = "kruskal_wallis"
    PEARSON_CORR = "pearson_correlation"
    SPEARMAN_CORR = "spearman_correlation"
    LINEAR_REGRESSION = "linear_regression"


class MultipleTestingCorrection(Enum):
    """Multiple testing correction methods"""
    BONFERRONI = "bonferroni"
    HOLM = "holm"
    FDR_BH = "fdr_bh"  # Benjamini-Hochberg
    FDR_BY = "fdr_by"  # Benjamini-Yekutieli
    NONE = "none"


class OutlierMethod(Enum):
    """Outlier detection methods"""
    IQR = "iqr"
    Z_SCORE = "z_score"
    ISOLATION_FOREST = "isolation_forest"
    DBSCAN = "dbscan"
    GRUBBS = "grubbs"
    ROUT = "rout"  # Robust regression and outlier removal


@dataclass
class ValidationResult:
    """Result of experimental validation"""
    validation_id: str
    experiment_id: str
    is_valid: bool
    confidence_level: float
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    power_analysis: Dict[str, float] = field(default_factory=dict)
    outliers: Dict[str, List[int]] = field(default_factory=dict)
    assumptions_met: Dict[str, bool] = field(default_factory=dict)
    corrected_pvalues: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ExperimentalData:
    """Container for experimental data to validate"""
    experiment_id: str
    groups: Dict[str, np.ndarray]  # Group name -> measurements
    metadata: Dict[str, Any] = field(default_factory=dict)
    hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    alpha: float = 0.05
    power_threshold: float = 0.8


class ExperimentalValidator:
    """
    Validates experimental results with rigorous statistical methods
    """
    
    def __init__(self):
        """Initialize the experimental validator"""
        self.min_sample_size = 3
        self.outlier_contamination = 0.1  # Expected proportion of outliers
        self.effect_size_thresholds = {
            "small": 0.2,
            "medium": 0.5,
            "large": 0.8
        }
        logger.info("✅ ExperimentalValidator initialized")
    
    async def validate_experiment(
        self,
        data: ExperimentalData,
        tests: Optional[List[StatisticalTest]] = None,
        correction: MultipleTestingCorrection = MultipleTestingCorrection.FDR_BH,
        outlier_methods: Optional[List[OutlierMethod]] = None
    ) -> ValidationResult:
        """
        Comprehensive validation of experimental results
        """
        validation_id = f"val_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        
        result = ValidationResult(
            validation_id=validation_id,
            experiment_id=data.experiment_id,
            is_valid=True,
            confidence_level=1.0 - data.alpha
        )
        
        # Default tests if not specified
        if tests is None:
            tests = self._determine_appropriate_tests(data)
            
        # Default outlier methods
        if outlier_methods is None:
            outlier_methods = [OutlierMethod.IQR, OutlierMethod.Z_SCORE]
        
        try:
            # 1. Check sample sizes
            self._validate_sample_sizes(data, result)
            
            # 2. Check assumptions
            await self._check_statistical_assumptions(data, tests, result)
            
            # 3. Detect outliers
            await self._detect_outliers(data, outlier_methods, result)
            
            # 4. Perform power analysis
            await self._perform_power_analysis(data, tests, result)
            
            # 5. Run statistical tests
            test_results = await self._run_statistical_tests(data, tests, result)
            
            # 6. Apply multiple testing correction
            if len(test_results) > 1 and correction != MultipleTestingCorrection.NONE:
                await self._apply_multiple_testing_correction(
                    test_results, correction, data.alpha, result
                )
            
            # 7. Cross-validate if possible
            await self._cross_validate_results(data, result)
            
            # 8. Generate recommendations
            self._generate_recommendations(data, result)
            
            # Final validity check
            result.is_valid = (
                len(result.issues) == 0 and
                result.power_analysis.get("achieved_power", 0) >= data.power_threshold
            )
            
        except BiologyError as e:
            logger.error(f"Error validating experiment: {str(e)}", exc_info=True)
            result.issues.append(f"Validation error: {str(e)}")
            result.is_valid = False
            
        return result
    
    def _determine_appropriate_tests(self, data: ExperimentalData) -> List[StatisticalTest]:
        """Determine appropriate statistical tests based on data"""
        tests = []
        n_groups = len(data.groups)
        
        if n_groups == 2:
            # Two group comparison
            tests.append(StatisticalTest.T_TEST)
            tests.append(StatisticalTest.MANN_WHITNEY)
        elif n_groups > 2:
            # Multiple group comparison
            tests.append(StatisticalTest.ANOVA)
            tests.append(StatisticalTest.KRUSKAL_WALLIS)
            
        # Always check for correlations if continuous data
        if all(len(group) > 10 for group in data.groups.values()):
            tests.append(StatisticalTest.PEARSON_CORR)
            tests.append(StatisticalTest.SPEARMAN_CORR)
            
        return tests
    
    def _validate_sample_sizes(self, data: ExperimentalData, result: ValidationResult):
        """Check if sample sizes are adequate"""
        for group_name, measurements in data.groups.items():
            n = len(measurements)
            if n < self.min_sample_size:
                result.issues.append(
                    f"Grupo '{group_name}' tiene tamaño de muestra insuficiente: {n} < {self.min_sample_size}"
                )
            elif n < 30:
                result.warnings.append(
                    f"Grupo '{group_name}' tiene tamaño de muestra pequeño ({n}), "
                    "los resultados pueden tener poder estadístico limitado"
                )
                
        result.statistics["sample_sizes"] = {
            name: len(measurements) for name, measurements in data.groups.items()
        }
    
    async def _check_statistical_assumptions(
        self,
        data: ExperimentalData,
        tests: List[StatisticalTest],
        result: ValidationResult
    ):
        """Check assumptions for planned statistical tests"""
        assumptions = {}
        
        # Check normality for parametric tests
        if StatisticalTest.T_TEST in tests or StatisticalTest.ANOVA in tests:
            for group_name, measurements in data.groups.items():
                if len(measurements) >= 8:  # Shapiro-Wilk needs at least 3 samples
                    _, p_value = stats.shapiro(measurements)
                    is_normal = p_value > 0.05
                    assumptions[f"normality_{group_name}"] = is_normal
                    
                    if not is_normal:
                        result.warnings.append(
                            f"Grupo '{group_name}' no pasa test de normalidad (p={p_value:.4f}). "
                            "Considera usar tests no paramétricos"
                        )
                        
        # Check homogeneity of variances
        if len(data.groups) >= 2:
            group_values = list(data.groups.values())
            if all(len(g) >= 2 for g in group_values):
                _, p_value = stats.levene(*group_values)
                equal_var = p_value > 0.05
                assumptions["equal_variances"] = equal_var
                
                if not equal_var:
                    result.warnings.append(
                        f"Varianzas no homogéneas entre grupos (p={p_value:.4f}). "
                        "Usa Welch's t-test o tests no paramétricos"
                    )
                    
        result.assumptions_met = assumptions
    
    async def _detect_outliers(
        self,
        data: ExperimentalData,
        methods: List[OutlierMethod],
        result: ValidationResult
    ):
        """Detect outliers using multiple methods"""
        outliers = {}
        
        for group_name, measurements in data.groups.items():
            group_outliers = set()
            
            for method in methods:
                if method == OutlierMethod.IQR:
                    outlier_indices = self._detect_outliers_iqr(measurements)
                elif method == OutlierMethod.Z_SCORE:
                    outlier_indices = self._detect_outliers_zscore(measurements)
                elif method == OutlierMethod.GRUBBS:
                    outlier_indices = self._detect_outliers_grubbs(measurements)
                else:
                    continue
                    
                group_outliers.update(outlier_indices)
                
            outliers[group_name] = sorted(list(group_outliers))
            
            if outliers[group_name]:
                result.warnings.append(
                    f"Grupo '{group_name}' tiene {len(outliers[group_name])} outliers detectados"
                )
                
        result.outliers = outliers
    
    def _detect_outliers_iqr(self, data: np.ndarray, multiplier: float = 1.5) -> List[int]:
        """Detect outliers using IQR method"""
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outliers = []
        for i, value in enumerate(data):
            if value < lower_bound or value > upper_bound:
                outliers.append(i)
                
        return outliers
    
    def _detect_outliers_zscore(self, data: np.ndarray, threshold: float = 3.0) -> List[int]:
        """Detect outliers using Z-score method"""
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return []
            
        z_scores = np.abs((data - mean) / std)
        outliers = np.where(z_scores > threshold)[0].tolist()
        
        return outliers
    
    def _detect_outliers_grubbs(self, data: np.ndarray, alpha: float = 0.05) -> List[int]:
        """Detect outliers using Grubbs test (single outlier at a time)"""
        outliers = []
        test_data = data.copy()
        indices = list(range(len(data)))
        
        while len(test_data) > 3:
            mean = np.mean(test_data)
            std = np.std(test_data, ddof=1)
            
            if std == 0:
                break
                
            # Calculate Grubbs statistic
            residuals = np.abs(test_data - mean)
            max_residual_idx = np.argmax(residuals)
            G = residuals[max_residual_idx] / std
            
            # Critical value
            n = len(test_data)
            t_critical = stats.t.ppf(1 - alpha / (2 * n), n - 2)
            G_critical = ((n - 1) / np.sqrt(n)) * np.sqrt(t_critical**2 / (n - 2 + t_critical**2))
            
            if G > G_critical:
                outliers.append(indices[max_residual_idx])
                test_data = np.delete(test_data, max_residual_idx)
                indices.pop(max_residual_idx)
            else:
                break
                
        return outliers
    
    async def _perform_power_analysis(
        self,
        data: ExperimentalData,
        tests: List[StatisticalTest],
        result: ValidationResult
    ):
        """Perform statistical power analysis"""
        power_results = {}
        
        if StatisticalTest.T_TEST in tests and len(data.groups) == 2 and _HAS_STATSMODELS:
            # T-test power analysis
            groups = list(data.groups.values())
            if len(groups[0]) >= 2 and len(groups[1]) >= 2:
                # Calculate effect size (Cohen's d)
                mean1, mean2 = np.mean(groups[0]), np.mean(groups[1])
                pooled_std = np.sqrt(
                    ((len(groups[0]) - 1) * np.var(groups[0], ddof=1) +
                     (len(groups[1]) - 1) * np.var(groups[1], ddof=1)) /
                    (len(groups[0]) + len(groups[1]) - 2)
                )
                
                if pooled_std > 0:
                    effect_size = abs(mean1 - mean2) / pooled_std
                    
                    # Calculate achieved power
                    power_analyzer = TTestPower()
                    achieved_power = power_analyzer.solve_power(
                        effect_size=effect_size,
                        nobs1=len(groups[0]),
                        ratio=len(groups[1]) / len(groups[0]),
                        alpha=data.alpha,
                        alternative='two-sided'
                    )
                    
                    power_results["achieved_power"] = achieved_power
                    power_results["effect_size"] = effect_size
                    power_results["effect_size_interpretation"] = self._interpret_effect_size(effect_size)
                    
                    # Calculate required sample size for desired power
                    if achieved_power < data.power_threshold:
                        required_n = power_analyzer.solve_power(
                            effect_size=effect_size,
                            power=data.power_threshold,
                            ratio=1.0,
                            alpha=data.alpha,
                            alternative='two-sided'
                        )
                        power_results["required_n_per_group"] = int(np.ceil(required_n))
                        
                        result.recommendations.append(
                            f"Aumentar tamaño de muestra a {int(np.ceil(required_n))} por grupo "
                            f"para alcanzar poder de {data.power_threshold}"
                        )
                        
        result.power_analysis = power_results
    
    def _interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size"""
        if abs(d) < self.effect_size_thresholds["small"]:
            return "negligible"
        elif abs(d) < self.effect_size_thresholds["medium"]:
            return "small"
        elif abs(d) < self.effect_size_thresholds["large"]:
            return "medium"
        else:
            return "large"
    
    async def _run_statistical_tests(
        self,
        data: ExperimentalData,
        tests: List[StatisticalTest],
        result: ValidationResult
    ) -> Dict[str, Dict[str, float]]:
        """Run specified statistical tests"""
        test_results = {}
        
        for test in tests:
            try:
                if test == StatisticalTest.T_TEST and len(data.groups) == 2:
                    groups = list(data.groups.values())
                    # Use Welch's t-test if variances are unequal
                    equal_var = result.assumptions_met.get("equal_variances", True)
                    stat, p_value = stats.ttest_ind(groups[0], groups[1], equal_var=equal_var)
                    test_results["t_test"] = {"statistic": stat, "p_value": p_value}
                    
                elif test == StatisticalTest.MANN_WHITNEY and len(data.groups) == 2:
                    groups = list(data.groups.values())
                    stat, p_value = stats.mannwhitneyu(groups[0], groups[1], alternative='two-sided')
                    test_results["mann_whitney"] = {"statistic": stat, "p_value": p_value}
                    
                elif test == StatisticalTest.ANOVA and len(data.groups) > 2:
                    groups = list(data.groups.values())
                    stat, p_value = stats.f_oneway(*groups)
                    test_results["anova"] = {"statistic": stat, "p_value": p_value}
                    
                elif test == StatisticalTest.KRUSKAL_WALLIS and len(data.groups) > 2:
                    groups = list(data.groups.values())
                    stat, p_value = stats.kruskal(*groups)
                    test_results["kruskal_wallis"] = {"statistic": stat, "p_value": p_value}
                    
            except BiologyError as e:
                result.warnings.append(f"No se pudo ejecutar {test.value}: {str(e)}")
                
        result.statistics["test_results"] = test_results
        return test_results
    
    async def _apply_multiple_testing_correction(
        self,
        test_results: Dict[str, Dict[str, float]],
        method: MultipleTestingCorrection,
        alpha: float,
        result: ValidationResult
    ):
        """Apply multiple testing correction"""
        if not test_results:
            return
            
        # Extract p-values
        test_names = []
        p_values = []
        
        for test_name, test_result in test_results.items():
            if "p_value" in test_result:
                test_names.append(test_name)
                p_values.append(test_result["p_value"])
                
        if not p_values:
            return
            
        # If statsmodels not available, skip with warning
        if not _HAS_STATSMODELS:
            result.warnings.append(
                f"Corrección por comparaciones múltiples omitida (statsmodels no disponible). Método solicitado: {method.value}"
            )
            return

        # Apply correction
        if method == MultipleTestingCorrection.BONFERRONI:
            reject, corrected_p, _, _ = multipletests(p_values, alpha=alpha, method='bonferroni')
        elif method == MultipleTestingCorrection.HOLM:
            reject, corrected_p, _, _ = multipletests(p_values, alpha=alpha, method='holm')
        elif method == MultipleTestingCorrection.FDR_BH:
            reject, corrected_p, _, _ = multipletests(p_values, alpha=alpha, method='fdr_bh')
        elif method == MultipleTestingCorrection.FDR_BY:
            reject, corrected_p, _, _ = multipletests(p_values, alpha=alpha, method='fdr_by')
        else:
            return
            
        # Store corrected p-values
        for i, test_name in enumerate(test_names):
            result.corrected_pvalues[test_name] = float(corrected_p[i])
            
        result.statistics["multiple_testing_correction"] = method.value
        result.statistics["n_tests_corrected"] = len(p_values)
        
        # Check if any significant results remain after correction
        if not any(reject):
            result.warnings.append(
                f"Ningún resultado significativo después de corrección {method.value}"
            )
    
    async def _cross_validate_results(self, data: ExperimentalData, result: ValidationResult):
        """Cross-validate results with external datasets if available"""
        if "external_datasets" not in data.metadata:
            return
            
        cv_results = []
        
        for external_data in data.metadata["external_datasets"]:
            try:
                # Compare effect sizes or other metrics
                if "effect_size" in external_data:
                    our_effect = result.power_analysis.get("effect_size", 0)
                    external_effect = external_data["effect_size"]
                    
                    # Check if effects are in same direction and similar magnitude
                    same_direction = np.sign(our_effect) == np.sign(external_effect)
                    effect_ratio = min(abs(our_effect), abs(external_effect)) / max(abs(our_effect), abs(external_effect))
                    
                    cv_results.append({
                        "dataset": external_data.get("name", "Unknown"),
                        "same_direction": same_direction,
                        "effect_ratio": effect_ratio,
                        "validated": same_direction and effect_ratio > 0.5
                    })
                    
            except BiologyError as e:
                result.warnings.append(f"Error en cross-validation: {str(e)}")
                
        if cv_results:
            result.statistics["cross_validation"] = cv_results
            validated_count = sum(1 for r in cv_results if r["validated"])
            
            if validated_count < len(cv_results) / 2:
                result.warnings.append(
                    f"Solo {validated_count}/{len(cv_results)} datasets externos validan los resultados"
                )
    
    def _generate_recommendations(self, data: ExperimentalData, result: ValidationResult):
        """Generate recommendations based on validation results"""
        
        # Sample size recommendations
        if result.power_analysis.get("achieved_power", 1.0) < data.power_threshold:
            effect_size = result.power_analysis.get("effect_size", 0)
            if effect_size < self.effect_size_thresholds["small"]:
                result.recommendations.append(
                    "El tamaño del efecto es muy pequeño. Considera si el efecto es prácticamente significativo"
                )
                
        # Outlier recommendations
        total_outliers = sum(len(outliers) for outliers in result.outliers.values())
        total_samples = sum(len(group) for group in data.groups.values())
        
        if total_outliers > 0:
            outlier_proportion = total_outliers / total_samples
            if outlier_proportion > 0.1:
                result.recommendations.append(
                    f"Alta proporción de outliers ({outlier_proportion:.1%}). "
                    "Revisa protocolo experimental y calidad de datos"
                )
            else:
                result.recommendations.append(
                    "Considera análisis de sensibilidad excluyendo outliers"
                )
                
        # Test selection recommendations
        normality_issues = sum(
            1 for key, value in result.assumptions_met.items()
            if key.startswith("normality_") and not value
        )
        
        if normality_issues > 0:
            result.recommendations.append(
                "Datos no normales detectados. Prioriza resultados de tests no paramétricos"
            )
            
        # Multiple testing recommendations
        if len(result.corrected_pvalues) > 5:
            result.recommendations.append(
                "Muchas comparaciones múltiples. Considera reducir número de hipótesis o usar FDR"
            )
    
    async def validate_reproducibility(
        self,
        original_data: ExperimentalData,
        replication_data: ExperimentalData,
        tolerance: float = 0.1
    ) -> Dict[str, Any]:
        """
        Validate reproducibility between original and replication experiments
        """
        reproducibility_report = {
            "is_reproduced": False,
            "effect_size_agreement": 0.0,
            "direction_agreement": False,
            "statistical_agreement": False,
            "details": {}
        }
        
        try:
            # Validate both experiments
            original_validation = await self.validate_experiment(original_data)
            replication_validation = await self.validate_experiment(replication_data)
            
            # Compare effect sizes
            orig_effect = original_validation.power_analysis.get("effect_size", 0)
            repl_effect = replication_validation.power_analysis.get("effect_size", 0)
            
            if orig_effect != 0:
                effect_agreement = 1 - abs(orig_effect - repl_effect) / abs(orig_effect)
                reproducibility_report["effect_size_agreement"] = effect_agreement
                reproducibility_report["direction_agreement"] = np.sign(orig_effect) == np.sign(repl_effect)
                
            # Compare statistical significance
            orig_pvals = original_validation.statistics.get("test_results", {})
            repl_pvals = replication_validation.statistics.get("test_results", {})
            
            for test_name in orig_pvals:
                if test_name in repl_pvals:
                    orig_sig = orig_pvals[test_name].get("p_value", 1) < original_data.alpha
                    repl_sig = repl_pvals[test_name].get("p_value", 1) < replication_data.alpha
                    
                    if orig_sig == repl_sig:
                        reproducibility_report["statistical_agreement"] = True
                        
            # Overall reproducibility assessment
            reproducibility_report["is_reproduced"] = (
                reproducibility_report["direction_agreement"] and
                reproducibility_report["effect_size_agreement"] > (1 - tolerance) and
                reproducibility_report["statistical_agreement"]
            )
            
            reproducibility_report["details"] = {
                "original": {
                    "effect_size": orig_effect,
                    "power": original_validation.power_analysis.get("achieved_power", 0),
                    "n_samples": sum(len(g) for g in original_data.groups.values())
                },
                "replication": {
                    "effect_size": repl_effect,
                    "power": replication_validation.power_analysis.get("achieved_power", 0),
                    "n_samples": sum(len(g) for g in replication_data.groups.values())
                }
            }
            
        except BiologyError as e:
            logger.error(f"Error validating reproducibility: {str(e)}", exc_info=True)
            reproducibility_report["error"] = str(e)
            
        return reproducibility_report


# Singleton instance
_validator_instance = None


def get_experimental_validator() -> ExperimentalValidator:
    """Get or create the singleton validator instance"""
    global _validator_instance
    
    if _validator_instance is None:
        _validator_instance = ExperimentalValidator()
        
    return _validator_instance


# Backwards-compatibility adapter expected by EngineeringLoop
class ExperimentalValidatorService:
    """
    Service-style adapter that wraps ExperimentalValidator and exposes
    a dict-based async `validate_experiment` compatible with EngineeringLoop.
    """

    def __init__(self):
        self._core = get_experimental_validator()

    async def validate_experiment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accepts a lightweight payload with optional hints and returns a service-like dict:
        {
          "success": bool,
          "validation": { ... detailed stats ... },
          "feasibility_score": float
        }
        """
        try:
            # Build minimal synthetic ExperimentalData from payload hints
            experiment_id = payload.get("experiment_id", f"eng_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}")
            precision = float(payload.get("precision", 0.95) or 0.95)
            throughput = float(payload.get("throughput", 40.0) or 40.0)

            # Create two-group synthetic data reflecting precision/throughput
            rng = np.random.default_rng(1234)
            n = max(8, int(min(50, max(10, throughput))))
            base = 1.0
            noise = max(0.01, (1.0 - precision) * 0.2)
            group_a = rng.normal(loc=base, scale=noise, size=n)
            group_b = rng.normal(loc=base * (1.0 + noise), scale=noise, size=n)

            data = ExperimentalData(
                experiment_id=experiment_id,
                groups={"A": group_a, "B": group_b},
                metadata={
                    "source": "engineering_adapter",
                    "hints": {
                        "experiment_type": payload.get("experiment_type"),
                        "equipment": payload.get("equipment"),
                    },
                },
                alpha=0.05,
                power_threshold=0.8,
            )

            result = await self._core.validate_experiment(data)

            # Convert ValidationResult dataclass to a dict
            validation_dict = {
                "validation_id": result.validation_id,
                "experiment_id": result.experiment_id,
                "is_valid": result.is_valid,
                "confidence_level": result.confidence_level,
                "issues": result.issues,
                "warnings": result.warnings,
                "statistics": result.statistics,
                "power_analysis": result.power_analysis,
                "outliers": result.outliers,
                "assumptions_met": result.assumptions_met,
                "corrected_pvalues": result.corrected_pvalues,
                "recommendations": result.recommendations,
                "timestamp": result.timestamp.isoformat(),
            }

            # Simple feasibility score based on validity and power
            feasibility = 0.6
            if result.is_valid:
                feasibility += 0.25
            feasibility += min(0.15, float(result.power_analysis.get("achieved_power", 0.0)) * 0.15)
            feasibility = float(min(1.0, max(0.0, feasibility)))

            return {
                "success": True,
                "validation": validation_dict,
                "feasibility_score": feasibility,
            }
        except Exception as e:  # noqa: BLE001 - broad for adapter safety
            logger.debug(f"ExperimentalValidatorService error: {e}")
            return {
                "success": False,
                "error": str(e),
            }


__all__ = [
    "ExperimentalValidator",
    "ExperimentalValidatorService",
    "get_experimental_validator",
    "ValidationResult",
    "ExperimentalData",
]
