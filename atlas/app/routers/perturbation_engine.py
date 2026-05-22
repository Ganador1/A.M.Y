"""
Perturbation Engine Router - AXIOM META 4
API endpoints for advanced parameter perturbations and sensitivity analysis.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from app.core.bootstrap_logging import logger
from app.services.perturbation_engine import PerturbationEngine, PerturbationType, SensitivityMethod
from app.security import require_scopes
from app.exceptions.domain.biology import BiologyError

router = APIRouter(prefix="/api/v1/perturbation-engine", tags=["perturbation-engine"])
perturbation_engine_router = router


class ParameterDefinition(BaseModel):
    """Parameter definition for perturbation"""
    name: str = Field(..., description="Parameter name")
    min_value: float = Field(..., description="Minimum value")
    max_value: float = Field(..., description="Maximum value")
    default_value: float = Field(..., description="Default value")
    unit: str = Field(default="", description="Parameter unit")
    distribution: str = Field(default="gaussian", description="Perturbation distribution type")
    std_dev: Optional[float] = Field(default=None, description="Standard deviation for Gaussian distribution")
    correlation_matrix: Optional[List[List[float]]] = Field(default=None, description="Correlation matrix for correlated perturbations")


class PerturbationConfig(BaseModel):
    """Configuration for parameter perturbations"""
    num_samples: int = Field(default=100, description="Number of perturbation samples to generate")
    perturbation_factor: float = Field(default=0.1, description="Default perturbation factor (10%)")
    confidence_level: float = Field(default=0.95, description="Confidence level for analysis")
    correlation_threshold: float = Field(default=0.7, description="Threshold for correlation analysis")
    significance_threshold: float = Field(default=0.05, description="Significance threshold for statistical tests")


class PerturbationRequest(BaseModel):
    """Request model for parameter perturbations"""
    parameters: List[ParameterDefinition] = Field(..., description="Parameters to perturb")
    perturbation_config: PerturbationConfig = Field(default_factory=PerturbationConfig, description="Perturbation configuration")


class SensitivityAnalysisRequest(BaseModel):
    """Request model for sensitivity analysis"""
    parameters: List[ParameterDefinition] = Field(..., description="Parameters to analyze")
    method: str = Field(default="sobol", description="Sensitivity analysis method")
    experimental_data: Dict[str, Any] = Field(default_factory=dict, description="Experimental data for analysis")
    num_samples: int = Field(default=1000, description="Number of samples for analysis")


class RobustnessAnalysisRequest(BaseModel):
    """Request model for robustness analysis"""
    experiment_config: Dict[str, Any] = Field(..., description="Experiment configuration")
    parameters: List[ParameterDefinition] = Field(..., description="Parameters to analyze")
    perturbation_config: PerturbationConfig = Field(default_factory=PerturbationConfig, description="Perturbation configuration")
    num_iterations: int = Field(default=50, description="Number of robustness iterations")


class CriticalConditionsRequest(BaseModel):
    """Request model for critical conditions detection"""
    experimental_data: Dict[str, Any] = Field(..., description="Experimental data")
    parameters: List[ParameterDefinition] = Field(..., description="Parameters to analyze")
    threshold: float = Field(default=0.1, description="Threshold for criticality detection")


class RobustnessReportRequest(BaseModel):
    """Request model for robustness report generation"""
    experiment_id: str = Field(..., description="Experiment ID")
    parameters: List[ParameterDefinition] = Field(..., description="Parameters to analyze")
    experimental_data: Dict[str, Any] = Field(default_factory=dict, description="Experimental data")


# Initialize perturbation engine service
perturbation_engine = PerturbationEngine()


@router.post("/perturb-parameters", summary="Generate Parameter Perturbations")
async def perturb_parameters(request: PerturbationRequest, background_tasks: BackgroundTasks):
    """
    Generate parameter perturbations for reproducibility testing.
    
    This endpoint generates multiple sets of perturbed parameters using various
    distribution strategies (Gaussian, uniform, log-normal, systematic, correlated).
    
    Useful for:
    - Testing experimental robustness
    - Identifying critical parameters
    - Preparing reproducibility studies
    """
    try:
        # Convert Pydantic models to dictionaries
        parameters_dict = [param.dict() for param in request.parameters]
        config_dict = request.perturbation_config.dict()
        
        result = await perturbation_engine.perturb_parameters({
            "action": "perturb_parameters",
            "parameters": parameters_dict,
            "perturbation_config": config_dict
        })
        
        if result["success"]:
            return {
                "success": True,
                "perturbations": result["perturbations"],
                "num_samples": result["num_samples"],
                "parameters_perturbed": result["parameters_perturbed"],
                "perturbation_types": list(set(
                    pert[param.name]["perturbation_type"] 
                    for pert in result["perturbations"] 
                    for param in request.parameters
                ))
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating parameter perturbations: {e}")
        raise HTTPException(status_code=500, detail=f"Parameter perturbation failed: {str(e)}")


@router.post("/sensitivity-analysis", summary="Perform Sensitivity Analysis")
async def sensitivity_analysis(request: SensitivityAnalysisRequest):
    """
    Perform sensitivity analysis on experimental parameters.
    
    Available methods:
    - sobol: Sobol indices for global sensitivity
    - morris: Morris screening method
    - fast: Fourier Amplitude Sensitivity Test
    - delta_moment: Delta moment-based analysis
    - correlation: Correlation-based analysis
    
    Returns sensitivity indices, confidence intervals, and interpretations.
    """
    try:
        # Convert Pydantic models to dictionaries
        parameters_dict = [param.dict() for param in request.parameters]
        
        result = await perturbation_engine.sensitivity_analysis({
            "action": "sensitivity_analysis",
            "parameters": parameters_dict,
            "method": request.method,
            "experimental_data": request.experimental_data,
            "num_samples": request.num_samples
        })
        
        if result["success"]:
            return {
                "success": True,
                "method": result["method"],
                "sensitivity_results": result["sensitivity_results"],
                "interpretation": result["interpretation"],
                "num_samples": result["num_samples"],
                "summary": {
                    "total_parameters": result["interpretation"]["total_parameters"],
                    "high_sensitivity_count": result["interpretation"]["high_sensitivity_count"],
                    "overall_robustness": result["interpretation"]["overall_robustness"],
                    "most_sensitive_parameter": result["interpretation"]["most_sensitive_parameter"]
                }
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error performing sensitivity analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Sensitivity analysis failed: {str(e)}")


@router.post("/robustness-analysis", summary="Analyze Experimental Robustness")
async def robustness_analysis(request: RobustnessAnalysisRequest):
    """
    Analyze experimental robustness through multiple parameter perturbations.
    
    This endpoint:
    - Generates multiple parameter sets with perturbations
    - Simulates experiments with each parameter set
    - Calculates robustness metrics
    - Identifies failure patterns
    
    Returns comprehensive robustness assessment.
    """
    try:
        # Convert Pydantic models to dictionaries
        parameters_dict = [param.dict() for param in request.parameters]
        config_dict = request.perturbation_config.dict()
        
        result = await perturbation_engine.robustness_analysis({
            "action": "robustness_analysis",
            "experiment_config": request.experiment_config,
            "parameters": parameters_dict,
            "perturbation_config": config_dict,
            "num_iterations": request.num_iterations
        })
        
        if result["success"]:
            return {
                "success": True,
                "robustness_metrics": result["robustness_metrics"],
                "experiment_results": result["experiment_results"],
                "num_iterations": result["num_iterations"],
                "summary": {
                    "robustness_score": result["robustness_metrics"]["robustness_score"],
                    "success_rate": result["robustness_metrics"]["successful_reproductions"] / result["robustness_metrics"]["total_experiments"],
                    "average_reproducibility": result["robustness_metrics"]["average_reproducibility_score"]
                }
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error performing robustness analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Robustness analysis failed: {str(e)}")


@router.post("/detect-critical-conditions", summary="Detect Critical Experimental Conditions")
async def detect_critical_conditions(request: CriticalConditionsRequest):
    """
    Detect critical experimental conditions that affect reproducibility.
    
    This endpoint:
    - Analyzes parameter sensitivity
    - Identifies critical parameters
    - Assesses parameter interactions
    - Generates recommendations
    
    Returns critical parameters with their impact levels and recommendations.
    """
    try:
        # Convert Pydantic models to dictionaries
        parameters_dict = [param.dict() for param in request.parameters]
        
        result = await perturbation_engine.detect_critical_conditions({
            "action": "critical_conditions_detection",
            "experimental_data": request.experimental_data,
            "parameters": parameters_dict,
            "threshold": request.threshold
        })
        
        if result["success"]:
            return {
                "success": True,
                "critical_parameters": result["critical_parameters"],
                "parameter_interactions": result["parameter_interactions"],
                "threshold": result["threshold"],
                "total_parameters": result["total_parameters"],
                "summary": {
                    "critical_count": len(result["critical_parameters"]),
                    "high_criticality_count": len([cp for cp in result["critical_parameters"] if cp["criticality_level"] == "Critical"]),
                    "significant_interactions": len([pi for pi in result["parameter_interactions"] if pi["significance"] == "significant"])
                }
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error detecting critical conditions: {e}")
        raise HTTPException(status_code=500, detail=f"Critical conditions detection failed: {str(e)}")


@router.post("/generate-robustness-report", summary="Generate Comprehensive Robustness Report")
async def generate_robustness_report(request: RobustnessReportRequest):
    """
    Generate comprehensive robustness report for an experiment.
    
    This endpoint combines:
    - Robustness analysis
    - Critical conditions detection
    - Sensitivity analysis
    - Recommendations generation
    
    Returns a complete robustness assessment report.
    """
    try:
        # Convert Pydantic models to dictionaries
        parameters_dict = [param.dict() for param in request.parameters]
        
        result = await perturbation_engine.generate_robustness_report({
            "action": "generate_robustness_report",
            "experiment_id": request.experiment_id,
            "parameters": parameters_dict,
            "experimental_data": request.experimental_data
        })
        
        if result["success"]:
            return {
                "success": True,
                "report": result["report"],
                "experiment_id": result["experiment_id"],
                "robustness_score": result["robustness_score"],
                "critical_parameters_count": result["critical_parameters_count"],
                "recommendations_count": result["recommendations_count"],
                "summary": {
                    "overall_robustness": "High" if result["robustness_score"] > 0.8 else "Moderate" if result["robustness_score"] > 0.6 else "Low",
                    "critical_parameters": result["report"]["critical_parameters"],
                    "top_recommendations": result["report"]["recommendations"][:3] if result["report"]["recommendations"] else []
                }
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating robustness report: {e}")
        raise HTTPException(status_code=500, detail=f"Robustness report generation failed: {str(e)}")


@router.get("/perturbation-types", summary="Get Available Perturbation Types")
async def get_perturbation_types():
    """
    Get information about available perturbation types and their characteristics.
    """
    return {
        "success": True,
        "perturbation_types": {
            "gaussian": {
                "description": "Gaussian (normal) distribution perturbation",
                "use_case": "Most common for continuous parameters",
                "parameters": ["mean", "std_dev"],
                "characteristics": "Symmetric, bell-shaped distribution"
            },
            "uniform": {
                "description": "Uniform distribution perturbation",
                "use_case": "When all values in range are equally likely",
                "parameters": ["min_value", "max_value"],
                "characteristics": "Flat distribution across range"
            },
            "log_normal": {
                "description": "Log-normal distribution perturbation",
                "use_case": "For parameters that are naturally log-distributed",
                "parameters": ["log_mean", "log_std_dev"],
                "characteristics": "Skewed distribution, always positive"
            },
            "systematic": {
                "description": "Systematic perturbation with fixed steps",
                "use_case": "For discrete or categorical parameters",
                "parameters": ["step_size", "range"],
                "characteristics": "Discrete values at regular intervals"
            },
            "correlated": {
                "description": "Correlated perturbation considering parameter relationships",
                "use_case": "When parameters are not independent",
                "parameters": ["correlation_matrix"],
                "characteristics": "Maintains parameter correlations"
            }
        }
    }


@router.get("/sensitivity-methods", summary="Get Available Sensitivity Analysis Methods")
async def get_sensitivity_methods():
    """
    Get information about available sensitivity analysis methods and their applications.
    """
    return {
        "success": True,
        "sensitivity_methods": {
            "sobol": {
                "description": "Sobol indices for global sensitivity analysis",
                "use_case": "Comprehensive sensitivity analysis with interactions",
                "advantages": "Captures parameter interactions, provides confidence intervals",
                "computational_cost": "High",
                "interpretation": "Higher index = more sensitive parameter"
            },
            "morris": {
                "description": "Morris screening method",
                "use_case": "Quick screening of parameter importance",
                "advantages": "Fast, good for many parameters",
                "computational_cost": "Low",
                "interpretation": "Higher index = more sensitive parameter"
            },
            "fast": {
                "description": "Fourier Amplitude Sensitivity Test",
                "use_case": "Efficient sensitivity analysis",
                "advantages": "Good balance of speed and accuracy",
                "computational_cost": "Medium",
                "interpretation": "Higher index = more sensitive parameter"
            },
            "delta_moment": {
                "description": "Delta moment-based sensitivity analysis",
                "use_case": "When output distribution shape matters",
                "advantages": "Captures distribution changes",
                "computational_cost": "Medium",
                "interpretation": "Higher index = more impact on output distribution"
            },
            "correlation": {
                "description": "Correlation-based sensitivity analysis",
                "use_case": "Quick linear sensitivity assessment",
                "advantages": "Very fast, simple interpretation",
                "computational_cost": "Very Low",
                "interpretation": "Higher absolute correlation = more sensitive parameter"
            }
        }
    }


@router.get("/health", summary="Health Check")
async def health_check():
    """Check if the perturbation engine service is healthy"""
    return {
        "success": True,
        "service": "PerturbationEngine",
        "status": "healthy",
        "available_perturbation_types": 5,
        "available_sensitivity_methods": 5,
        "supported_distributions": ["gaussian", "uniform", "log_normal", "systematic", "correlated"]
    }
