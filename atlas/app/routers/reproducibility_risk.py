"""
⚠️ Servicio de Evaluación de Riesgos de Reproducibilidad Científica

Este módulo proporciona endpoints para evaluar y cuantificar los riesgos asociados
con la reproducibilidad de experimentos científicos, identificando factores que
pueden comprometer la confiabilidad y repetibilidad de resultados de investigación.

Características principales:
- 📊 Evaluación cuantitativa de riesgos de reproducibilidad
- 🔍 Análisis de fortaleza de evidencia experimental
- 📈 Medición de estabilidad de resultados
- 🔒 Evaluación de sensibilidad de datos
- 🔗 Análisis de dependencias y complejidad
- 📋 Reportes detallados de factores de riesgo
- 🎯 Recomendaciones para mejorar reproducibilidad

Factores de riesgo evaluados:
- Fortaleza de evidencia: Calidad y robustez de los datos experimentales
- Estabilidad: Consistencia de resultados bajo variaciones controladas
- Sensibilidad: Impacto de cambios en datos o parámetros
- Dependencias: Complejidad de la cadena de herramientas y librerías

El servicio utiliza algoritmos de machine learning para predecir riesgos potenciales
y proporciona recomendaciones específicas para mitigar problemas de reproducibilidad.

Author: ATLAS Autonomous Laboratory System
Date: ${new Date().toISOString().split('T')[0]}
Version: 4.1
"""

import logging
import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.security import require_scopes
from app.services.reproducibility_risk_service import reproducibility_risk_service
from app.exceptions.domain.biology import BiologyError
from app.types.reproducibility_risk_types import (
    AssessReproducibilityRiskResult,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router with authentication
router = APIRouter(
    prefix="/api/v1/reproducibility-risk",
    tags=["reproducibility", "risk-assessment", "validation"],
    dependencies=[Depends(require_scopes(["reproducibility:read"]))]
)


class RiskAssessmentRequest(BaseModel):
    """Modelo de solicitud para evaluación de riesgos de reproducibilidad"""
    evidence_strength: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Fortaleza de evidencia experimental (0.0-1.0)"
    )
    stability_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Puntuación de estabilidad de resultados (0.0-1.0)"
    )
    data_sensitivity: Optional[str] = Field(
        default=None,
        description="Nivel de sensibilidad de datos",
        examples=["low", "medium", "high", "critical"]
    )
    dependency_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Número de dependencias externas"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "evidence_strength": 0.85,
                "stability_score": 0.72,
                "data_sensitivity": "medium",
                "dependency_count": 12
            }
        }
    )

@router.post("/assess", response_model=Dict[str, Any])
async def assess_reproducibility_risk(request: RiskAssessmentRequest) -> AssessReproducibilityRiskResult:
    """
    ⚠️ Evalúa riesgos de reproducibilidad científica

    Realiza una evaluación comprehensiva de los riesgos asociados con la reproducibilidad
    de un experimento científico, analizando múltiples factores que pueden afectar
    la confiabilidad y repetibilidad de los resultados.

    Args:
        request: Parámetros de evaluación de riesgo con métricas opcionales

    Returns:
        Dict[str, Any]: Resultado de evaluación con puntuación de riesgo y recomendaciones

    Raises:
        HTTPException: Si hay error en la evaluación o parámetros inválidos

    Example:
        POST /assess
        {
            "evidence_strength": 0.85,
            "stability_score": 0.72,
            "data_sensitivity": "medium",
            "dependency_count": 12
        }
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        params_provided = sum([
            request.evidence_strength is not None,
            request.stability_score is not None,
            request.data_sensitivity is not None,
            request.dependency_count is not None
        ])

        if params_provided == 0:
            logger.warning("🚫 No se proporcionaron parámetros para evaluación de riesgo")
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar al menos un parámetro para evaluación"
            )

        # Validar data_sensitivity si se proporciona
        if request.data_sensitivity:
            valid_sensitivities = ["low", "medium", "high", "critical"]
            if request.data_sensitivity.lower() not in valid_sensitivities:
                logger.warning("🚫 Nivel de sensibilidad inválido: %s", request.data_sensitivity)
                raise HTTPException(
                    status_code=400,
                    detail=f"data_sensitivity debe ser uno de: {', '.join(valid_sensitivities)}"
                )

        logger.info("⚠️ Iniciando evaluación de riesgo de reproducibilidad")
        logger.info("📊 Parámetros proporcionados: evidencia=%.3f, estabilidad=%.3f, sensibilidad=%s, dependencias=%s",
                   request.evidence_strength or 0,
                   request.stability_score or 0,
                   request.data_sensitivity or "N/A",
                   request.dependency_count or "N/A")

        # Ejecutar evaluación
        result = reproducibility_risk_service.assess(
            evidence_strength=request.evidence_strength,
            stability_score=request.stability_score,
            data_sensitivity=request.data_sensitivity,
            dependency_count=request.dependency_count,
        )

        if not result.get("success"):
            logger.error("❌ Error en evaluación de riesgo: %s", result.get("error", "Error desconocido"))
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Evaluación de riesgo fallida")
            )

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Enriquecer respuesta con metadatos
        result["metadata"] = {
            "execution_time_seconds": execution_time,
            "parameters_evaluated": params_provided,
            "timestamp": datetime.datetime.now().isoformat(),
            "assessment_type": "reproducibility_risk"
        }

        logger.info("✅ Evaluación de riesgo completada: nivel=%s, puntuación=%.3f (tiempo: %.4fs)",
                   result.get("risk_level", "unknown"), result.get("risk_score", 0), execution_time)

        return result

    except HTTPException:
        raise
    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error interno en evaluación de riesgo: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en evaluación de riesgo: {str(e)}"
        ) from e
