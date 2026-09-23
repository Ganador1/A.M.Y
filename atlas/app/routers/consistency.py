"""
Consistency Validation Router

Router FastAPI para validación comprehensiva de consistencia de texto y verificación
de coherencia semántica en la plataforma de computación científica AXIOM. Proporciona
endpoints REST API para evaluación de calidad de contenido, validación semántica
y flujos de trabajo automatizados de consistencia.

Este router ofrece capacidades avanzadas de verificación de consistencia para:
- Análisis de consistencia de texto contra terminología y conceptos requeridos
- Validación de coherencia semántica para contenido científico y técnico
- Evaluación de calidad de contenido con puntuación y retroalimentación
- Verificación automatizada de consistencia para documentos de investigación y publicaciones
- Validación de consistencia multi-idioma y gestión de terminología
- Verificación de consistencia contextual con conocimiento específico de dominio
- Retroalimentación de consistencia en tiempo real para creación de contenido

El router se integra con ConsistencyCheckerService para proporcionar
a investigadores y creadores de contenido herramientas para asegurar precisión semántica,
consistencia terminológica y calidad de contenido en documentación científica.

Endpoints disponibles:
- POST /consistency/check: Validar consistencia de texto contra términos y conceptos requeridos

Dependencias:
- ConsistencyCheckerService: Validación de consistencia principal y análisis semántico
- NLPTools: Procesamiento de lenguaje natural para análisis de texto y verificación de coherencia
- TerminologyDatabase: Gestión de terminología y conceptos específicos de dominio
- QualityMetrics: Algoritmos de puntuación y evaluación de calidad de contenido
- Logging: Logging comprehensivo para operaciones de validación de consistencia

Uso típico:
    La verificación de consistencia de texto soporta términos requeridos opcionales para validación específica de dominio.
    Los resultados incluyen puntuaciones de consistencia, términos faltantes y métricas de coherencia.
    Los flujos de trabajo automatizados pueden integrar verificación de consistencia en pipelines de contenido.
"""

from fastapi import APIRouter
from app.services.consistency_checker_service import consistency_checker_service
from typing import List, Optional

router = APIRouter(prefix="/consistency", tags=["consistency"])

@router.post("/check")
def check(text: str, required_terms: Optional[List[str]] = None):
    return consistency_checker_service.check(text, required_terms)
