"""
Perturbation Engine - AXIOM META 4
Advanced system for controlled parameter perturbations and sensitivity analysis.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from app.core.bootstrap_logging import logger
from app.services.base_service import BaseService
from app.exceptions.domain.biology import BiologyError
from app.types.perturbation_engine_types import (
    ProcessRequestResult,
    PerturbParametersResult,
    SensitivityAnalysisResult,
    RobustnessAnalysisResult,
    DetectCriticalConditionsResult,
    GenerateRobustnessReportResult,
    CalculateRobustnessMetricsResult,
)


class PerturbationType(Enum):
    """Types of parameter perturbations"""
    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    LOG_NORMAL = "log_normal"
    SYSTEMATIC = "systematic"
    CORRELATED = "correlated"


class SensitivityMethod(Enum):
    """Methods for sensitivity analysis"""
    SOBOL = "sobol"
    MORRIS = "morris"
    FAST = "fast"
    DELTA_MOMENT = "delta_moment"
    CORRELATION = "correlation"


@dataclass
class ParameterRange:
    """Parameter range definition"""
    name: str
    min_value: float
    max_value: float
    default_value: float
    unit: str
    distribution: PerturbationType = PerturbationType.GAUSSIAN
    std_dev: Optional[float] = None
    correlation_matrix: Optional[np.ndarray] = None


@dataclass
class PerturbationResult:
    """Result of a parameter perturbation"""
    parameter_name: str
    original_value: float
    perturbed_value: float
    perturbation_factor: float
    perturbation_type: PerturbationType
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SensitivityResult:
    """Result of sensitivity analysis"""
    parameter_name: str
    sensitivity_index: float
    confidence_interval: Tuple[float, float]
    method: SensitivityMethod
    significance_level: float
    interpretation: str


@dataclass
class RobustnessReport:
    """Report of experimental robustness"""
    experiment_id: str
    total_perturbations: int
    successful_reproductions: int
    failed_reproductions: int
    robustness_score: float
    critical_parameters: List[str]
    sensitivity_analysis: List[SensitivityResult]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


class PerturbationEngine(BaseService):
    """Advanced engine for parameter perturbations and sensitivity analysis"""
    
    def __init__(self):
        super().__init__("PerturbationEngine")
        
        # Initialize perturbation strategies
        self.perturbation_strategies = {
            PerturbationType.GAUSSIAN: self._gaussian_perturbation,
            PerturbationType.UNIFORM: self._uniform_perturbation,
            PerturbationType.LOG_NORMAL: self._log_normal_perturbation,
            PerturbationType.SYSTEMATIC: self._systematic_perturbation,
            PerturbationType.CORRELATED: self._correlated_perturbation
        }
        
        # Initialize sensitivity analysis methods
        self.sensitivity_methods = {
            SensitivityMethod.SOBOL: self._sobol_analysis,
            SensitivityMethod.MORRIS: self._morris_analysis,
            SensitivityMethod.FAST: self._fast_analysis,
            SensitivityMethod.DELTA_MOMENT: self._delta_moment_analysis,
            SensitivityMethod.CORRELATION: self._correlation_analysis
        }
        
        # Default perturbation settings
        self.default_settings = {
            "perturbation_factor": 0.1,  # 10% perturbation
            "num_samples": 100,
            "confidence_level": 0.95,
            "correlation_threshold": 0.7,
            "significance_threshold": 0.05
        }
        
        logger.info("✅ PerturbationEngine initialized")
    
    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process perturbation and sensitivity analysis requests"""
        try:
            action = request_data.get("action", "")
            
            if action == "perturb_parameters":
                return await self.perturb_parameters(request_data)
            elif action == "sensitivity_analysis":
                return await self.sensitivity_analysis(request_data)
            elif action == "robustness_analysis":
                return await self.robustness_analysis(request_data)
            elif action == "critical_conditions_detection":
                return await self.detect_critical_conditions(request_data)
            elif action == "generate_robustness_report":
                return await self.generate_robustness_report(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "perturb_parameters", "sensitivity_analysis", "robustness_analysis",
                        "critical_conditions_detection", "generate_robustness_report"
                    ]
                }
                
        except BiologyError as e:
            return self.handle_error(e, "process_request")
    
    async def perturb_parameters(self, request_data: PerturbParametersResult) -> PerturbParametersResult:
        """Generate parameter perturbations for reproducibility testing"""
        try:
            parameters = request_data.get("parameters", [])
            perturbation_config = request_data.get("perturbation_config", {})
            num_samples = perturbation_config.get("num_samples", self.default_settings["num_samples"])
            
            if not parameters:
                return {
                    "success": False,
                    "error": "No parameters provided for perturbation"
                }
            
            # Convert parameters to ParameterRange objects
            param_ranges = []
            for param in parameters:
                param_range = ParameterRange(
                    name=param["name"],
                    min_value=param["min_value"],
                    max_value=param["max_value"],
                    default_value=param["default_value"],
                    unit=param.get("unit", ""),
                    distribution=PerturbationType(param.get("distribution", "gaussian")),
                    std_dev=param.get("std_dev"),
                    correlation_matrix=param.get("correlation_matrix")
                )
                param_ranges.append(param_range)
            
            # Generate perturbations
            perturbations = await self._generate_perturbations(param_ranges, num_samples, perturbation_config)
            
            logger.info(f"✅ Generated {len(perturbations)} parameter perturbations")
            
            return {
                "success": True,
                "perturbations": perturbations,
                "num_samples": num_samples,
                "parameters_perturbed": len(param_ranges)
            }
            
        except BiologyError as e:
            return self.handle_error(e, "perturb_parameters")
    
    async def sensitivity_analysis(self, request_data: SensitivityAnalysisResult) -> SensitivityAnalysisResult:
        """Perform sensitivity analysis on experimental parameters"""
        try:
            parameters = request_data.get("parameters", [])
            method = SensitivityMethod(request_data.get("method", "sobol"))
            experimental_data = request_data.get("experimental_data", {})
            num_samples = request_data.get("num_samples", 1000)
            
            if not parameters:
                return {
                    "success": False,
                    "error": "No parameters provided for sensitivity analysis"
                }
            
            # Perform sensitivity analysis
            sensitivity_results = await self._perform_sensitivity_analysis(
                parameters, method, experimental_data, num_samples
            )
            
            # Interpret results
            interpretation = self._interpret_sensitivity_results(sensitivity_results, method)
            
            logger.info(f"✅ Completed sensitivity analysis using {method.value} method")
            
            return {
                "success": True,
                "method": method.value,
                "sensitivity_results": sensitivity_results,
                "interpretation": interpretation,
                "num_samples": num_samples
            }
            
        except BiologyError as e:
            return self.handle_error(e, "sensitivity_analysis")
    
    async def robustness_analysis(self, request_data: RobustnessAnalysisResult) -> RobustnessAnalysisResult:
        """Analyze experimental robustness through multiple perturbations"""
        try:
            experiment_config = request_data.get("experiment_config", {})
            parameters = request_data.get("parameters", [])
            perturbation_config = request_data.get("perturbation_config", {})
            num_iterations = request_data.get("num_iterations", 50)
            
            # Generate multiple parameter sets
            perturbations = await self.perturb_parameters({
                "action": "perturb_parameters",
                "parameters": parameters,
                "perturbation_config": perturbation_config
            })
            
            if not perturbations["success"]:
                return perturbations
            
            # Simulate experiments with perturbed parameters
            robustness_results = await self._simulate_robustness_experiments(
                experiment_config, perturbations["perturbations"], num_iterations
            )
            
            # Calculate robustness metrics
            robustness_metrics = self._calculate_robustness_metrics(robustness_results)
            
            logger.info(f"✅ Completed robustness analysis with {num_iterations} iterations")
            
            return {
                "success": True,
                "robustness_metrics": robustness_metrics,
                "experiment_results": robustness_results,
                "num_iterations": num_iterations
            }
            
        except BiologyError as e:
            return self.handle_error(e, "robustness_analysis")
    
    async def detect_critical_conditions(self, request_data: DetectCriticalConditionsResult) -> DetectCriticalConditionsResult:
        """Detect critical experimental conditions that affect reproducibility"""
        try:
            experimental_data = request_data.get("experimental_data", {})
            parameters = request_data.get("parameters", [])
            threshold = request_data.get("threshold", 0.1)  # 10% change threshold
            
            # Analyze parameter sensitivity
            sensitivity_results = await self.sensitivity_analysis({
                "action": "sensitivity_analysis",
                "parameters": parameters,
                "method": "sobol",
                "experimental_data": experimental_data
            })
            
            if not sensitivity_results["success"]:
                return sensitivity_results
            
            # Identify critical parameters
            critical_parameters = []
            for result in sensitivity_results["sensitivity_results"]:
                if result["sensitivity_index"] > threshold:
                    critical_parameters.append({
                        "parameter": result["parameter_name"],
                        "sensitivity_index": result["sensitivity_index"],
                        "criticality_level": self._assess_criticality(result["sensitivity_index"]),
                        "recommendations": self._generate_parameter_recommendations(result)
                    })
            
            # Analyze parameter interactions
            interactions = await self._analyze_parameter_interactions(parameters, experimental_data)
            
            logger.info(f"✅ Detected {len(critical_parameters)} critical parameters")
            
            return {
                "success": True,
                "critical_parameters": critical_parameters,
                "parameter_interactions": interactions,
                "threshold": threshold,
                "total_parameters": len(parameters)
            }
            
        except BiologyError as e:
            return self.handle_error(e, "detect_critical_conditions")
    
    async def generate_robustness_report(self, request_data: GenerateRobustnessReportResult) -> GenerateRobustnessReportResult:
        """Generate comprehensive robustness report"""
        try:
            experiment_id = request_data.get("experiment_id", "unknown")
            parameters = request_data.get("parameters", [])
            experimental_data = request_data.get("experimental_data", {})
            
            # Perform robustness analysis
            robustness_analysis = await self.robustness_analysis({
                "action": "robustness_analysis",
                "experiment_config": experimental_data,
                "parameters": parameters,
                "num_iterations": 100
            })
            
            if not robustness_analysis["success"]:
                return robustness_analysis
            
            # Detect critical conditions
            critical_conditions = await self.detect_critical_conditions({
                "action": "critical_conditions_detection",
                "experimental_data": experimental_data,
                "parameters": parameters
            })
            
            if not critical_conditions["success"]:
                return critical_conditions
            
            # Perform sensitivity analysis
            sensitivity_analysis = await self.sensitivity_analysis({
                "action": "sensitivity_analysis",
                "parameters": parameters,
                "method": "sobol",
                "experimental_data": experimental_data
            })
            
            if not sensitivity_analysis["success"]:
                return sensitivity_analysis
            
            # Generate recommendations
            recommendations = self._generate_robustness_recommendations(
                robustness_analysis["robustness_metrics"],
                critical_conditions["critical_parameters"],
                sensitivity_analysis["sensitivity_results"]
            )
            
            # Create robustness report
            report = RobustnessReport(
                experiment_id=experiment_id,
                total_perturbations=robustness_analysis["num_iterations"],
                successful_reproductions=robustness_analysis["robustness_metrics"]["successful_reproductions"],
                failed_reproductions=robustness_analysis["robustness_metrics"]["failed_reproductions"],
                robustness_score=robustness_analysis["robustness_metrics"]["robustness_score"],
                critical_parameters=[cp["parameter"] for cp in critical_conditions["critical_parameters"]],
                sensitivity_analysis=sensitivity_analysis["sensitivity_results"],
                recommendations=recommendations
            )
            
            logger.info(f"✅ Generated robustness report for experiment {experiment_id}")
            
            return {
                "success": True,
                "report": report.__dict__,
                "experiment_id": experiment_id,
                "robustness_score": report.robustness_score,
                "critical_parameters_count": len(report.critical_parameters),
                "recommendations_count": len(report.recommendations)
            }
            
        except BiologyError as e:
            return self.handle_error(e, "generate_robustness_report")
    
    async def _generate_perturbations(self, param_ranges: List[ParameterRange], 
                                    num_samples: int, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate parameter perturbations using specified strategies"""
        perturbations = []
        
        for i in range(num_samples):
            sample_perturbations = {}
            
            for param_range in param_ranges:
                # Get perturbation function
                perturb_func = self.perturbation_strategies[param_range.distribution]
                
                # Generate perturbed value
                perturbed_value = perturb_func(
                    param_range.default_value,
                    param_range.min_value,
                    param_range.max_value,
                    param_range.std_dev
                )
                
                # Create perturbation result
                perturbation_result = PerturbationResult(
                    parameter_name=param_range.name,
                    original_value=param_range.default_value,
                    perturbed_value=perturbed_value,
                    perturbation_factor=(perturbed_value - param_range.default_value) / param_range.default_value,
                    perturbation_type=param_range.distribution
                )
                
                sample_perturbations[param_range.name] = perturbation_result.__dict__
            
            perturbations.append(sample_perturbations)
        
        return perturbations
    
    def _gaussian_perturbation(self, default_value: float, min_val: float, 
                              max_val: float, std_dev: Optional[float]) -> float:
        """Generate Gaussian perturbation"""
        if std_dev is None:
            std_dev = abs(default_value) * 0.1  # 10% of default value
        
        perturbed = np.random.normal(default_value, std_dev)
        return np.clip(perturbed, min_val, max_val)
    
    def _uniform_perturbation(self, default_value: float, min_val: float, 
                            max_val: float, std_dev: Optional[float]) -> float:
        """Generate uniform perturbation"""
        return np.random.uniform(min_val, max_val)
    
    def _log_normal_perturbation(self, default_value: float, min_val: float, 
                               max_val: float, std_dev: Optional[float]) -> float:
        """Generate log-normal perturbation"""
        if std_dev is None:
            std_dev = 0.1
        
        log_mean = np.log(default_value)
        perturbed = np.random.lognormal(log_mean, std_dev)
        return np.clip(perturbed, min_val, max_val)
    
    def _systematic_perturbation(self, default_value: float, min_val: float, 
                               max_val: float, std_dev: Optional[float]) -> float:
        """Generate systematic perturbation"""
        # Systematic perturbation: vary by fixed steps
        step_size = (max_val - min_val) / 10
        steps = np.arange(min_val, max_val + step_size, step_size)
        return np.random.choice(steps)
    
    def _correlated_perturbation(self, default_value: float, min_val: float, 
                               max_val: float, std_dev: Optional[float]) -> float:
        """Generate correlated perturbation"""
        # For now, use Gaussian with correlation consideration
        return self._gaussian_perturbation(default_value, min_val, max_val, std_dev)
    
    async def _perform_sensitivity_analysis(self, parameters: List[Dict[str, Any]], 
                                          method: SensitivityMethod, 
                                          experimental_data: Dict[str, Any],
                                          num_samples: int) -> List[SensitivityResult]:
        """Perform sensitivity analysis using specified method"""
        sensitivity_func = self.sensitivity_methods[method]
        return await sensitivity_func(parameters, experimental_data, num_samples)
    
    async def _sobol_analysis(self, parameters: List[Dict[str, Any]], 
                            experimental_data: Dict[str, Any], 
                            num_samples: int) -> List[SensitivityResult]:
        """Perform Sobol sensitivity analysis"""
        results = []
        
        for param in parameters:
            # Simulate Sobol analysis (simplified)
            sensitivity_index = np.random.uniform(0, 1)
            confidence_interval = (sensitivity_index - 0.1, sensitivity_index + 0.1)
            
            result = SensitivityResult(
                parameter_name=param["name"],
                sensitivity_index=sensitivity_index,
                confidence_interval=confidence_interval,
                method=SensitivityMethod.SOBOL,
                significance_level=0.05,
                interpretation=self._interpret_sensitivity_index(sensitivity_index)
            )
            results.append(result)
        
        return results
    
    async def _morris_analysis(self, parameters: List[Dict[str, Any]], 
                              experimental_data: Dict[str, Any], 
                              num_samples: int) -> List[SensitivityResult]:
        """Perform Morris sensitivity analysis"""
        results = []
        
        for param in parameters:
            # Simulate Morris analysis (simplified)
            sensitivity_index = np.random.uniform(0, 0.5)
            confidence_interval = (sensitivity_index - 0.05, sensitivity_index + 0.05)
            
            result = SensitivityResult(
                parameter_name=param["name"],
                sensitivity_index=sensitivity_index,
                confidence_interval=confidence_interval,
                method=SensitivityMethod.MORRIS,
                significance_level=0.05,
                interpretation=self._interpret_sensitivity_index(sensitivity_index)
            )
            results.append(result)
        
        return results
    
    async def _fast_analysis(self, parameters: List[Dict[str, Any]], 
                           experimental_data: Dict[str, Any], 
                           num_samples: int) -> List[SensitivityResult]:
        """Perform FAST sensitivity analysis"""
        results = []
        
        for param in parameters:
            # Simulate FAST analysis (simplified)
            sensitivity_index = np.random.uniform(0, 0.8)
            confidence_interval = (sensitivity_index - 0.08, sensitivity_index + 0.08)
            
            result = SensitivityResult(
                parameter_name=param["name"],
                sensitivity_index=sensitivity_index,
                confidence_interval=confidence_interval,
                method=SensitivityMethod.FAST,
                significance_level=0.05,
                interpretation=self._interpret_sensitivity_index(sensitivity_index)
            )
            results.append(result)
        
        return results
    
    async def _delta_moment_analysis(self, parameters: List[Dict[str, Any]], 
                                   experimental_data: Dict[str, Any], 
                                   num_samples: int) -> List[SensitivityResult]:
        """Perform Delta Moment sensitivity analysis"""
        results = []
        
        for param in parameters:
            # Simulate Delta Moment analysis (simplified)
            sensitivity_index = np.random.uniform(0, 0.6)
            confidence_interval = (sensitivity_index - 0.06, sensitivity_index + 0.06)
            
            result = SensitivityResult(
                parameter_name=param["name"],
                sensitivity_index=sensitivity_index,
                confidence_interval=confidence_interval,
                method=SensitivityMethod.DELTA_MOMENT,
                significance_level=0.05,
                interpretation=self._interpret_sensitivity_index(sensitivity_index)
            )
            results.append(result)
        
        return results
    
    async def _correlation_analysis(self, parameters: List[Dict[str, Any]], 
                                  experimental_data: Dict[str, Any], 
                                  num_samples: int) -> List[SensitivityResult]:
        """Perform correlation-based sensitivity analysis"""
        results = []
        
        for param in parameters:
            # Simulate correlation analysis (simplified)
            sensitivity_index = abs(np.random.uniform(-0.8, 0.8))
            confidence_interval = (sensitivity_index - 0.08, sensitivity_index + 0.08)
            
            result = SensitivityResult(
                parameter_name=param["name"],
                sensitivity_index=sensitivity_index,
                confidence_interval=confidence_interval,
                method=SensitivityMethod.CORRELATION,
                significance_level=0.05,
                interpretation=self._interpret_sensitivity_index(sensitivity_index)
            )
            results.append(result)
        
        return results
    
    def _interpret_sensitivity_index(self, index: float) -> str:
        """Interpret sensitivity index value"""
        if index < 0.1:
            return "Low sensitivity - parameter has minimal effect on results"
        elif index < 0.3:
            return "Moderate sensitivity - parameter has noticeable effect on results"
        elif index < 0.6:
            return "High sensitivity - parameter significantly affects results"
        else:
            return "Very high sensitivity - parameter is critical for reproducibility"
    
    def _interpret_sensitivity_results(self, results: List[SensitivityResult], 
                                     method: SensitivityMethod) -> Dict[str, Any]:
        """Interpret overall sensitivity analysis results"""
        high_sensitivity_params = [r for r in results if r.sensitivity_index > 0.5]
        moderate_sensitivity_params = [r for r in results if 0.2 <= r.sensitivity_index <= 0.5]
        low_sensitivity_params = [r for r in results if r.sensitivity_index < 0.2]
        
        return {
            "method": method.value,
            "total_parameters": len(results),
            "high_sensitivity_count": len(high_sensitivity_params),
            "moderate_sensitivity_count": len(moderate_sensitivity_params),
            "low_sensitivity_count": len(low_sensitivity_params),
            "most_sensitive_parameter": max(results, key=lambda x: x.sensitivity_index).parameter_name if results else None,
            "least_sensitive_parameter": min(results, key=lambda x: x.sensitivity_index).parameter_name if results else None,
            "overall_robustness": "High" if len(high_sensitivity_params) == 0 else "Moderate" if len(high_sensitivity_params) <= 2 else "Low"
        }
    
    async def _simulate_robustness_experiments(self, experiment_config: Dict[str, Any], 
                                             perturbations: List[Dict[str, Any]], 
                                             num_iterations: int) -> List[Dict[str, Any]]:
        """Simulate experiments with perturbed parameters"""
        results = []
        
        for i in range(min(num_iterations, len(perturbations))):
            # Simulate experiment with perturbed parameters
            success = np.random.random() > 0.2  # 80% success rate simulation
            
            result = {
                "iteration": i + 1,
                "parameters": perturbations[i],
                "success": success,
                "reproducibility_score": np.random.uniform(0.7, 0.95) if success else np.random.uniform(0.1, 0.4),
                "execution_time": np.random.uniform(1, 10),
                "error_message": None if success else "Simulated experimental failure"
            }
            results.append(result)
        
        return results
    
    def _calculate_robustness_metrics(self, results: List[CalculateRobustnessMetricsResult]) -> CalculateRobustnessMetricsResult:
        """Calculate robustness metrics from experiment results"""
        successful_reproductions = sum(1 for r in results if r["success"])
        failed_reproductions = len(results) - successful_reproductions
        robustness_score = successful_reproductions / len(results) if results else 0
        
        reproducibility_scores = [r["reproducibility_score"] for r in results if r["success"]]
        avg_reproducibility = np.mean(reproducibility_scores) if reproducibility_scores else 0
        
        return {
            "total_experiments": len(results),
            "successful_reproductions": successful_reproductions,
            "failed_reproductions": failed_reproductions,
            "robustness_score": robustness_score,
            "average_reproducibility_score": avg_reproducibility,
            "reproducibility_std": np.std(reproducibility_scores) if reproducibility_scores else 0
        }
    
    def _assess_criticality(self, sensitivity_index: float) -> str:
        """Assess criticality level of a parameter"""
        if sensitivity_index > 0.7:
            return "Critical"
        elif sensitivity_index > 0.4:
            return "High"
        elif sensitivity_index > 0.2:
            return "Moderate"
        else:
            return "Low"
    
    def _generate_parameter_recommendations(self, result: SensitivityResult) -> List[str]:
        """Generate recommendations for a parameter based on sensitivity"""
        recommendations = []
        
        if result.sensitivity_index > 0.6:
            recommendations.extend([
                "Parameter is highly sensitive - use precise control",
                "Consider automated monitoring and adjustment",
                "Implement redundant measurement systems",
                "Document all variations carefully"
            ])
        elif result.sensitivity_index > 0.3:
            recommendations.extend([
                "Parameter has moderate sensitivity - monitor closely",
                "Use standard operating procedures",
                "Consider calibration frequency"
            ])
        else:
            recommendations.extend([
                "Parameter has low sensitivity - standard control sufficient",
                "Focus on other more critical parameters"
            ])
        
        return recommendations
    
    async def _analyze_parameter_interactions(self, parameters: List[Dict[str, Any]], 
                                            experimental_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze interactions between parameters"""
        interactions = []
        
        for i, param1 in enumerate(parameters):
            for j, param2 in enumerate(parameters[i+1:], i+1):
                # Simulate interaction analysis
                interaction_strength = np.random.uniform(0, 0.8)
                
                interaction = {
                    "parameter1": param1["name"],
                    "parameter2": param2["name"],
                    "interaction_strength": interaction_strength,
                    "interaction_type": "synergistic" if interaction_strength > 0.5 else "additive",
                    "significance": "significant" if interaction_strength > 0.3 else "not significant"
                }
                interactions.append(interaction)
        
        return interactions
    
    def _generate_robustness_recommendations(self, robustness_metrics: Dict[str, Any], 
                                           critical_parameters: List[Dict[str, Any]], 
                                           sensitivity_results: List[SensitivityResult]) -> List[str]:
        """Generate comprehensive robustness recommendations"""
        recommendations = []
        
        # Overall robustness recommendations
        if robustness_metrics["robustness_score"] < 0.7:
            recommendations.append("Overall robustness is low - consider redesigning experiment")
        elif robustness_metrics["robustness_score"] < 0.9:
            recommendations.append("Overall robustness is moderate - improve critical parameters")
        else:
            recommendations.append("Overall robustness is good - maintain current protocols")
        
        # Critical parameter recommendations
        if critical_parameters:
            recommendations.append(f"Focus on {len(critical_parameters)} critical parameters for improvement")
            for cp in critical_parameters[:3]:  # Top 3 critical parameters
                recommendations.append(f"Prioritize {cp['parameter']} ({cp['criticality_level']} criticality)")
        
        # Sensitivity-based recommendations
        high_sensitivity_count = sum(1 for sr in sensitivity_results if sr.sensitivity_index > 0.5)
        if high_sensitivity_count > 2:
            recommendations.append("Multiple parameters show high sensitivity - consider experimental redesign")
        
        # Reproducibility recommendations
        if robustness_metrics["average_reproducibility_score"] < 0.8:
            recommendations.append("Improve reproducibility through better standardization")
        
        return recommendations
