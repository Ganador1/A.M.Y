"""
Router del Kit de Herramientas Experimentales - Herramientas Experimentales del Dominio

Módulo FastAPI que proporciona acceso a herramientas experimentales específicas por dominio
para ejecutar simulaciones, análisis y validaciones científicas en la plataforma AXIOM.

Capacidades principales:
- Ejecución de experimentos: herramientas especializadas por dominio científico
- Validación estadística rigurosa: análisis de poder, detección de outliers y correcciones
- Experimentos por lotes: ejecución comparativa de múltiples experimentos
- Verificación de reproducibilidad: comparación entre experimentos originales y réplicas
- Endpoints rápidos: acceso simplificado a herramientas comunes
- Monitoreo de salud: estado del servicio y capacidades disponibles
- Documentación de ejemplos: casos de uso para diferentes dominios

Catálogo de Endpoints:
- GET /api/v1/experimental/capabilities: Lista de capacidades disponibles por dominio
- POST /api/v1/experimental/run: Ejecución de experimento único con herramienta específica
- POST /api/v1/experimental/batch: Ejecución de múltiples experimentos con comparación
- POST /api/v1/experimental/validate: Validación estadística completa de resultados
- POST /api/v1/experimental/reproducibility: Verificación de reproducibilidad experimental
- POST /api/v1/experimental/quick/molecular-properties: Cálculo rápido de propiedades moleculares
- POST /api/v1/experimental/quick/protein-fold: Predicción rápida de estructura proteica
- GET /api/v1/experimental/health: Health check del kit de herramientas
- GET /api/v1/experimental/examples: Ejemplos de uso para diferentes herramientas

Dependencias:
- ExperimentalToolkitHub: Hub central de herramientas experimentales
- ExperimentalValidator: Servicio de validación estadística y reproducibilidad
- ExperimentalResult/ExperimentalData: Modelos de datos experimentales
- StatisticalTest/MultipleTestingCorrection/OutlierMethod: Métodos estadísticos
- numpy: Computación numérica para análisis estadísticos
- require_scopes: Sistema de autorización por scopes de seguridad

Uso del Servicio:
    El router permite acceso a herramientas especializadas para diferentes dominios
    científicos incluyendo biología, química y física. Soporta ejecución individual
    y por lotes de experimentos, con validación estadística completa y verificación
    de reproducibilidad. Los endpoints rápidos facilitan el acceso a herramientas
    comunes sin configuración compleja.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
import numpy as np

from app.security import require_scopes
from app.domains.engineering.services.experimental_toolkit_hub import (
    get_experimental_hub,
    ExperimentalResult,
    ExperimentalToolkitHub
)
from app.exceptions.domain.biology import BiologyError
from app.domains.engineering.services.experimental_validator import (
    get_experimental_validator,
    ExperimentalData,
    ValidationResult,
    StatisticalTest,
    MultipleTestingCorrection,
    OutlierMethod
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router with authentication
router = APIRouter(
    prefix="/api/v1/experimental",
    tags=["experimental", "toolkit"],
    dependencies=[Depends(require_scopes(["experimental"]))]
)


class ExperimentRequest(BaseModel):
    """Request model for running an experiment"""
    domain: str = Field(..., description="Scientific domain (biology, chemistry, physics)")
    tool_name: str = Field(..., description="Name of the experimental tool")
    method: str = Field(..., description="Specific method to use")
    inputs: Dict[str, Any] = Field(..., description="Tool-specific input parameters")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "domain": "chemistry",
                "tool_name": "molecular_properties",
                "method": "RDKit",
                "inputs": {
                    "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"
                }
            }
        }
    )


class ValidationRequest(BaseModel):
    """Request model for validating experimental results"""
    experiment_id: str = Field(..., description="ID of the experiment to validate")
    groups: Dict[str, List[float]] = Field(..., description="Experimental groups and measurements")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    hypotheses: Optional[List[Dict[str, Any]]] = Field(default=[], description="Hypotheses to test")
    alpha: float = Field(default=0.05, ge=0.001, le=0.1, description="Significance level")
    power_threshold: float = Field(default=0.8, ge=0.5, le=0.99, description="Desired statistical power")
    tests: Optional[List[str]] = Field(default=None, description="Statistical tests to perform")
    correction: str = Field(default="fdr_bh", description="Multiple testing correction method")
    outlier_methods: Optional[List[str]] = Field(default=None, description="Outlier detection methods")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "experiment_id": "exp_20250117_123456",
                "groups": {
                    "control": [1.2, 1.4, 1.1, 1.3, 1.5],
                    "treatment": [2.1, 2.3, 2.0, 2.2, 2.4]
                },
                "alpha": 0.05,
                "power_threshold": 0.8,
                "tests": ["t_test", "mann_whitney"],
                "correction": "bonferroni"
            }
        }
    )


class BatchExperimentRequest(BaseModel):
    """Request for running multiple experiments"""
    experiments: List[ExperimentRequest] = Field(..., description="List of experiments to run")
    compare_results: bool = Field(default=True, description="Whether to compare results")


class ReproducibilityRequest(BaseModel):
    """Request for validating reproducibility"""
    original_experiment_id: str = Field(..., description="Original experiment ID")
    original_groups: Dict[str, List[float]] = Field(..., description="Original measurements")
    replication_experiment_id: str = Field(..., description="Replication experiment ID")
    replication_groups: Dict[str, List[float]] = Field(..., description="Replication measurements")
    tolerance: float = Field(default=0.1, ge=0.0, le=0.5, description="Tolerance for effect size agreement")


@router.get("/capabilities", dependencies=[Depends(require_scopes(["experimental:read"]))])
async def list_capabilities() -> Dict[str, List[Dict[str, Any]]]:
    """
    List all available experimental capabilities by domain

    Returns a dictionary mapping domains to their available tools and methods.
    """
    try:
        hub = await get_experimental_hub()
        capabilities = await hub.list_all_capabilities()

        return {
            "status": "success",
            "domains": list(capabilities.keys()),
            "total_tools": sum(len(tools) for tools in capabilities.values()),
            "capabilities": capabilities
        }

    except BiologyError as e:
        logger.error(f"Error listing capabilities: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing capabilities: {str(e)}"
        )


@router.post("/run", dependencies=[Depends(require_scopes(["experimental:execute"]))])
async def run_experiment(request: ExperimentRequest) -> Dict[str, Any]:
    """
    Run a single experiment using the specified tool

    Executes an experiment in the specified domain using the requested tool
    and method with the provided inputs.
    """
    try:
        hub = await get_experimental_hub()

        # Execute experiment
        result = await hub.execute_experiment(
            domain=request.domain,
            tool_name=request.tool_name,
            method=request.method,
            inputs=request.inputs
        )

        # Convert result to dict
        return {
            "status": "success" if not result.errors else "error",
            "experiment_id": result.experiment_id,
            "domain": result.domain,
            "tool_name": result.tool_name,
            "method": result.method,
            "outputs": result.outputs,
            "metrics": result.metrics,
            "logs": result.logs,
            "errors": result.errors,
            "duration_seconds": result.duration_seconds,
            "timestamp": result.timestamp.isoformat()
        }

    except BiologyError as e:
        logger.error(f"Error running experiment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running experiment: {str(e)}"
        )


@router.post("/batch", dependencies=[Depends(require_scopes(["experimental:execute"]))])
async def run_batch_experiments(request: BatchExperimentRequest) -> Dict[str, Any]:
    """
    Run multiple experiments in batch

    Executes multiple experiments and optionally compares their results.
    """
    try:
        hub = await get_experimental_hub()

        # Convert requests to format expected by hub
        experiments = [
            {
                "domain": exp.domain,
                "tool_name": exp.tool_name,
                "method": exp.method,
                "inputs": exp.inputs
            }
            for exp in request.experiments
        ]

        # Run comparative experiment
        comparison = await hub.run_comparative_experiment(experiments)

        return {
            "status": "success",
            "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "comparison": comparison
        }

    except BiologyError as e:
        logger.error(f"Error running batch experiments: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running batch experiments: {str(e)}"
        )


@router.post("/validate", dependencies=[Depends(require_scopes(["experimental:validate"]))])
async def validate_results(request: ValidationRequest) -> Dict[str, Any]:
    """
    Validate experimental results with rigorous statistical methods

    Performs comprehensive statistical validation including power analysis,
    outlier detection, assumption checking, and multiple testing corrections.
    """
    try:
        validator = get_experimental_validator()

        # Create experimental data object
        data = ExperimentalData(
            experiment_id=request.experiment_id,
            groups={k: np.array(v) for k, v in request.groups.items()},
            metadata=request.metadata,
            hypotheses=request.hypotheses,
            alpha=request.alpha,
            power_threshold=request.power_threshold
        )

        # Parse test types
        tests = None
        if request.tests:
            tests = [StatisticalTest[t.upper()] for t in request.tests]

        # Parse correction method
        correction = MultipleTestingCorrection[request.correction.upper()]

        # Parse outlier methods
        outlier_methods = None
        if request.outlier_methods:
            outlier_methods = [OutlierMethod[m.upper()] for m in request.outlier_methods]

        # Run validation
        result = await validator.validate_experiment(
            data=data,
            tests=tests,
            correction=correction,
            outlier_methods=outlier_methods
        )

        # Convert result to dict
        return {
            "status": "success",
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
            "timestamp": result.timestamp.isoformat()
        }

    except BiologyError as e:
        logger.error(f"Error validating results: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating results: {str(e)}"
        )


@router.post("/reproducibility", dependencies=[Depends(require_scopes(["experimental:validate"]))])
async def check_reproducibility(request: ReproducibilityRequest) -> Dict[str, Any]:
    """
    Check reproducibility between original and replication experiments

    Compares effect sizes, statistical significance, and other metrics
    to determine if results are successfully reproduced.
    """
    try:
        validator = get_experimental_validator()

        # Create data objects
        original_data = ExperimentalData(
            experiment_id=request.original_experiment_id,
            groups={k: np.array(v) for k, v in request.original_groups.items()}
        )

        replication_data = ExperimentalData(
            experiment_id=request.replication_experiment_id,
            groups={k: np.array(v) for k, v in request.replication_groups.items()}
        )

        # Validate reproducibility
        report = await validator.validate_reproducibility(
            original_data=original_data,
            replication_data=replication_data,
            tolerance=request.tolerance
        )

        return {
            "status": "success",
            "reproducibility_report": report
        }

    except BiologyError as e:
        logger.error(f"Error checking reproducibility: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking reproducibility: {str(e)}"
        )


# Quick experiment endpoints for common use cases

@router.post("/quick/molecular-properties", dependencies=[Depends(require_scopes(["experimental:execute"]))])
async def quick_molecular_properties(smiles: str) -> Dict[str, Any]:
    """
    Quick endpoint to calculate molecular properties from SMILES
    """
    request = ExperimentRequest(
        domain="chemistry",
        tool_name="molecular_properties",
        method="RDKit",
        inputs={"smiles": smiles}
    )
    return await run_experiment(request)


@router.post("/quick/protein-fold", dependencies=[Depends(require_scopes(["experimental:execute"]))])
async def quick_protein_fold(sequence: str) -> Dict[str, Any]:
    """
    Quick endpoint to predict protein structure from sequence
    """
    request = ExperimentRequest(
        domain="biology",
        tool_name="protein_structure_prediction",
        method="ESMFold",
        inputs={"protein_sequence": sequence}
    )
    return await run_experiment(request)


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for experimental toolkit
    """
    try:
        hub = await get_experimental_hub()
        toolkit_count = len(hub.toolkits)

        return {
            "status": "healthy",
            "service": "experimental_toolkit",
            "toolkits_loaded": toolkit_count,
            "message": f"Experimental toolkit operational with {toolkit_count} domains"
        }
    except BiologyError as e:
        return {
            "status": "unhealthy",
            "service": "experimental_toolkit",
            "error": str(e)
        }


