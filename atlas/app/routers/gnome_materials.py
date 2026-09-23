"""
Router de Descubrimiento de Materiales GNOME - Predicción y Descubrimiento de Materiales

Módulo FastAPI para descubrimiento de materiales y predicción de propiedades usando métodos GNOME.
Proporciona endpoints REST API para el diseño racional de materiales y ciencia de materiales computacional.

Capacidades principales:
- Sugerencia de candidatos: recomendación de materiales basada en propiedades objetivo
- Predicción de propiedades: estimación de propiedades para fórmulas químicas
- Flujos de trabajo de descubrimiento: procesos automatizados de diseño de materiales
- Integración con ciencia de materiales computacional
- Cribado de alto rendimiento: evaluación rápida de múltiples candidatos

Catálogo de Endpoints:
- POST /api/gnome/suggest-candidates: Sugerencia de candidatos de materiales basada en propiedades objetivo
- POST /api/gnome/predict-properties: Predicción de propiedades para fórmulas químicas específicas

Dependencias:
- GNOMEMaterialsService: Servicio central de descubrimiento de materiales GNOME
- pydantic BaseModel: Modelos de validación para requests
- FastAPI APIRouter: Framework para definición de rutas
- HTTPException: Manejo de errores HTTP

Uso del Servicio:
    El router permite el diseño racional de materiales mediante predicción
    computacional de propiedades. Soporta tanto sugerencias basadas en objetivos
    específicos como predicciones para fórmulas químicas concretas, facilitando
    el descubrimiento y optimización de nuevos materiales.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.domains.chemistry.services.gnome_materials_service import GNOMEMaterialsService


router = APIRouter(prefix="/api/gnome", tags=["GNOME"])
service = GNOMEMaterialsService()


class SuggestPayload(BaseModel):
    target: str = Field(..., description="Target property or goal, e.g. 'high thermal conductivity'")
    top_n: Optional[int] = Field(default=3, ge=1, le=20)


@router.post("/suggest-candidates")
async def suggest_candidates(payload: SuggestPayload):
    res = service.suggest_candidates(payload.model_dump())
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


class PredictPayload(BaseModel):
    formula: str = Field(..., description="Chemical formula, e.g. LiFePO4")


@router.post("/predict-properties")
async def predict_properties(payload: PredictPayload):
    res = service.predict_properties(payload.model_dump())
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res
