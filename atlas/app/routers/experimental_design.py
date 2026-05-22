"""
Router de Diseño Experimental - Asistencia Estadística y Planificación Científica

Módulo FastAPI para asistencia en diseño experimental y planificación estadística.
Proporciona herramientas integrales para diseñar experimentos óptimos, calcular tamaños
de muestra y asegurar validez estadística en diversos dominios de investigación.

Capacidades principales:
- Diseño experimental completo: análisis de poder y evaluación de viabilidad
- Diseño experimental rápido: prototipado rápido con parámetros simplificados
- Cálculo de tamaño de muestra: análisis de poder estadístico detallado
- Plantillas específicas por dominio: recomendaciones adaptadas a áreas de investigación
- Monitoreo de salud: estado del servicio y expertise por dominio
- Evaluación de riesgos: análisis de viabilidad y recomendaciones alternativas
- Optimización de recursos: diseño eficiente considerando restricciones presupuestarias

Catálogo de Endpoints:
- POST /design-experiment: Diseño experimental completo con análisis integral
- POST /quick-design: Diseño experimental simplificado para necesidades básicas
- GET /design-types: Tipos de diseño experimental soportados y fases de estudio
- GET /domain-templates: Plantillas de diseño específicas por dominio de investigación
- POST /sample-size-calculator: Cálculos independientes de tamaño de muestra
- GET /health: Estado de salud del servicio y expertise por dominio

Dependencias:
- ExperimentalDesignAssistantService: Servicio central de diseño y análisis
- numpy: Cálculos estadísticos y matemáticos
- pydantic: Validación de requests y responses
- ResearchObjective/ResourceConstraints/StatisticalRequirements: Modelos de dominio
- ExperimentType/StudyPhase: Tipos de experimento y fases de estudio

Uso del Servicio:
    Todos los endpoints aceptan requests JSON y retornan recomendaciones estructuradas
    de diseño experimental. El endpoint de diseño completo proporciona análisis integral
    incluyendo análisis de poder, evaluación de riesgos y opciones de diseño alternativas.
    Los cálculos de tamaño de muestra consideran tasas de abandono y requisitos estadísticos.
"""

import numpy as np
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from app.services.experimental_design_service import (
from app.exceptions.domain.biology import BiologyError
    ExperimentalDesignAssistantService,
    ResearchObjective,
    ResourceConstraints,
    StatisticalRequirements,
    ExperimentType,
    StudyPhase
)

# Initialize router
router = APIRouter()

# Initialize service
experimental_design_service = ExperimentalDesignAssistantService()

class ResearchObjectiveRequest(BaseModel):
    """Request model for research objective"""
    title: str = Field(..., description="Research objective title")
    description: str = Field(..., description="Detailed description")
    primary_outcome: str = Field(..., description="Primary outcome measure")
    secondary_outcomes: List[str] = Field(default=[], description="Secondary outcome measures")
    domain: str = Field(..., description="Research domain")
    hypothesis: str = Field(..., description="Research hypothesis")
    effect_size_expected: float = Field(..., ge=0.0, le=2.0, description="Expected effect size")
    clinical_significance: Optional[float] = Field(None, description="Clinical significance threshold")
    priority: int = Field(default=1, ge=1, le=5, description="Priority level (1=highest, 5=lowest)")

class ResourceConstraintsRequest(BaseModel):
    """Request model for resource constraints"""
    budget: Optional[float] = Field(None, ge=0, description="Available budget")
    time_months: Optional[int] = Field(None, ge=1, le=120, description="Available time in months")
    max_participants: Optional[int] = Field(None, ge=1, description="Maximum number of participants")
    available_equipment: List[str] = Field(default=[], description="Available equipment")
    staff_expertise: List[str] = Field(default=[], description="Staff expertise areas")
    ethical_approvals: List[str] = Field(default=[], description="Obtained ethical approvals")
    regulatory_requirements: List[str] = Field(default=[], description="Regulatory requirements")

class StatisticalRequirementsRequest(BaseModel):
    """Request model for statistical requirements"""
    alpha: float = Field(default=0.05, ge=0.001, le=0.1, description="Type I error rate")
    power: float = Field(default=0.80, ge=0.5, le=0.99, description="Statistical power")
    beta: float = Field(default=0.20, ge=0.01, le=0.5, description="Type II error rate")
    effect_size: Optional[float] = Field(None, ge=0.0, le=2.0, description="Expected effect size")
    variance_estimate: Optional[float] = Field(None, ge=0.0, description="Variance estimate")
    correlation_expected: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Expected correlation")
    dropout_rate: float = Field(default=0.15, ge=0.0, le=0.5, description="Expected dropout rate")
    interim_analyses: int = Field(default=0, ge=0, le=5, description="Number of interim analyses")
    multiple_comparisons: bool = Field(default=False, description="Multiple comparisons correction needed")

