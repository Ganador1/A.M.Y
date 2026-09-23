"""
🔬 Evaluación Científica Unificada - Sistema de Puntuación Integral

Este módulo proporciona endpoints para la evaluación comprehensiva y unificada
de hipótesis científicas, utilizando un sistema de puntuación compuesto que
combina múltiples métricas científicas para determinar la calidad, novedad
y robustez de las hipótesis de investigación.

Características principales:
- 📊 **Puntuación compuesta**: Sistema unificado que combina múltiples métricas
- 🆕 **Evaluación de novedad**: Medición de la originalidad científica
- 🔍 **Fuerza de evidencia**: Calidad y robustez de los datos experimentales
- 📈 **Estabilidad**: Medición de la consistencia y reproducibilidad
- 📝 **Análisis de texto**: Procesamiento de lenguaje natural para hipótesis
- 🎯 **Validación automática**: Verificación de parámetros y rangos
- 📋 **Explicaciones detalladas**: Justificación completa de las puntuaciones

Métricas de evaluación:
- **Novedad (Novelty)**: Originalidad y contribución al conocimiento existente
- **Evidencia (Evidence)**: Fortaleza de los datos y métodos experimentales
- **Estabilidad (Stability)**: Consistencia bajo variaciones y condiciones
- **Texto**: Análisis semántico de la formulación de hipótesis

Sistema de puntuación compuesto:
- **Fórmula**: Combinación ponderada de métricas normalizadas
- **Rango**: 0.0 a 1.0 (bajo a alto)
- **Umbrales**: Definición de niveles de calidad (bajo, medio, alto, excelente)
- **Versionado**: Control de versiones de fórmulas de evaluación

El servicio está diseñado como MVP sin persistencia, enfocándose en la evaluación
en tiempo real de hipótesis científicas con métricas objetivas y explicables.

Author: ATLAS Autonomous Laboratory System
Date: ${new Date().toISOString().split('T')[0]}
Version: 4.1
"""

import logging
import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.exceptions.infrastructure.api import APIError
from app.services.scientific_evaluation_service import (
    scientific_evaluation_service, EvaluationInput
)
from app.security import require_scopes

# Configure logging
logger = logging.getLogger(__name__)

# Create router with authentication
router = APIRouter(
    prefix="/api/v1/scientific-evaluation",
    tags=["scientific-evaluation", "hypothesis-validation", "scientific-metrics"],
    dependencies=[Depends(require_scopes(["scientific-evaluation:read"]))]
)

class EvaluationRequest(BaseModel):
    hypothesis_id: Optional[str] = Field(None, description="ID de hipótesis si existe")
    novelty_score: Optional[float] = Field(None, ge=0, le=1)
    evidence_strength: Optional[float] = Field(None, ge=0, le=1)
    stability_score: Optional[float] = Field(None, ge=0, le=1, description="Proxy de robustez")
    text: Optional[str] = None

class EvaluationResponse(BaseModel):
    formula_version: str
    components: dict
    composite_score: float
    explanation: dict

@router.post("/", response_model=EvaluationResponse, dependencies=[Depends(require_scopes(["scientific-evaluation:execute"]))])
async def evaluate_scientific_hypothesis(req: EvaluationRequest) -> EvaluationResponse:
    """
    🔬 Evalúa hipótesis científicas con puntuación compuesta

    Realiza una evaluación comprehensiva de hipótesis científicas utilizando
    un sistema de puntuación compuesto que combina novedad, fuerza de evidencia,
    estabilidad y análisis de texto para determinar la calidad científica.

    Args:
        req: Parámetros de evaluación incluyendo métricas opcionales y texto

    Returns:
        EvaluationResponse: Resultado de evaluación con puntuación compuesta y componentes

    Raises:
        HTTPException: Si hay error en la evaluación o parámetros inválidos

    Example:
        POST /
        {
            "hypothesis_id": "hyp_123",
            "novelty_score": 0.85,
            "evidence_strength": 0.72,
            "stability_score": 0.68,
            "text": "La proteína X interactúa con Y bajo condiciones Z"
        }

    Notas:
    - Al menos una métrica debe ser proporcionada
    - Las puntuaciones deben estar en rango [0.0, 1.0]
    - El análisis de texto es opcional pero recomendado
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        provided_metrics = sum([
            req.novelty_score is not None,
            req.evidence_strength is not None,
            req.stability_score is not None,
            req.text is not None and req.text.strip() != ""
        ])

        if provided_metrics == 0:
            logger.warning("🚫 No se proporcionaron métricas para evaluación")
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar al menos una métrica (novelty_score, evidence_strength, stability_score) o texto para evaluación"
            )

        # Validar rangos de métricas
        if req.novelty_score is not None and (req.novelty_score < 0.0 or req.novelty_score > 1.0):
            logger.warning("🚫 Puntuación de novedad fuera de rango: %.3f", req.novelty_score)
            raise HTTPException(
                status_code=400,
                detail="novelty_score debe estar entre 0.0 y 1.0"
            )

        if req.evidence_strength is not None and (req.evidence_strength < 0.0 or req.evidence_strength > 1.0):
            logger.warning("🚫 Fuerza de evidencia fuera de rango: %.3f", req.evidence_strength)
            raise HTTPException(
                status_code=400,
                detail="evidence_strength debe estar entre 0.0 y 1.0"
            )

        if req.stability_score is not None and (req.stability_score < 0.0 or req.stability_score > 1.0):
            logger.warning("🚫 Puntuación de estabilidad fuera de rango: %.3f", req.stability_score)
            raise HTTPException(
                status_code=400,
                detail="stability_score debe estar entre 0.0 y 1.0"
            )

        # Validar texto si se proporciona
        if req.text and len(req.text.strip()) < 10:
            logger.warning("🚫 Texto de hipótesis demasiado corto: %d caracteres", len(req.text))
            raise HTTPException(
                status_code=400,
                detail="Si se proporciona texto, debe tener al menos 10 caracteres"
            )

        logger.info("🔬 Iniciando evaluación científica")
        logger.info("📊 Métricas proporcionadas: novedad=%.3f, evidencia=%.3f, estabilidad=%.3f, texto=%s",
                   req.novelty_score or 0,
                   req.evidence_strength or 0,
                   req.stability_score or 0,
                   "sí" if req.text else "no")

        # Ejecutar evaluación
        result = scientific_evaluation_service.evaluate(EvaluationInput(
            hypothesis_id=req.hypothesis_id,
            novelty_score=req.novelty_score,
            evidence_strength=req.evidence_strength,
            stability_score=req.stability_score,
            text=req.text,
        ))

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Enriquecer respuesta con metadatos
        result_dict = result.dict() if hasattr(result, 'dict') else result
        if isinstance(result_dict, dict):
            result_dict["metadata"] = {
                "execution_time_seconds": execution_time,
                "metrics_provided": provided_metrics,
                "timestamp": datetime.datetime.now().isoformat(),
                "evaluation_type": "scientific_hypothesis"
            }

        logger.info("✅ Evaluación científica completada: puntuación=%.3f (tiempo: %.4fs)",
                   result.composite_score if hasattr(result, 'composite_score') else 0, execution_time)

        return result

    except HTTPException:
        raise
    except APIError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error interno en evaluación científica: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en evaluación: {str(e)}"
        ) from e
