"""
DNABERT-2 Genomics Router

Router FastAPI para análisis de secuencias de DNA utilizando métodos inspirados en DNABERT-2.
Proporciona endpoints REST API para codificación y tokenización de secuencias de DNA,
predicción de motivos y reconocimiento de patrones, clasificación de regiones promotoras,
flujos de trabajo de análisis de secuencias genómicas e integración con pipelines bioinformáticos.

Capacidades principales:
- Codificación avanzada de secuencias de DNA con tokenización k-mer
- Predicción de motivos funcionales y reconocimiento de patrones regulatorios
- Clasificación automática de regiones promotoras y elementos cis-regulatorios
- Análisis de secuencias genómicas con modelos de aprendizaje profundo
- Flujos de trabajo integrados para análisis genómico de alto rendimiento
- Integración seamless con pipelines bioinformáticos existentes
- Análisis de conservación de secuencias y evolución molecular
- Predicción de sitios de unión a factores de transcripción
- Análisis de estructura secundaria de RNA y elementos reguladores
- Procesamiento por lotes de múltiples secuencias genómicas

Endpoints disponibles:
- POST /encode-sequence: Codificar secuencia de DNA con parámetros configurables
- POST /predict-motifs: Predecir motivos funcionales en secuencias de DNA
- POST /classify-promoter: Clasificar regiones promotoras y elementos reguladores
- POST /analyze-sequence: Análisis comprehensivo de secuencias genómicas
- GET /capabilities: Capacidades del servicio DNABERT-2
- GET /health: Verificación del estado del servicio
- POST /batch-analyze: Análisis por lotes de múltiples secuencias

Dependencias:
- DNABERT2GenomicsService: Servicio principal de genómica DNABERT-2
- SequencePayload: Modelo de carga de secuencia de DNA
- AnalysisRequest: Solicitud de análisis genómico

Uso típico:
    from app.routers.dnabert2 import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /api/dnabert2
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.domains.biology.services.dnabert2_service import DNABERT2GenomicsService


router = APIRouter(prefix="/api/dnabert2", tags=["DNABERT2"])
service = DNABERT2GenomicsService()


class SequencePayload(BaseModel):
    """Payload model for DNA sequence inputs.

    This model defines the structure for DNA sequence data, including
    the sequence itself and optional k-mer size.
    """
    sequence: str = Field(..., description="DNA sequence (A,C,G,T,N)")
    k: Optional[int] = Field(default=None, description="k-mer size (default=6)")


@router.post("/encode-sequence")
async def encode_sequence(payload: SequencePayload):
    """Encode a DNA sequence using DNABERT-2 inspired methods.

    This endpoint processes the DNA sequence and returns its encoding.

    Args:
        payload: The sequence payload.

    Returns:
        Encoding result.
    """
    res = service.encode_sequence(payload.model_dump())
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.post("/predict-motifs")
async def predict_motifs(payload: SequencePayload):
    """Predict functional motifs in DNA sequences.

    This endpoint analyzes the sequence to predict motifs.

    Args:
        payload: The sequence payload.

    Returns:
        Prediction results.
    """
    res = service.predict_motifs(payload.model_dump())
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.post("/classify-promoter")
async def classify_promoter(payload: SequencePayload):
    """Classify promoter regions in DNA sequences.

    This endpoint classifies promoter regions and regulatory elements.

    Args:
        payload: The sequence payload.

    Returns:
        Classification results.
    """
    res = service.classify_promoter(payload.model_dump())
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res