class ExperimentDesignRequest(BaseModel):
    """Request model for experimental design"""
    research_objectives: List[ResearchObjectiveRequest] = Field(..., description="Research objectives (at least 1 required)")
    resource_constraints: ResourceConstraintsRequest = Field(..., description="Resource constraints")
    statistical_requirements: Optional[StatisticalRequirementsRequest] = Field(None, description="Statistical requirements")
    design_preferences: Optional[Dict[str, Any]] = Field(default={}, description="Design preferences")

class ExperimentDesignResponse(BaseModel):
    """Response model for experimental design"""
    id: str
    title: str
    design_type: str
    study_phase: str
    total_sample_size: int
    duration_months: int
    estimated_cost: float
    feasibility_score: float
    power_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    alternatives: List[str]
    created_at: str

class QuickDesignRequest(BaseModel):
    """Request model for quick experimental design"""
    research_title: str = Field(..., description="Research title")
    domain: str = Field(..., description="Research domain")
    primary_outcome: str = Field(..., description="Primary outcome")
    hypothesis: str = Field(..., description="Research hypothesis")
    expected_effect_size: float = Field(default=0.5, ge=0.1, le=1.0, description="Expected effect size")
    available_participants: Optional[int] = Field(None, ge=10, description="Available participants")
    budget: Optional[float] = Field(None, ge=1000, description="Available budget")
    time_months: Optional[int] = Field(None, ge=1, le=60, description="Available time")

@router.post("/design-experiment", response_model=ExperimentDesignResponse)
async def design_experiment(
    request: ExperimentDesignRequest,
    background_tasks: BackgroundTasks
):
    """
    Design optimal experiment based on research objectives and constraints
    
    This endpoint analyzes research objectives and available resources to create
    an optimal experimental design with statistical power analysis, feasibility
    assessment, risk evaluation, and detailed recommendations.
    """
    try:
        # Convert request models to service models
        objectives = [
            ResearchObjective(
                id=f"obj_{i+1}",
                title=obj.title,
                description=obj.description,
                primary_outcome=obj.primary_outcome,
                secondary_outcomes=obj.secondary_outcomes,
                domain=obj.domain,
                hypothesis=obj.hypothesis,
                effect_size_expected=obj.effect_size_expected,
                clinical_significance=obj.clinical_significance,
                priority=obj.priority
            )
            for i, obj in enumerate(request.research_objectives)
        ]
        
        constraints = ResourceConstraints(
            budget=request.resource_constraints.budget,
            time_months=request.resource_constraints.time_months,
            max_participants=request.resource_constraints.max_participants,
            available_equipment=request.resource_constraints.available_equipment,
            staff_expertise=request.resource_constraints.staff_expertise,
            ethical_approvals=request.resource_constraints.ethical_approvals,
            regulatory_requirements=request.resource_constraints.regulatory_requirements
        )
        
        stat_req = None
        if request.statistical_requirements:
            stat_req = StatisticalRequirements(
                alpha=request.statistical_requirements.alpha,
                power=request.statistical_requirements.power,
                beta=request.statistical_requirements.beta,
                effect_size=request.statistical_requirements.effect_size,
                variance_estimate=request.statistical_requirements.variance_estimate,
                correlation_expected=request.statistical_requirements.correlation_expected,
                dropout_rate=request.statistical_requirements.dropout_rate,
                interim_analyses=request.statistical_requirements.interim_analyses,
                multiple_comparisons=request.statistical_requirements.multiple_comparisons
            )
        
        # Design experiment
        design = await experimental_design_service.design_experiment(
            research_objectives=objectives,
            resource_constraints=constraints,
            statistical_requirements=stat_req,
            design_preferences=request.design_preferences
        )
        
        # Convert to response model
        return ExperimentDesignResponse(
            id=design.id,
            title=design.title,
            design_type=design.design_type.value,
            study_phase=design.study_phase.value,
            total_sample_size=design.total_sample_size,
            duration_months=design.duration_months,
            estimated_cost=design.estimated_cost,
            feasibility_score=design.feasibility_score,
            power_analysis=design.power_analysis,
            risk_assessment=design.risk_assessment,
            recommendations=design.recommendations,
            alternatives=design.alternatives,
            created_at=design.created_at.isoformat()
        )
        
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Failed to design experiment: {str(e)}")