# Example usage documentation
@router.get("/examples")
async def get_examples() -> Dict[str, Any]:
    """
    Get example requests for different experimental tools
    """
    return {
        "molecular_dynamics": {
            "domain": "biology",
            "tool_name": "molecular_dynamics",
            "method": "OpenMM",
            "inputs": {
                "pdb_file": "/path/to/protein.pdb",
                "temperature": 300,
                "pressure": 1.0,
                "time_ns": 10.0,
                "force_field": "amber14-all.xml"
            }
        },
        "chemical_properties": {
            "domain": "chemistry",
            "tool_name": "molecular_properties",
            "method": "RDKit",
            "inputs": {
                "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O"
            }
        },
        "gene_expression": {
            "domain": "biology",
            "tool_name": "gene_expression_analysis",
            "method": "scanpy",
            "inputs": {
                "count_matrix": "[[1,2,3],[4,5,6]]",
                "metadata": {
                    "gene_names": ["GENE1", "GENE2", "GENE3"],
                    "cell_names": ["CELL1", "CELL2"]
                }
            }
        },
        "quantum_simulation": {
            "domain": "physics",
            "tool_name": "quantum_simulation",
            "method": "particle_in_box",
            "inputs": {
                "box_length": 1.0,
                "mass": 9.109e-31,
                "n_levels": 5
            }
        }
    }
