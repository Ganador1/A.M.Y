"""
Router de Torneo de Hipótesis - Ranking y Competencia de Hipótesis Científicas

Módulo FastAPI para ranking competitivo de hipótesis científicas mediante torneos.
Proporciona endpoints para evaluación comparativa y ranking de hipótesis basado
en criterios científicos, evidencia y potencial de impacto.

Capacidades principales:
- Ranking competitivo: evaluación comparativa de múltiples hipótesis
- Sistema de torneos: competición estructurada entre hipótesis
- Evaluación por criterios: ranking basado en evidencia, plausibilidad y novedad
- Soporte batch: procesamiento eficiente de múltiples hipótesis
- Resultados estructurados: rankings claros con justificaciones

Catálogo de Endpoints:
- POST /hypothesis-tournament/rank: Ranking competitivo de hipótesis por criterios científicos

Dependencias:
- hypothesis_tournament_service: Servicio central de ranking y competición de hipótesis
- FastAPI APIRouter: Framework para definición de rutas
- typing: Anotaciones de tipos para Python

Uso del Servicio:
    El router permite evaluación comparativa sistemática de hipótesis científicas,
    facilitando la identificación de las hipótesis más prometedoras mediante
    competición estructurada y criterios de evaluación objetivos.
"""

from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.hypothesis_tournament_service import hypothesis_tournament_service

router = APIRouter(prefix="/hypothesis-tournament", tags=["hypothesis-tournament"])

@router.post("/rank")
def rank(hypotheses: List[Dict[str, Any]]):
    return hypothesis_tournament_service.rank(hypotheses)