@router.post("/quick-design")
async def quick_design_experiment(request: QuickDesignRequest):
    """
    Generate quick experimental design based on minimal inputs
    
    This endpoint provides a simplified interface for generating basic
    experimental designs with default parameters and quick recommendations.
    """
    try:
        # Create simplified research objective
        objective = ResearchObjective(
            id="quick_obj_1",
            title=request.research_title,
            description=f"Quick design for {request.research_title}",
            primary_outcome=request.primary_outcome,
            secondary_outcomes=[],
            domain=request.domain,
            hypothesis=request.hypothesis,
            effect_size_expected=request.expected_effect_size
        )
        
        # Create basic constraints
        constraints = ResourceConstraints(
            budget=request.budget,
            time_months=request.time_months,
            max_participants=request.available_participants
        )
        
        # Use default statistical requirements
        stat_req = StatisticalRequirements()
        
        # Design experiment
        design = await experimental_design_service.design_experiment(
            research_objectives=[objective],
            resource_constraints=constraints,
            statistical_requirements=stat_req
        )
        
        # Return simplified response
        return {
            "design_id": design.id,
            "design_type": design.design_type.value,
            "sample_size": design.total_sample_size,
            "duration_months": design.duration_months,
            "estimated_cost": design.estimated_cost,
            "feasibility_score": design.feasibility_score,
            "key_recommendations": design.recommendations[:5],  # Top 5 recommendations
            "power": design.power_analysis.get("primary_analysis", {}).get("power", 0.8),
            "groups": len(design.experimental_groups),
            "status": "feasible" if design.feasibility_score > 0.7 else "challenging"
        }
        
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create quick design: {str(e)}")

@router.get("/design-types")
async def get_supported_design_types():
    """Get list of supported experimental design types"""
    return {
        "experiment_types": [
            {
                "type": design_type.value,
                "name": design_type.value.replace("_", " ").title(),
                "description": f"Description for {design_type.value}"
            }
            for design_type in ExperimentType
        ],
        "study_phases": [
            {
                "phase": phase.value,
                "name": phase.value.replace("_", " ").title(),
                "description": f"Description for {phase.value}"
            }
            for phase in StudyPhase
        ]
    }

@router.get("/domain-templates")
async def get_domain_templates():
    """Get experimental design templates by research domain"""
    try:
        # Get domain expertise from service
        health_status = await experimental_design_service.get_design_health_status()
        
        return {
            "domains": health_status["domain_expertise"],
            "templates": {
                domain: {
                    "common_designs": ["randomized_controlled", "factorial", "observational"],
                    "typical_duration_months": 12,
                    "recommended_sample_size": {"small": 50, "medium": 200, "large": 500},
                    "key_considerations": [
                        "statistical_power",
                        "ethical_requirements", 
                        "regulatory_compliance"
                    ]
                }
                for domain in health_status["domain_expertise"]
            }
        }
        
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Failed to get domain templates: {str(e)}")

class SampleSizeRequest(BaseModel):
    """Request model for sample size calculation"""
    effect_size: float = Field(..., ge=0.1, le=2.0, description="Expected effect size")
    alpha: float = Field(default=0.05, ge=0.001, le=0.1, description="Type I error rate")
    power: float = Field(default=0.80, ge=0.5, le=0.99, description="Statistical power")
    design_type: str = Field(default="randomized_controlled", description="Experimental design type")
    dropout_rate: float = Field(default=0.15, ge=0.0, le=0.5, description="Expected dropout rate")

@router.post("/sample-size-calculator")
async def calculate_sample_size(request: SampleSizeRequest):
    """
    Calculate required sample size for given parameters
    
    This endpoint provides a standalone sample size calculator that can be used
    to estimate required participants before full experimental design.
    """
    try:
        # Simple sample size calculation
        z_alpha = 1.96 if request.alpha == 0.05 else (2.576 if request.alpha == 0.01 else 1.645)
        z_beta = 0.84 if request.power == 0.8 else (1.28 if request.power == 0.9 else 0.67)
        
        # Basic sample size calculation
        n_per_group = ((z_alpha + z_beta) ** 2) * 2 / (request.effect_size ** 2)
        n_per_group = int(np.ceil(n_per_group))
        
        # Adjust for dropout
        n_adjusted = int(np.ceil(n_per_group / (1 - request.dropout_rate)))
        
        # Total sample size (assuming 2 groups by default)
        groups = 2 if request.design_type in {"randomized_controlled", "case_control"} else 3
        total_n = n_adjusted * groups
        
        return {
            "sample_size_per_group": n_per_group,
            "sample_size_adjusted": n_adjusted,
            "total_sample_size": total_n,
            "number_of_groups": groups,
            "parameters_used": {
                "effect_size": request.effect_size,
                "alpha": request.alpha,
                "power": request.power,
                "dropout_rate": request.dropout_rate,
                "design_type": request.design_type
            },
            "recommendations": [
                f"Each group needs {n_adjusted} participants",
                f"Total study needs {total_n} participants",
                f"Power analysis based on {request.power:.0%} power and {request.alpha} alpha level",
                "Consider pilot study to validate effect size assumption"
            ]
        }
        
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Sample size calculation failed: {str(e)}")

@router.get("/health")
async def get_health_status():
    """Get health status of experimental design assistant service"""
    try:
        return await experimental_design_service.get_design_health_status()
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# End of router module
